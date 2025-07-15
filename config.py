import os

# Website credentials
WEBSITE_URL = "https://www.ivasms.com/login"
LIVE_SMS_URL = "https://www.ivasms.com/portal/live/my_sms"
EMAIL = os.getenv("WEBSITE_EMAIL", "Unseendevx2@gmail.com")
PASSWORD = os.getenv("WEBSITE_PASSWORD", "RheaxDev@2025")

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7752038917:AAG3KfU-d4n5ysuOvq1qomNx0JXA4dGcjmA")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1002541578739")

# Bot settings
CHECK_INTERVAL = 2  # seconds between checks
SESSION_TIMEOUT = 24 * 60 * 60  # 24 hours in seconds
MAX_RETRIES = 3
HEADLESS_MODE = True

# Message template
MESSAGE_FOOTER = "𝑩𝒐𝒕 𝒃𝒚 𝑫𝒆𝒗  \n𝑫𝑿𝒁 𝑾𝒐𝒓𝒌𝒛𝒐𝒏𝒆 𝒊𝒏𝒄."

# ChromeDriver settings
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",
    "--headless",
    "--remote-debugging-port=9222",
    "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Chrome binary path for Replit
CHROME_BINARY_PATH = "/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium"
