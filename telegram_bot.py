import asyncio
import telegram
from telegram.ext import Application, CommandHandler, CallbackContext
from typing import Dict
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MESSAGE_FOOTER
from logger import logger

class TelegramBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.bot = None
        self.application = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize the Telegram bot"""
        try:
            self.bot = telegram.Bot(token=self.bot_token)
            
            # Test bot connection
            bot_info = await self.bot.get_me()
            logger.info(f"Bot initialized successfully: @{bot_info.username}")
            
            # Initialize application for command handling
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("start", self.start_command))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            return False
    
    async def send_otp_message(self, otp_data: Dict) -> bool:
        """
        Send formatted OTP message to Telegram channel
        """
        try:
            # Format the message
            message = self.format_otp_message(otp_data)
            
            # Send message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"OTP message sent to Telegram: {otp_data['otp']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def format_otp_message(self, otp_data: Dict) -> str:
        """
        Format OTP data into Telegram message
        """
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""<b>𝑵𝑬𝑾 𝑶𝑻𝑷 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫 🟢</b>

<b>Live SMS - IVORY COAST</b>
<b>SID</b> - {otp_data.get('service', 'Unknown')}
<b>Mobile</b> - <code>{otp_data.get('mobile', 'Unknown')}</code>
<b>OTP</b> - <code>{otp_data.get('otp', 'Unknown')}</code>
<b>Time</b> - {timestamp}

<i>Message:</i> {otp_data.get('message_content', '')[:100]}{'...' if len(otp_data.get('message_content', '')) > 100 else ''}

{MESSAGE_FOOTER}"""
        
        return message
    
    async def send_status_message(self, status_text: str) -> bool:
        """
        Send status message to Telegram channel
        """
        try:
            message = f"🤖 <b>Bot Status Update</b>\n\n{status_text}\n\n{MESSAGE_FOOTER}"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("Status message sent to Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send status message: {e}")
            return False
    
    async def status_command(self, update, context):
        """Handle /status command"""
        status_text = "✅ Bot is running and monitoring for new OTPs"
        await update.message.reply_text(status_text)
    
    async def start_command(self, update, context):
        """Handle /start command"""
        welcome_text = f"""🤖 <b>Telegram OTP Bot</b>

I'm monitoring live SMS for new OTPs and will forward them to this channel.

<b>Commands:</b>
/status - Check bot status
/start - Show this message

{MESSAGE_FOOTER}"""
        
        await update.message.reply_text(welcome_text, parse_mode='HTML')
    
    async def start_polling(self):
        """Start polling for Telegram commands"""
        try:
            if self.application:
                logger.info("Starting Telegram bot polling...")
                await self.application.initialize()
                await self.application.start()
                await self.application.updater.start_polling()
                self.is_running = True
                
        except Exception as e:
            logger.error(f"Error starting Telegram polling: {e}")
    
    async def stop_polling(self):
        """Stop polling for Telegram commands"""
        try:
            if self.application and self.is_running:
                logger.info("Stopping Telegram bot polling...")
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                self.is_running = False
                
        except Exception as e:
            logger.error(f"Error stopping Telegram polling: {e}")
