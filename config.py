import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Config
TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
CHANNEL_IDS = [int(x.strip()) for x in os.getenv('CHANNEL_IDS').split(',')]

# Google Sheets Config
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')

# DexScreener API
DEXSCREENER_API_BASE = "https://api.dexscreener.com/latest/dex"

# Tracking intervals in minutes
TRACKING_INTERVALS = [5, 10, 15, 30, 60]

# Alert multipliers
ALERT_MULTIPLIERS = [2, 3, 5, 10]

# Logging and Monitoring Config
HEARTBEAT_INTERVAL = 300  # 5 minutes
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENABLE_DEBUG_LOGS = os.getenv('ENABLE_DEBUG_LOGS', 'False').lower() == 'true'

# Bot Settings
MAX_ERROR_LOG_LENGTH = 500
API_TIMEOUT = 10
TRACKING_DURATION = 4320  # minutes (3 days)

# Smart Polling Settings (Realtime-like updates)
# Age-based intervals for dynamic polling
SMART_POLLING_INTERVALS = {
    'fresh': 30,      # 0-5 min: every 30 seconds
    'hot': 60,        # 5-60 min OR gain >20%: every 1 minute
    'normal': 300,    # 1-24 hours: every 5 minutes
    'mature': 900,    # 1-2 days: every 15 minutes
    'old': 1800       # 2-3 days: every 30 minutes
}

# Thresholds for "hot" token detection
HOT_GAIN_THRESHOLD = 20  # percent gain to be considered "hot"

# Channel Format Mapping (from .env)
# Format: CHANNEL_FORMATS=channel_id1:format1,channel_id2:format2
# Example: CHANNEL_FORMATS=-1002031885122:ca_only,-1002026135487:narrative_ca
def parse_channel_formats():
    """Parse channel format mapping from environment variable"""
    formats_str = os.getenv('CHANNEL_FORMATS', '')
    channel_formats = {}
    
    if formats_str:
        try:
            # Split by comma to get each channel:format pair
            pairs = formats_str.split(',')
            for pair in pairs:
                pair = pair.strip()
                if ':' in pair:
                    channel_id_str, format_name = pair.split(':', 1)
                    channel_id = int(channel_id_str.strip())
                    format_name = format_name.strip()
                    channel_formats[channel_id] = format_name
        except Exception as e:
            print(f"⚠️ Error parsing CHANNEL_FORMATS: {e}")
            print(f"   Format should be: channel_id1:format1,channel_id2:format2")
    
    return channel_formats

CHANNEL_FORMAT_MAPPING = parse_channel_formats()

# Default format if channel not in mapping
DEFAULT_CHANNEL_FORMAT = os.getenv('DEFAULT_CHANNEL_FORMAT', 'standard')
