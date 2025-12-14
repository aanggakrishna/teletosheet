import logging
import colorlog
from datetime import datetime
import os

class BotLogger:
    def __init__(self, name="CryptoSignalBot", log_file="bot.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create formatters
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        file_handler = logging.FileHandler(f"logs/{log_file}", encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message, emoji="ℹ️"):
        self.logger.info(f"{emoji} {message}")
    
    def success(self, message, emoji="✅"):
        self.logger.info(f"{emoji} {message}")
    
    def warning(self, message, emoji="⚠️"):
        self.logger.warning(f"{emoji} {message}")
    
    def error(self, message, emoji="❌", exc_info=False):
        self.logger.error(f"{emoji} {message}", exc_info=exc_info)
    
    def debug(self, message, emoji="🔍"):
        self.logger.debug(f"{emoji} {message}")
    
    def heartbeat(self, message="Bot is alive"):
        self.logger.info(f"💓 {message}")
    
    def startup(self, message):
        self.logger.info(f"🚀 {message}")
    
    def signal_received(self, token_name, channel_name):
        self.logger.info(f"📥 New signal: {token_name} from {channel_name}")
    
    def alert_triggered(self, multiplier, token_name=""):
        self.logger.info(f"🚨 Alert triggered: {multiplier}x {token_name}")
    
    def tracking_update(self, token_name, interval, multiplier):
        self.logger.info(f"🔄 Updated {interval}min: {token_name} - {multiplier:.2f}x")
    
    def api_error(self, api_name, error):
        self.logger.error(f"🔌 {api_name} API error: {error}")
    
    def stopped_tracking(self, token_name):
        self.logger.info(f"⏹️ Stopped tracking: {token_name}")

# Create global logger instance
logger = BotLogger()