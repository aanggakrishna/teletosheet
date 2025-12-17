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
