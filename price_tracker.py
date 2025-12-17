import requests
import asyncio
from datetime import datetime
from config import (DEXSCREENER_API_BASE, TRACKING_INTERVALS, ALERT_MULTIPLIERS,
                    SMART_POLLING_INTERVALS, HOT_GAIN_THRESHOLD, TRACKING_DURATION)
from logger import logger

class PriceTracker:
    def __init__(self, sheets_handler):
        self.sheets = sheets_handler
        self.last_heartbeat = datetime.now()
        self.signal_last_update = {}  # Track last update time per signal
    
    @staticmethod
    def clean_numeric_value(value):
        """Clean and convert numeric value from sheets (handles $, commas, etc)"""
        if value is None or value == '':
            return 0.0
        
        # If already a number, return it
        if isinstance(value, (int, float)):
            return float(value)
        
        # If string, clean it
        if isinstance(value, str):
            # Remove $, commas, spaces, and other non-numeric chars (except . and -)
            cleaned = value.replace('$', '').replace(',', '').replace(' ', '').strip()
            if cleaned == '' or cleaned == '-':
                return 0.0
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        
        return 0.0
    
    async def track_prices(self):
        """Main tracking loop with smart polling"""
        logger.info("🔄 Price tracking loop started with SMART POLLING")
        
        while True:
            try:
                active_signals = self.sheets.get_active_signals()
                
                if active_signals:
                    logger.debug(f"Processing {len(active_signals)} active signals...")
                    
                    for signal in active_signals:
                        await self.process_signal_smart(signal)
                        await asyncio.sleep(0.5)  # Small delay between signals
                else:
                    logger.debug("No active signals to track")
                
                # Heartbeat every 10 minutes in price tracker
                now = datetime.now()
                if (now - self.last_heartbeat).total_seconds() > 600:
                    logger.debug(f"Price tracker heartbeat - processed {len(active_signals)} signals")
                    self.last_heartbeat = now
                
                # Check every 10 seconds for new signals to update
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    def get_smart_interval(self, signal):
        """Calculate dynamic update interval based on signal age and performance"""
        try:
            timestamp_str = signal.get('timestamp_received', '')
            if not timestamp_str:
                return SMART_POLLING_INTERVALS['normal']
            
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            age_minutes = (datetime.now() - timestamp).total_seconds() / 60
            
            # Calculate current gain
            entry_mc = self.clean_numeric_value(signal.get('mc_entry', 0))
            current_mc = self.clean_numeric_value(signal.get('current_mc_live', entry_mc))
            
            if entry_mc > 0:
                gain_percent = ((current_mc - entry_mc) / entry_mc) * 100
            else:
                gain_percent = 0
            
            # Determine interval based on age and performance
            if age_minutes < 5:
                # Fresh signal (0-5 min): aggressive 30 seconds
                return SMART_POLLING_INTERVALS['fresh']
            elif age_minutes < 60 or gain_percent > HOT_GAIN_THRESHOLD:
                # Hot signal (<1 hour OR pumping >20%): every 1 minute
                return SMART_POLLING_INTERVALS['hot']
            elif age_minutes < 1440:  # < 24 hours
                # Normal signal: every 5 minutes
                return SMART_POLLING_INTERVALS['normal']
            elif age_minutes < 2880:  # < 2 days
                # Mature signal: every 15 minutes
                return SMART_POLLING_INTERVALS['mature']
            else:
                # Old signal (2-3 days): every 30 minutes
                return SMART_POLLING_INTERVALS['old']
        
        except Exception as e:
            logger.debug(f"Error calculating smart interval: {e}")
            return SMART_POLLING_INTERVALS['normal']
    
    async def process_signal_smart(self, signal):
        """Process signal with smart polling intervals"""
        try:
            row_index = signal['row_index']
            ca = signal.get('ca', '')
            token_name = signal.get('token_name', 'Unknown')
            
            if not ca:
                logger.warning(f"No CA found for signal: {token_name}")
                return
            
            # Check if tracking duration exceeded (3 days)
            timestamp_str = signal.get('timestamp_received', '')
            if not timestamp_str:
                logger.warning(f"No timestamp for signal: {token_name}")
                return
            
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            elapsed_minutes = (datetime.now() - timestamp).total_seconds() / 60
            
            if elapsed_minutes > TRACKING_DURATION:
                self.sheets.update_status(row_index, 'stopped')
                logger.stopped_tracking(token_name)
                return
            
            # Get dynamic interval
            update_interval = self.get_smart_interval(signal)
            
            # Check if enough time has passed since last update
            signal_key = f"{row_index}_{ca}"
            last_update = self.signal_last_update.get(signal_key)
            
            if last_update:
                seconds_since_update = (datetime.now() - last_update).total_seconds()
                if seconds_since_update < update_interval:
                    # Too soon to update
                    return
            
            # Time to update! Fetch fresh data
            await self.update_live_price(signal, row_index, ca)
            
            # Record this update time
            self.signal_last_update[signal_key] = datetime.now()
            
            # Also process traditional interval tracking
            await self.process_traditional_intervals(signal, row_index, ca, elapsed_minutes)
        
        except Exception as e:
            error_msg = f"Error processing signal {signal.get('token_name', 'Unknown')}: {e}"
            logger.error(error_msg, exc_info=True)
            
            row_index = signal.get('row_index')
            if row_index:
                self.sheets.update_error_log(row_index, str(e))
    
    async def update_live_price(self, signal, row_index, ca):
        """Update realtime live price data"""
        try:
            token_name = signal.get('token_name', 'Unknown')
            
            # Validate CA
            if not ca or len(ca) < 32:
                return
            
            # Fetch from DexScreener
            price_data = await self.fetch_dexscreener_price(ca)
            
            if not price_data:
                return
            
            current_price = price_data.get('price', 0)
            current_mc = price_data.get('market_cap', 0)
            
            # Calculate gain
            entry_mc = self.clean_numeric_value(signal.get('mc_entry', 0))
            if entry_mc > 0:
                gain_percent = ((current_mc - entry_mc) / entry_mc) * 100
                multiplier = current_mc / entry_mc
            else:
                gain_percent = 0
                multiplier = 0
            
            # Get current update count
            update_count = int(self.clean_numeric_value(signal.get('update_count', 0))) + 1
            
            # Update live columns
            self.sheets.update_live_data(row_index, current_price, current_mc, gain_percent, update_count)
            
            # Check pump milestones (50% and 100%)
            await self.check_pump_milestones(signal, row_index, gain_percent, token_name)
            
            # Update ATH tracking
            await self.update_ath_tracking(signal, row_index, current_price, current_mc, gain_percent, token_name)
            
            # Update peak if higher
            peak_mc = self.clean_numeric_value(signal.get('peak_mc', entry_mc))
            peak_mult = self.clean_numeric_value(signal.get('peak_multiplier', 1.0))
            alert_history_last = int(self.clean_numeric_value(signal.get('alert_history_last', 0)))
            alert_times = {}
            
            if current_mc > peak_mc:
                peak_mc = current_mc
                peak_mult = multiplier
                
                logger.info(f"🚀 New peak for {token_name}: {peak_mult:.2f}x (${current_mc:,.0f})")
                
                # Check for alert achievements
                for alert_mult in ALERT_MULTIPLIERS:
                    if multiplier >= alert_mult and alert_history_last < alert_mult:
                        alert_history_last = alert_mult
                        alert_times[alert_mult] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        logger.alert_triggered(f"{alert_mult}x", token_name)
                
                self.sheets.update_peak_and_alerts(
                    row_index, peak_mc, peak_mult, alert_history_last, alert_times
                )
            
            logger.debug(f"Live update #{update_count} for {token_name}: {multiplier:.2f}x ({gain_percent:+.1f}%)")
        
        except Exception as e:
            logger.debug(f"Error updating live price: {e}")
    
    async def check_pump_milestones(self, signal, row_index, gain_percent, token_name):
        """Check and record pump milestones (50% and 100% gains)"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pump_50_time = signal.get('pump_50_time', '')
            pump_100_time = signal.get('pump_100_time', '')
            
            # Check 50% milestone (1.5x = 50% gain)
            if gain_percent >= 50 and not pump_50_time:
                self.sheets.update_pump_milestones(row_index, pump_50_time=current_time)
                logger.info(f"🎯 {token_name} reached 50% pump milestone! (+{gain_percent:.1f}%)")
            
            # Check 100% milestone (2x = 100% gain)
            if gain_percent >= 100 and not pump_100_time:
                self.sheets.update_pump_milestones(row_index, pump_100_time=current_time)
                logger.info(f"🚀🚀 {token_name} reached 100% pump milestone! (+{gain_percent:.1f}%)")
        
        except Exception as e:
            logger.debug(f"Error checking pump milestones: {e}")
    
    async def update_ath_tracking(self, signal, row_index, current_price, current_mc, current_gain_percent, token_name):
        """Update All Time High tracking"""
        try:
            entry_mc = self.clean_numeric_value(signal.get('mc_entry', 0))
            ath_mc = self.clean_numeric_value(signal.get('ath_mc', entry_mc))
            
            # Check if current MC is new ATH
            if current_mc > ath_mc:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Calculate ATH gain from entry
                if entry_mc > 0:
                    ath_gain_percent = ((current_mc - entry_mc) / entry_mc) * 100
                else:
                    ath_gain_percent = 0
                
                # Update ATH data
                self.sheets.update_ath(row_index, current_price, current_mc, ath_gain_percent, current_time)
                
                logger.info(f"📈 New ATH for {token_name}: ${current_mc:,.0f} MC (+{ath_gain_percent:.1f}%)")
        
        except Exception as e:
            logger.debug(f"Error updating ATH: {e}")
    
    async def process_traditional_intervals(self, signal, row_index, ca, elapsed_minutes):
        """Process traditional 5/10/15/30/60 min interval tracking"""
        try:
            token_name = signal.get('token_name', 'Unknown')
            
            # Check which intervals need updating
            for interval in TRACKING_INTERVALS:
                if elapsed_minutes >= interval:
                    # Check if this interval is already filled
                    existing_price = signal.get(f'price_{interval}min', '')
                    if existing_price == '' or existing_price is None:
                        # Fetch and update
                        await self.update_interval(signal, row_index, ca, interval)
        
        except Exception as e:
            logger.debug(f"Error processing traditional intervals: {e}")
    
    async def process_signal(self, signal):
        """Process individual signal tracking"""
        try:
            row_index = signal['row_index']
            ca = signal.get('ca', '')
            token_name = signal.get('token_name', 'Unknown')
            
            if not ca:
                logger.warning(f"No CA found for signal: {token_name}")
                return
            
            # Calculate elapsed time
            timestamp_str = signal.get('timestamp_received', '')
            if not timestamp_str:
                logger.warning(f"No timestamp for signal: {token_name}")
                return
            
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            elapsed_minutes = (datetime.now() - timestamp).total_seconds() / 60
            
            # Check if we need to stop tracking (after 60 minutes)
            if elapsed_minutes > 60:
                self.sheets.update_status(row_index, 'stopped')
                logger.stopped_tracking(token_name)
                return
            
            # Check which intervals need updating
            for interval in TRACKING_INTERVALS:
                if elapsed_minutes >= interval:
                    # Check if this interval is already filled
                    existing_price = signal.get(f'price_{interval}min', '')
                    if existing_price == '' or existing_price is None:
                        # Fetch and update
                        await self.update_interval(signal, row_index, ca, interval)
        
        except Exception as e:
            error_msg = f"Error processing signal {signal.get('token_name', 'Unknown')}: {e}"
            logger.error(error_msg, exc_info=True)
            
            row_index = signal.get('row_index')
            if row_index:
                self.sheets.update_error_log(row_index, str(e))
    
    async def update_interval(self, signal, row_index, ca, interval):
        """Fetch price and update specific interval"""
        token_name = signal.get('token_name', 'Unknown')
        
        try:
            # Validate CA first
            if not ca or len(ca) < 32:
                error_msg = f"Invalid CA for {token_name}, stopping tracking"
                logger.warning(error_msg)
                self.sheets.update_status(row_index, 'invalid_ca')
                self.sheets.update_error_log(row_index, error_msg)
                return
            
            # Fetch from DexScreener
            price_data = await self.fetch_dexscreener_price(ca)
            
            if not price_data:
                # Check if this is the first attempt (5min interval)
                if interval == 5:
                    error_msg = f"No trading data available on DexScreener - CA: {ca}"
                    logger.warning(f"⚠️ {token_name}: No price data available (might be unlisted/no liquidity)")
                    self.sheets.update_status(row_index, 'no_pairs')
                    self.sheets.update_error_log(row_index, error_msg)
                # For subsequent intervals, just skip silently (already logged in 5min)
                return
            
            current_price = price_data.get('price', 0)
            current_mc = price_data.get('market_cap', 0)
            
            # Calculate change - use clean_numeric_value for sheet data
            entry_mc = self.clean_numeric_value(signal.get('mc_entry', 0))
            if entry_mc > 0:
                change_percent = ((current_mc - entry_mc) / entry_mc) * 100
                multiplier = current_mc / entry_mc
            else:
                change_percent = 0
                multiplier = 0
            
            # Update tracking columns
            self.sheets.update_tracking_data(
                row_index, interval, current_price, current_mc, f"{change_percent:.2f}%"
            )
            
            # Update peak if higher - use clean_numeric_value for sheet data
            peak_mc = self.clean_numeric_value(signal.get('peak_mc', entry_mc))
            peak_mult = self.clean_numeric_value(signal.get('peak_multiplier', 1.0))
            alert_history_last = int(self.clean_numeric_value(signal.get('alert_history_last', 0)))
            alert_times = {}
            
            if current_mc > peak_mc:
                peak_mc = current_mc
                peak_mult = multiplier
                
                logger.info(f"🚀 New peak for {token_name}: {peak_mult:.2f}x (${current_mc:,.0f})")
                
                # Check for alert achievements
                for alert_mult in ALERT_MULTIPLIERS:
                    if multiplier >= alert_mult and alert_history_last < alert_mult:
                        alert_history_last = alert_mult
                        alert_times[alert_mult] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        logger.alert_triggered(f"{alert_mult}x", token_name)
                
                self.sheets.update_peak_and_alerts(
                    row_index, peak_mc, peak_mult, alert_history_last, alert_times
                )
            
            logger.tracking_update(token_name, interval, multiplier)
            
        except Exception as e:
            error_msg = f"Error updating {interval}min interval for {token_name}: {e}"
            logger.error(error_msg, exc_info=True)
            self.sheets.update_error_log(row_index, str(e))
    
    async def fetch_dexscreener_price(self, ca):
        """Fetch price from DexScreener API"""
        try:
            # Validate CA before making request
            if not ca or len(ca) < 32:
                logger.warning(f"Invalid CA format: {ca}")
                return None
            
            # DexScreener API: /tokens/{address} - will auto-detect chain
            url = f"{DEXSCREENER_API_BASE}/tokens/{ca}"
            logger.debug(f"Fetching from DexScreener: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                # Token not found - endpoint doesn't recognize the address
                logger.debug(f"DexScreener 404 for CA: {ca[:8]}...")
                return None
            elif response.status_code != 200:
                logger.api_error("DexScreener", f"HTTP {response.status_code} for CA: {ca[:8]}...")
                return None
            
            data = response.json()
            
            # Check if we got pairs data
            if not data.get('pairs') or len(data['pairs']) == 0:
                # API returned OK but no trading pairs exist
                logger.debug(f"No trading pairs found for CA: {ca[:8]}... (token exists but not listed/traded)")
                return None
            
            # Get the first pair (usually the most liquid)
            pair = data['pairs'][0]
            
            result = {
                'price': float(pair.get('priceUsd', 0)),
                'market_cap': float(pair.get('fdv', 0)),  # Fully Diluted Valuation
                'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                'volume_24h': float(pair.get('volume', {}).get('h24', 0))
            }
            
            logger.debug(f"DexScreener data fetched for {ca[:8]}...: ${result['market_cap']:,.0f} MC")
            return result
        
        except requests.RequestException as e:
            logger.debug(f"DexScreener request failed: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"DexScreener data parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"DexScreener unexpected error: {e}", exc_info=True)
            return None

