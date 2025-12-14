import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON

class SheetsHandler:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_SERVICE_ACCOUNT_JSON, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(GOOGLE_SHEET_ID).sheet1
        self._ensure_headers()
    
    def _ensure_headers(self):
        """Ensure spreadsheet has correct headers"""
        headers = [
            'nomor', 'timestamp_received', 'channel_id', 'channel_name', 'ca', 
            'token_name', 'chain', 'price_entry', 'mc_entry', 'liquidity', 
            'volume_24h', 'bundles_percent', 'snipers_percent', 'dev_percent', 
            'confidence_score', 'price_5min', 'mc_5min', 'change_5min', 
            'price_10min', 'mc_10min', 'change_10min', 'price_15min', 'mc_15min', 
            'change_15min', 'price_30min', 'mc_30min', 'change_30min', 
            'price_60min', 'mc_60min', 'change_60min', 'peak_mc', 'peak_multiplier', 
            'current_status', 'alert_2x_time', 'alert_3x_time', 'alert_5x_time', 
            'alert_10x_time', 'alert_history_last', 'error_log', 
            'link_dexscreener', 'link_pump'
        ]
        
        existing_headers = self.sheet.row_values(1)
        if not existing_headers or existing_headers != headers:
            self.sheet.insert_row(headers, 1)
    
    def append_signal(self, data):
        """Append new signal to sheet"""
        try:
            all_values = self.sheet.get_all_values()
            next_number = len(all_values)  # Header is row 1, so this gives correct number
            
            row = [
                next_number,
                data.get('timestamp_received', ''),
                data.get('channel_id', ''),
                data.get('channel_name', ''),
                data.get('ca', ''),
                data.get('token_name', ''),
                data.get('chain', ''),
                data.get('price_entry', ''),
                data.get('mc_entry', ''),
                data.get('liquidity', ''),
                data.get('volume_24h', ''),
                data.get('bundles_percent', ''),
                data.get('snipers_percent', ''),
                data.get('dev_percent', ''),
                data.get('confidence_score', ''),
                data.get('price_5min', ''),
                data.get('mc_5min', ''),
                data.get('change_5min', ''),
                data.get('price_10min', ''),
                data.get('mc_10min', ''),
                data.get('change_10min', ''),
                data.get('price_15min', ''),
                data.get('mc_15min', ''),
                data.get('change_15min', ''),
                data.get('price_30min', ''),
                data.get('mc_30min', ''),
                data.get('change_30min', ''),
                data.get('price_60min', ''),
                data.get('mc_60min', ''),
                data.get('change_60min', ''),
                data.get('peak_mc', ''),
                data.get('peak_multiplier', ''),
                data.get('current_status', ''),
                data.get('alert_2x_time', ''),
                data.get('alert_3x_time', ''),
                data.get('alert_5x_time', ''),
                data.get('alert_10x_time', ''),
                data.get('alert_history_last', ''),
                data.get('error_log', ''),
                data.get('link_dexscreener', ''),
                data.get('link_pump', '')
            ]
            
            self.sheet.append_row(row)
            print(f"✅ Signal appended: {data.get('token_name')} - {data.get('ca')}")
            return next_number
        except Exception as e:
            print(f"❌ Error appending signal: {e}")
            return None
    
    def get_active_signals(self):
        """Get all active signals for tracking"""
        try:
            all_records = self.sheet.get_all_records()
            active_signals = []
            
            for idx, record in enumerate(all_records, start=2):  # Start at 2 (skip header)
                if record.get('current_status') == 'active':
                    record['row_index'] = idx
                    active_signals.append(record)
            
            return active_signals
        except Exception as e:
            print(f"❌ Error getting active signals: {e}")
            return []
    
    def update_tracking_data(self, row_index, interval, price, mc, change):
        """Update tracking columns for specific interval"""
        try:
            # Column mapping (adjust based on header order)
            col_mapping = {
                5: {'price': 'P', 'mc': 'Q', 'change': 'R'},
                10: {'price': 'S', 'mc': 'T', 'change': 'U'},
                15: {'price': 'V', 'mc': 'W', 'change': 'X'},
                30: {'price': 'Y', 'mc': 'Z', 'change': 'AA'},
                60: {'price': 'AB', 'mc': 'AC', 'change': 'AD'}
            }
            
            cols = col_mapping.get(interval)
            if not cols:
                return
            
            updates = [
                {'range': f"{cols['price']}{row_index}", 'values': [[price]]},
                {'range': f"{cols['mc']}{row_index}", 'values': [[mc]]},
                {'range': f"{cols['change']}{row_index}", 'values': [[change]]}
            ]
            
            self.sheet.batch_update(updates)
        except Exception as e:
            print(f"❌ Error updating tracking data: {e}")
    
    def update_peak_and_alerts(self, row_index, peak_mc, peak_mult, alert_history_last, alert_times):
        """Update peak MC, multiplier, and alert data"""
        try:
            updates = [
                {'range': f"AE{row_index}", 'values': [[peak_mc]]},  # peak_mc
                {'range': f"AF{row_index}", 'values': [[peak_mult]]},  # peak_multiplier
                {'range': f"AL{row_index}", 'values': [[alert_history_last]]}  # alert_history_last
            ]
            
            # Update alert timestamp columns
            alert_col_mapping = {2: 'AH', 3: 'AI', 5: 'AJ', 10: 'AK'}
            for mult, timestamp in alert_times.items():
                if mult in alert_col_mapping and timestamp:
                    updates.append({
                        'range': f"{alert_col_mapping[mult]}{row_index}",
                        'values': [[timestamp]]
                    })
            
            self.sheet.batch_update(updates)
        except Exception as e:
            print(f"❌ Error updating peak/alerts: {e}")
    
    def update_status(self, row_index, status):
        """Update signal status"""
        try:
            self.sheet.update(f"AG{row_index}", [[status]])  # current_status column
        except Exception as e:
            print(f"❌ Error updating status: {e}")
    
    def update_error_log(self, row_index, error_msg):
        """Update error log column"""
        try:
            self.sheet.update(f"AM{row_index}", [[error_msg]])  # error_log column
        except Exception as e:
            print(f"❌ Error updating error log: {e}")
    
    def find_row_by_ca(self, ca):
        """Find row index by contract address"""
        try:
            ca_column = self.sheet.col_values(5)  # Column E (ca)
            if ca in ca_column:
                return ca_column.index(ca) + 1
            return None
        except Exception as e:
            print(f"❌ Error finding row by CA: {e}")
            return None
    
    def update_alert_from_message(self, ca, alert_data):
        """Update row when alert message is received"""
        try:
            row_index = self.find_row_by_ca(ca)
            if not row_index:
                return
            
            multiplier = alert_data.get('multiplier', 0)
            peak = alert_data.get('peak', multiplier)
            alert_time = alert_data.get('alert_time', '')
            
            # Update peak if higher
            current_peak = self.sheet.cell(row_index, 32).value  # peak_multiplier column
            current_peak = float(current_peak) if current_peak else 1.0
            
            if peak > current_peak:
                self.sheet.update(f"AF{row_index}", [[peak]])  # peak_multiplier
                
                if alert_data.get('current_mc'):
                    self.sheet.update(f"AE{row_index}", [[alert_data['current_mc']]])  # peak_mc
            
            # Update alert_history_last
            self.sheet.update(f"AL{row_index}", [[multiplier]])
            
            # Update specific alert timestamp
            alert_col_mapping = {2: 'AH', 3: 'AI', 5: 'AJ', 10: 'AK'}
            if multiplier in alert_col_mapping:
                self.sheet.update(f"{alert_col_mapping[multiplier]}{row_index}", [[alert_time]])
            
            print(f"✅ Alert updated: {multiplier}x for CA {ca}")
        except Exception as e:
            print(f"❌ Error updating alert from message: {e}")
