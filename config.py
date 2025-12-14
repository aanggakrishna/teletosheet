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
