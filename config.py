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
PRICE_CHECK_INTERVAL = 60  # seconds
TRACKING_DURATION = 60  # minutes
