import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON
from logger import logger

class SheetsHandler:
    def __init__(self):
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_SERVICE_ACCOUNT_JSON, scope)
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(GOOGLE_SHEET_ID).sheet1
            self._ensure_headers()
            logger.success("Google Sheets connection established")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets: {e}", exc_info=True)
            raise
    
    def _ensure_headers(self):
        """Ensure spreadsheet has correct headers"""
        try:
            headers = [
                'nomor', 'timestamp_received', 'channel_id', 'channel_name', 'message_id',
                'ca', 'token_name', 'chain', 'price_entry', 'mc_entry', 'liquidity', 
                'volume_24h', 'bundles_percent', 'snipers_percent', 'dev_percent', 
                'confidence_score', 'price_5min', 'mc_5min', 'change_5min', 
                'price_10min', 'mc_10min', 'change_10min', 'price_15min', 'mc_15min', 
                'change_15min', 'price_30min', 'mc_30min', 'change_30min', 
                'price_60min', 'mc_60min', 'change_60min', 'peak_mc', 'peak_multiplier', 
                'current_status', 'alert_2x_time', 'alert_3x_time', 'alert_5x_time', 
                'alert_10x_time', 'alert_history_last', 'update_history', 'error_log', 
                'link_dexscreener', 'link_pump'
            ]
            
            existing_headers = self.sheet.row_values(1)
            if not existing_headers or existing_headers != headers:
                self.sheet.insert_row(headers, 1)
                logger.info("📊 Headers updated in spreadsheet")
        except Exception as e:
            logger.error(f"Error ensuring headers: {e}", exc_info=True)
    
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
                data.get('message_id', ''),
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
                data.get('update_history', ''),
                data.get('error_log', ''),
                data.get('link_dexscreener', ''),
                data.get('link_pump', '')
            ]
            
            self.sheet.append_row(row)
            logger.success(f"Signal saved to sheet: {data.get('token_name')} ({data.get('ca', '')[:8]}...)")
            return next_number
            
        except Exception as e:
            logger.error(f"Error appending signal to sheet: {e}", exc_info=True)
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
            logger.error(f"Error getting active signals: {e}", exc_info=True)
            return []
    
    def update_tracking_data(self, row_index, interval, price, mc, change):
        """Update tracking columns for specific interval"""
        try:
            # Column mapping (adjusted after adding message_id column - all shifted by 1)
            col_mapping = {
                5: {'price': 'Q', 'mc': 'R', 'change': 'S'},
                10: {'price': 'T', 'mc': 'U', 'change': 'V'},
                15: {'price': 'W', 'mc': 'X', 'change': 'Y'},
                30: {'price': 'Z', 'mc': 'AA', 'change': 'AB'},
                60: {'price': 'AC', 'mc': 'AD', 'change': 'AE'}
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
            logger.debug(f"Updated {interval}min data for row {row_index}")
            
        except Exception as e:
            logger.error(f"Error updating tracking data: {e}", exc_info=True)
    
    def update_peak_and_alerts(self, row_index, peak_mc, peak_mult, alert_history_last, alert_times):
        """Update peak MC, multiplier, and alert data"""
        try:
            updates = [
                {'range': f"AF{row_index}", 'values': [[peak_mc]]},  # peak_mc (shifted)
                {'range': f"AG{row_index}", 'values': [[peak_mult]]},  # peak_multiplier (shifted)
                {'range': f"AM{row_index}", 'values': [[alert_history_last]]}  # alert_history_last (shifted)
            ]
            
            # Update alert timestamp columns (all shifted by 1)
            alert_col_mapping = {2: 'AI', 3: 'AJ', 5: 'AK', 10: 'AL'}
            for mult, timestamp in alert_times.items():
                if mult in alert_col_mapping and timestamp:
                    updates.append({
                        'range': f"{alert_col_mapping[mult]}{row_index}",
                        'values': [[timestamp]]
                    })
            
            self.sheet.batch_update(updates)
            logger.debug(f"Updated peak/alerts for row {row_index}")
            
        except Exception as e:
            logger.error(f"Error updating peak/alerts: {e}", exc_info=True)
    
    def update_status(self, row_index, status):
        """Update signal status"""
        try:
            self.sheet.update(f"AH{row_index}", [[status]])  # current_status column (shifted)
            logger.debug(f"Status updated to '{status}' for row {row_index}")
        except Exception as e:
            logger.error(f"Error updating status: {e}", exc_info=True)
    
    def update_error_log(self, row_index, error_msg):
        """Update error log column"""
        try:
            # Truncate error message if too long
            truncated_error = error_msg[:500] + "..." if len(error_msg) > 500 else error_msg
            self.sheet.update(f"AO{row_index}", [[truncated_error]])  # error_log column (shifted +2)
            logger.debug(f"Error logged for row {row_index}: {error_msg[:50]}...")
        except Exception as e:
            logger.error(f"Error updating error log: {e}")
    
    def find_row_by_ca(self, ca):
        """Find row index by contract address"""
        try:
            ca_column = self.sheet.col_values(6)  # Column F (ca) - shifted from E to F
            if ca in ca_column:
                row_index = ca_column.index(ca) + 1
                logger.debug(f"Found CA {ca} at row {row_index}")
                return row_index
            logger.warning(f"CA {ca} not found in sheet")
            return None
        except Exception as e:
            logger.error(f"Error finding row by CA: {e}", exc_info=True)
            return None
    
    def update_alert_from_message(self, reply_to_message_id, alert_data):
        """Update row when alert message is received (using reply_to_message_id)"""
        try:
            # Find row by message_id (column E)
            row_index = self.find_row_by_message_id(reply_to_message_id)
            if not row_index:
                # Fallback: try to find by CA
                ca = alert_data.get('ca', '')
                if ca:
                    row_index = self.find_row_by_ca(ca)
                
                if not row_index:
                    logger.warning(f"Cannot update alert - message_id {reply_to_message_id} not found")
                    return
            
            multiplier = alert_data.get('multiplier', 0)
            peak = alert_data.get('peak', multiplier)
            alert_time = alert_data.get('alert_time', '')
            time_elapsed = alert_data.get('time_elapsed', '')
            gain = alert_data.get('gain', multiplier)
            current_mc = alert_data.get('current_mc', 0)
            
            # Update peak if higher
            current_peak = self.sheet.cell(row_index, 33).value  # peak_multiplier column (shifted by 1)
            current_peak = float(current_peak) if current_peak else 1.0
            
            if peak > current_peak:
                self.sheet.update(f"AG{row_index}", [[peak]])  # peak_multiplier (shifted)
                logger.info(f"📈 Peak updated to {peak}x for message_id {reply_to_message_id}")
                
                if current_mc:
                    self.sheet.update(f"AF{row_index}", [[current_mc]])  # peak_mc (shifted)
            
            # Update alert_history_last
            self.sheet.update(f"AM{row_index}", [[multiplier]])
            
            # Update specific alert timestamp
            alert_col_mapping = {2: 'AI', 3: 'AJ', 5: 'AK', 10: 'AL'}  # Shifted columns
            if multiplier in alert_col_mapping:
                self.sheet.update(f"{alert_col_mapping[multiplier]}{row_index}", [[alert_time]])
            
            # Update update_history column with new alert info
            update_msg = f"{alert_time} | {multiplier}x alert | Gain: {gain}x | MC: ${current_mc:,.0f} | Time: {time_elapsed}"
            self.append_update_history(row_index, update_msg)
            
            logger.success(f"Alert updated: {multiplier}x for message_id {reply_to_message_id}")
            
        except Exception as e:
            logger.error(f"Error updating alert from message: {e}", exc_info=True)
    
    def find_row_by_message_id(self, message_id):
        """Find row index by message_id"""
        try:
            message_id_column = self.sheet.col_values(5)  # Column E (message_id)
            message_id_str = str(message_id)
            if message_id_str in message_id_column:
                row_index = message_id_column.index(message_id_str) + 1
                logger.debug(f"Found message_id {message_id} at row {row_index}")
                return row_index
            logger.debug(f"message_id {message_id} not found in sheet")
            return None
        except Exception as e:
            logger.error(f"Error finding row by message_id: {e}", exc_info=True)
            return None
    
    def append_update_history(self, row_index, update_msg):
        """Append update to update_history column"""
        try:
            # Get existing history
            existing_history = self.sheet.cell(row_index, 39).value  # Column AN (update_history, shifted)
            
            if existing_history:
                new_history = f"{existing_history}\n{update_msg}"
            else:
                new_history = update_msg
            
            # Update the cell
            self.sheet.update(f"AN{row_index}", [[new_history]])
            logger.debug(f"Update history appended for row {row_index}")
            
        except Exception as e:
            logger.error(f"Error appending update history: {e}", exc_info=True)
