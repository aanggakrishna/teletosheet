import asyncio
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, CHANNEL_IDS
from signal_parser import parse_new_signal, parse_alert_update, is_signal_message, is_alert_message
from sheets_handler import SheetsHandler
from price_tracker import PriceTracker

# Initialize handlers
sheets_handler = SheetsHandler()
price_tracker = PriceTracker(sheets_handler)

# Initialize Telethon client
client = TelegramClient('crypto_signal_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_IDS))
async def handle_new_message(event):
    """Handle incoming messages from tracked channels"""
    try:
        message_text = event.message.message
        channel_id = event.chat_id
        
        # Get channel name
        chat = await event.get_chat()
        channel_name = chat.title if hasattr(chat, 'title') else str(channel_id)
        
        # Check if it's a new signal
        if is_signal_message(message_text):
            signal_data = parse_new_signal(message_text, channel_id, channel_name)
            if signal_data:
                sheets_handler.append_signal(signal_data)
                print(f"📥 New signal received from {channel_name}")
        
        # Check if it's an alert update
        elif is_alert_message(message_text):
            alert_data = parse_alert_update(message_text)
            if alert_data and alert_data.get('ca'):
                sheets_handler.update_alert_from_message(alert_data['ca'], alert_data)
                print(f"🚨 Alert update: {alert_data.get('multiplier')}x")
    
    except Exception as e:
        print(f"❌ Error handling message: {e}")

async def main():
    """Main entry point"""
    print("🚀 Starting Crypto Signal Tracker...")
    
    # Start Telegram client
    await client.start(phone=TELEGRAM_PHONE)
    print("✅ Telegram client connected")
    
    # Start price tracking loop
    asyncio.create_task(price_tracker.track_prices())
    print("✅ Price tracker started")
    
    print("📡 Listening to channels...")
    print(f"📊 Monitoring {len(CHANNEL_IDS)} channels")
    
    # Keep running
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
