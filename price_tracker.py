import requests
import asyncio
from datetime import datetime
from config import DEXSCREENER_API_BASE, TRACKING_INTERVALS, ALERT_MULTIPLIERS
from logger import logger

class PriceTracker:
    def __init__(self, sheets_handler):
        self.sheets = sheets_handler
        self.last_heartbeat = datetime.now()
    
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
        """Main tracking loop"""
        logger.info("🔄 Price tracking loop started")
        
        while True:
            try:
                active_signals = self.sheets.get_active_signals()
                
                if active_signals:
                    logger.debug(f"Processing {len(active_signals)} active signals...")
                    
                    for signal in active_signals:
                        await self.process_signal(signal)
                        await asyncio.sleep(1)  # Small delay between signals
                else:
                    logger.debug("No active signals to track")
                
                # Heartbeat every 10 minutes in price tracker
                now = datetime.now()
                if (now - self.last_heartbeat).total_seconds() > 600:
                    logger.debug(f"Price tracker heartbeat - processed {len(active_signals)} signals")
                    self.last_heartbeat = now
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
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

