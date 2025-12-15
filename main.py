import asyncio
from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, CHANNEL_IDS
from signal_parser import parse_new_signal, parse_alert_update, is_signal_message, is_alert_message
from sheets_handler import SheetsHandler
from price_tracker import PriceTracker
from logger import logger

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
        message_id = event.message.id
        reply_to_message_id = event.message.reply_to_msg_id
        
        # Get channel name
        chat = await event.get_chat()
        channel_name = chat.title if hasattr(chat, 'title') else str(channel_id)
        
        logger.debug(f"Message received from {channel_name}: {message_text[:100]}...")
        logger.debug(f"Message ID: {message_id}, Reply to: {reply_to_message_id}")
        
        # Check if it's an alert update (and it's a reply)
        if is_alert_message(message_text):
            alert_data = parse_alert_update(message_text)
            if alert_data:
                if reply_to_message_id:
                    # Update existing signal row using reply_to_message_id
                    sheets_handler.update_alert_from_message(reply_to_message_id, alert_data)
                    logger.alert_triggered(f"{alert_data.get('multiplier')}x", alert_data.get('token_name', 'Unknown'))
                elif alert_data.get('ca'):
                    # Fallback: use CA if no reply
                    sheets_handler.update_alert_from_message(None, alert_data)
                    logger.alert_triggered(f"{alert_data.get('multiplier')}x", alert_data.get('ca', '')[:8])
                else:
                    logger.warning(f"Alert message without reply_to or CA from {channel_name}")
            else:
                logger.warning(f"Failed to parse alert from {channel_name}")
        
        # Check if it's a new signal
        elif is_signal_message(message_text):
            signal_data = parse_new_signal(message_text, channel_id, channel_name, message_id)
            if signal_data:
                sheets_handler.append_signal(signal_data)
                logger.signal_received(signal_data.get('token_name', 'Unknown'), channel_name)
            else:
                logger.warning(f"Failed to parse signal from {channel_name}")
    
    except Exception as e:
        logger.error(f"Error handling message from {channel_name if 'channel_name' in locals() else 'Unknown'}: {e}", exc_info=True)

async def heartbeat_loop():
    """Send periodic heartbeat to show bot is alive"""
    heartbeat_counter = 0
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            heartbeat_counter += 1
            
            # Get some stats
            active_signals = sheets_handler.get_active_signals()
            active_count = len(active_signals)
            
            logger.heartbeat(f"Heartbeat #{heartbeat_counter} - Monitoring {len(CHANNEL_IDS)} channels, tracking {active_count} signals")
            
            # Every hour (12 heartbeats), show more detailed status
            if heartbeat_counter % 12 == 0:
                logger.info(f"📊 Hourly Status Report:")
                logger.info(f"   • Active signals: {active_count}")
                logger.info(f"   • Monitored channels: {len(CHANNEL_IDS)}")
                logger.info(f"   • Bot uptime: {heartbeat_counter * 5} minutes")
                
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}", exc_info=True)
            await asyncio.sleep(60)

async def main():
    """Main entry point"""
    logger.startup("Starting Crypto Signal Tracker...")
    
    try:
        # Start Telegram client
        await client.start(phone=TELEGRAM_PHONE)
        logger.success("Telegram client connected")
        
        # Start price tracking loop
        asyncio.create_task(price_tracker.track_prices())
        logger.success("Price tracker started")
        
        # Start heartbeat loop
        asyncio.create_task(heartbeat_loop())
        logger.success("Heartbeat monitor started")
        
        logger.info(f"� Listening to {len(CHANNEL_IDS)} channels...")
        logger.info("🤖 Bot is now fully operational!")
        
        # Keep running
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error in main: {e}", exc_info=True)
    finally:
        logger.info("👋 Bot shutting down...")

if __name__ == '__main__':
    asyncio.run(main())
