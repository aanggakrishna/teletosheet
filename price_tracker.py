import requests
import asyncio
from datetime import datetime
from config import DEXSCREENER_API_BASE, TRACKING_INTERVALS, ALERT_MULTIPLIERS

class PriceTracker:
    def __init__(self, sheets_handler):
        self.sheets = sheets_handler
    
    async def track_prices(self):
        """Main tracking loop"""
        while True:
            try:
                active_signals = self.sheets.get_active_signals()
                print(f"🔄 Tracking {len(active_signals)} active signals...")
                
                for signal in active_signals:
                    await self.process_signal(signal)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Error in tracking loop: {e}")
                await asyncio.sleep(60)
    
    async def process_signal(self, signal):
        """Process individual signal tracking"""
        try:
            row_index = signal['row_index']
            ca = signal.get('ca', '')
            
            if not ca:
                return
            
            # Calculate elapsed time
            timestamp_str = signal.get('timestamp_received', '')
            if not timestamp_str:
                return
            
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            elapsed_minutes = (datetime.now() - timestamp).total_seconds() / 60
            
            # Check if we need to stop tracking (after 60 minutes)
            if elapsed_minutes > 60:
                self.sheets.update_status(row_index, 'stopped')
                print(f"⏹️ Stopped tracking: {signal.get('token_name')}")
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
            print(f"❌ Error processing signal: {e}")
            self.sheets.update_error_log(signal.get('row_index'), str(e))
    
    async def update_interval(self, signal, row_index, ca, interval):
        """Fetch price and update specific interval"""
        try:
            # Fetch from DexScreener
            price_data = await self.fetch_dexscreener_price(ca)
            
            if not price_data:
                error_msg = f"Failed to fetch price at {interval}min"
                self.sheets.update_error_log(row_index, error_msg)
                return
            
            current_price = price_data.get('price', 0)
            current_mc = price_data.get('market_cap', 0)
            
            # Calculate change
            entry_mc = float(signal.get('mc_entry', 0))
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
            
            # Update peak if higher
            peak_mc = float(signal.get('peak_mc', entry_mc))
            peak_mult = float(signal.get('peak_multiplier', 1.0))
            alert_history_last = int(signal.get('alert_history_last', 0))
            alert_times = {}
            
            if current_mc > peak_mc:
                peak_mc = current_mc
                peak_mult = multiplier
                
                # Check for alert achievements
                for alert_mult in ALERT_MULTIPLIERS:
                    if multiplier >= alert_mult and alert_history_last < alert_mult:
                        alert_history_last = alert_mult
                        alert_times[alert_mult] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                self.sheets.update_peak_and_alerts(
                    row_index, peak_mc, peak_mult, alert_history_last, alert_times
                )
            
            print(f"✅ Updated {interval}min: {signal.get('token_name')} - {multiplier:.2f}x")
            
        except Exception as e:
            print(f"❌ Error updating interval {interval}min: {e}")
            self.sheets.update_error_log(row_index, str(e))
    
    async def fetch_dexscreener_price(self, ca):
        """Fetch price from DexScreener API"""
        try:
            url = f"{DEXSCREENER_API_BASE}/tokens/solana/{ca}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('pairs'):
                return None
            
            # Get the first pair (usually the most liquid)
            pair = data['pairs'][0]
            
            return {
                'price': float(pair.get('priceUsd', 0)),
                'market_cap': float(pair.get('fdv', 0)),  # Fully Diluted Valuation
                'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                'volume_24h': float(pair.get('volume', {}).get('h24', 0))
            }
        
        except Exception as e:
            print(f"❌ DexScreener API error: {e}")
            return None
