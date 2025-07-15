import asyncio
import signal
import sys
from datetime import datetime
from web_monitor import WebMonitor
from telegram_bot import TelegramBot
from logger import logger
from config import *

class TelegramOTPBot:
    def __init__(self):
        self.web_monitor = WebMonitor()
        self.telegram_bot = TelegramBot()
        self.running = False
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🤖 Initializing Telegram OTP Bot...")
        
        # Initialize Telegram bot
        if not await self.telegram_bot.initialize():
            logger.error("Failed to initialize Telegram bot")
            return False
        
        # Setup web driver
        if not self.web_monitor.setup_driver():
            logger.error("Failed to setup web driver")
            return False
        
        # Send startup message
        await self.telegram_bot.send_status_message("🚀 Bot started and initializing...")
        
        logger.info("✅ Bot initialized successfully")
        return True
    
    async def start_monitoring(self):
        """Start the main monitoring loop"""
        try:
            self.running = True
            logger.info("🔍 Starting OTP monitoring...")
            
            # Login to website
            if not self.web_monitor.login():
                await self.telegram_bot.send_status_message("❌ Failed to login to website")
                return False
            
            # Navigate to live SMS page
            if not self.web_monitor.navigate_to_live_sms():
                await self.telegram_bot.send_status_message("❌ Failed to navigate to live SMS page")
                return False
            
            # Send success message
            await self.telegram_bot.send_status_message("✅ Successfully logged in and monitoring live SMS")
            
            # Start Telegram polling in background
            telegram_task = asyncio.create_task(self.telegram_bot.start_polling())
            
            # Start monitoring (this is blocking)
            monitor_task = asyncio.create_task(
                asyncio.to_thread(self.web_monitor.monitor_new_messages, self.telegram_bot)
            )
            
            # Wait for either task to complete
            await asyncio.gather(telegram_task, monitor_task, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            await self.telegram_bot.send_status_message(f"❌ Monitoring error: {str(e)}")
        finally:
            self.running = False
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down bot...")
        self.running = False
        
        try:
            # Send shutdown message
            await self.telegram_bot.send_status_message("🛑 Bot is shutting down...")
            
            # Stop Telegram polling
            await self.telegram_bot.stop_polling()
            
            # Cleanup web monitor
            self.web_monitor.cleanup()
            
            logger.info("✅ Bot shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main function"""
    bot = TelegramOTPBot()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        asyncio.create_task(bot.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize bot
        if not await bot.initialize():
            logger.error("Failed to initialize bot")
            sys.exit(1)
        
        # Start monitoring
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot.shutdown()

if __name__ == "__main__":
    # Print startup banner
    print("=" * 60)
    print("🤖 TELEGRAM OTP BOT")
    print("=" * 60)
    print(f"📧 Email: {EMAIL}")
    print(f"🌐 Website: {WEBSITE_URL}")
    print(f"📱 Live SMS URL: {LIVE_SMS_URL}")
    print(f"💬 Telegram Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"⏱️  Check Interval: {CHECK_INTERVAL}s")
    print(f"🕒 Session Timeout: {SESSION_TIMEOUT // 3600}h")
    print("=" * 60)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
