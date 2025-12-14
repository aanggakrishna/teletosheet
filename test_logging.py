#!/usr/bin/env python3
"""
Test script untuk logging system
Gunakan ini untuk test logging tanpa menjalankan bot utama
"""

import sys
import time
import asyncio
from logger import logger

async def test_logging():
    """Test semua fungsi logging"""
    
    print("=" * 60)
    print("🧪 TESTING LOGGING SYSTEM")
    print("=" * 60)
    
    # Test startup log
    logger.startup("Testing logging system")
    await asyncio.sleep(1)
    
    # Test success logs
    logger.success("Google Sheets connection established")
    logger.success("Telegram client connected")
    logger.success("Price tracker started")
    await asyncio.sleep(1)
    
    # Test signal logs
    logger.signal_received("PEPE", "Crypto Signals Pro")
    logger.signal_received("DOGE", "Pump Signals")
    await asyncio.sleep(1)
    
    # Test tracking logs
    logger.tracking_update("PEPE", 5, 1.25)
    logger.tracking_update("DOGE", 10, 2.45)
    await asyncio.sleep(1)
    
    # Test alert logs  
    logger.alert_triggered("2x", "PEPE")
    logger.alert_triggered("5x", "DOGE")
    await asyncio.sleep(1)
    
    # Test warning logs
    logger.warning("Failed to parse signal from channel")
    logger.warning("DexScreener rate limit reached")
    await asyncio.sleep(1)
    
    # Test error logs
    logger.api_error("DexScreener", "HTTP 429 - Rate limit")
    logger.error("Failed to update spreadsheet", exc_info=False)
    await asyncio.sleep(1)
    
    # Test debug logs
    logger.debug("Processing 5 active signals")
    logger.debug("Message received from channel")
    await asyncio.sleep(1)
    
    # Test info logs
    logger.info("📊 Monitoring 3 channels, tracking 5 signals")
    logger.stopped_tracking("SHIB")
    await asyncio.sleep(1)
    
    # Test heartbeat simulation
    for i in range(3):
        logger.heartbeat(f"Test heartbeat #{i+1} - All systems operational")
        await asyncio.sleep(2)
    
    # Test continuous heartbeat like real bot
    logger.info("\n🔄 Starting continuous heartbeat simulation (Ctrl+C to stop)")
    
    try:
        heartbeat_count = 0
        while True:
            heartbeat_count += 1
            
            # Normal heartbeat every 5 seconds (instead of 5 minutes for testing)
            logger.heartbeat(f"Heartbeat #{heartbeat_count} - Monitoring 3 channels, tracking 5 signals")
            
            # Hourly status every 5 heartbeats (instead of 12 for testing)
            if heartbeat_count % 5 == 0:
                logger.info("📊 Hourly Status Report:")
                logger.info("   • Active signals: 5")
                logger.info("   • Monitored channels: 3")
                logger.info(f"   • Bot uptime: {heartbeat_count * 5} seconds")
                
            # Simulate some activity between heartbeats
            if heartbeat_count % 3 == 0:
                logger.tracking_update("PEPE", 15, 1.85)
            elif heartbeat_count % 4 == 0:
                logger.signal_received("NEW_TOKEN", "Signal Channel")
                
            await asyncio.sleep(5)  # 5 seconds for testing instead of 5 minutes
            
    except KeyboardInterrupt:
        logger.info("🛑 Heartbeat test stopped by user")
        logger.info("👋 Test completed successfully")

if __name__ == "__main__":
    try:
        asyncio.run(test_logging())
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)