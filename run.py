#!/usr/bin/env python3
"""
Telegram OTP Bot Runner
This script provides a simple way to run the bot with proper error handling and restart capabilities.
"""

import asyncio
import sys
import time
from datetime import datetime
from main import main as bot_main
from logger import logger

class BotRunner:
    def __init__(self, max_restarts=None, restart_delay=60):
        self.max_restarts = max_restarts  # None means unlimited restarts
        self.restart_delay = restart_delay
        self.restart_count = 0
        self.start_time = datetime.now()
    
    async def run_with_restart(self):
        """Run the bot with automatic restart on failure - infinite restarts for keep-alive"""
        logger.info("🚀 Starting Telegram OTP Bot Runner with unlimited restarts...")
        
        while True:  # Infinite loop for keep-alive
            try:
                self.restart_count += 1
                logger.info(f"🔄 Bot attempt #{self.restart_count}")
                
                # Run the main bot
                await bot_main()
                
                # If we reach here, the bot exited normally (should not happen)
                logger.info("✅ Bot exited normally - restarting to keep alive...")
                await asyncio.sleep(self.restart_delay)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user (Ctrl+C)")
                break
                
            except Exception as e:
                logger.error(f"❌ Bot crashed: {e}")
                logger.info(f"⏳ Restarting in {self.restart_delay} seconds... (Restart #{self.restart_count})")
                await asyncio.sleep(self.restart_delay)
                
                # Reset restart count every 10 attempts to prevent overflow
                if self.restart_count >= 10:
                    self.restart_count = 0
                    logger.info("🔄 Restart count reset to keep bot alive")
        
        # Calculate uptime
        uptime = datetime.now() - self.start_time
        logger.info(f"📊 Total uptime: {uptime}")
        logger.info("🏁 Bot runner finished")

def print_startup_info():
    """Print startup information"""
    print("=" * 70)
    print("🤖 TELEGRAM OTP BOT RUNNER")
    print("=" * 70)
    print("📝 Features:")
    print("   • Automatic login to ivasms.com")
    print("   • Real-time SMS monitoring without page refresh")
    print("   • OTP extraction and Telegram forwarding")
    print("   • Session management (24h timeout)")
    print("   • Duplicate prevention")
    print("   • Auto-restart on failures")
    print()
    print("📋 Commands:")
    print("   • Ctrl+C: Stop the bot")
    print("   • /status: Check bot status (in Telegram)")
    print("   • /start: Show bot info (in Telegram)")
    print("=" * 70)
    print()

def main():
    """Main entry point"""
    print_startup_info()
    
    # Create and run bot runner with unlimited restarts for keep-alive
    runner = BotRunner(max_restarts=None, restart_delay=60)
    
    try:
        asyncio.run(runner.run_with_restart())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n💥 Fatal error in bot runner: {e}")
        print("🔄 Restarting bot runner...")
        # Even if runner fails, try to restart
        try:
            asyncio.run(runner.run_with_restart())
        except Exception as e2:
            print(f"💥 Critical error: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()
