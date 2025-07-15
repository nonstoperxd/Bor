# Telegram OTP Bot

## Overview

This is a web scraping bot that automatically monitors SMS messages from ivasms.com and forwards OTP codes to a Telegram channel. The bot uses Selenium WebDriver to maintain an active session on the website and continuously monitors for new SMS messages without refreshing the page to prevent data loss.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

### Core Components
- **Main Controller** (`main.py`): Orchestrates the entire bot operation and manages the monitoring loop
- **Web Monitor** (`web_monitor.py`): Handles website login, session management, and SMS monitoring using Selenium
- **Telegram Bot** (`telegram_bot.py`): Manages Telegram API interactions and message forwarding
- **OTP Extractor** (`otp_extractor.py`): Extracts OTP codes from SMS message content using regex patterns
- **Logger** (`logger.py`): Provides centralized logging functionality
- **Configuration** (`config.py`): Stores all configuration settings and credentials

### Architecture Pattern
The bot uses an event-driven monitoring pattern where:
1. Web monitor continuously polls the SMS page for new messages
2. When new messages are detected, OTP extractor processes the content
3. Valid OTPs are forwarded to Telegram via the bot component
4. The system maintains state to prevent duplicate message forwarding

## Key Components

### Web Monitoring
- **Technology**: Selenium WebDriver with Chrome
- **Purpose**: Maintains active session on ivasms.com and monitors SMS messages
- **Session Management**: 24-hour session with automatic re-login
- **Anti-Detection**: Uses various Chrome options to avoid bot detection

### Telegram Integration
- **Library**: python-telegram-bot
- **Functionality**: Sends formatted OTP messages to specified channel
- **Error Handling**: Robust error handling with retry mechanisms

### OTP Processing
- **Regex Patterns**: Multiple patterns to extract 4-8 digit OTP codes
- **Service Detection**: Identifies source services (Facebook, Google, etc.)
- **Duplicate Prevention**: Tracks sent OTPs to avoid resending

### Configuration Management
- **Credentials**: Website login credentials and Telegram bot tokens
- **Settings**: Chrome driver options, timeouts, and intervals
- **Message Templates**: Standardized message formatting with footer

## Data Flow

1. **Initialization**:
   - Setup Chrome WebDriver with anti-detection measures
   - Initialize Telegram bot connection
   - Login to ivasms.com website

2. **Monitoring Loop**:
   - Navigate to live SMS page
   - Continuously monitor for new messages (every 2 seconds)
   - Extract message content without refreshing page

3. **Processing**:
   - Parse SMS content to extract OTP codes
   - Identify service/sender information
   - Check for duplicates using sent OTPs tracking

4. **Delivery**:
   - Format message with OTP and service information
   - Send to Telegram channel with custom footer
   - Log successful delivery and update tracking

5. **Error Recovery**:
   - Automatic session renewal after 24 hours
   - Driver restart on failures
   - Retry mechanisms for network issues

## External Dependencies

### Required Libraries
- `selenium`: Web automation and scraping
- `python-telegram-bot`: Telegram API interaction
- `asyncio`: Asynchronous operations
- Standard library modules: `re`, `time`, `datetime`, `logging`, `os`

### External Services
- **ivasms.com**: Source website for SMS monitoring
- **Telegram Bot API**: Message delivery platform
- **Chrome WebDriver**: Browser automation engine

### System Requirements
- Chrome browser or Chromium
- ChromeDriver executable
- Python 3.7+ with asyncio support

## Deployment Strategy

### Environment Setup
- Bot tokens and credentials configured via environment variables with fallback to hardcoded values
- Chrome options optimized for headless server environments
- Logging configured for console output with timestamps

### Error Handling
- **Session Management**: Automatic re-login on session expiration
- **Driver Failures**: WebDriver restart capabilities
- **Network Issues**: Retry mechanisms with exponential backoff
- **Duplicate Prevention**: State tracking to avoid resending messages

### Monitoring & Maintenance
- Comprehensive logging for debugging and monitoring
- Status commands available via Telegram bot
- Automatic restart capabilities with configurable limits
- Session timeout handling (24-hour automatic renewal)

### Security Considerations
- Credentials stored in configuration (should be moved to environment variables)
- Anti-detection measures to avoid website blocking
- Rate limiting through configurable check intervals
- Secure Telegram token handling

### Scalability Notes
- Single-threaded design optimized for one website monitoring
- Memory-efficient OTP tracking with set-based duplicate detection
- Configurable intervals to balance responsiveness vs. resource usage
- Modular design allows easy extension for multiple websites

## Render Deployment

### Deployment Files Created
- **Dockerfile**: Container configuration with Firefox and Python 3.11
- **requirements.txt**: Python dependencies for production
- **start.sh**: Startup script with virtual display (Xvfb)
- **health_server.py**: Health check endpoint for Render monitoring
- **render.yaml**: Render-specific configuration
- **.env.example**: Environment variables template
- **DEPLOY.md**: Complete deployment guide
- **test_render.py**: Local testing script for deployment validation

### Environment Variables for Render
**Required:**
- `TELEGRAM_BOT_TOKEN`: Telegram bot API token
- `TELEGRAM_CHAT_ID`: Target channel/chat ID
- `WEBSITE_EMAIL`: ivasms.com login email
- `WEBSITE_PASSWORD`: ivasms.com login password

**Optional:**
- `PORT`: Health check port (default: 10000)
- `DISPLAY`: Virtual display (default: :99)

### Container Features
- Firefox ESR for reliable headless browsing
- Virtual display (Xvfb) for browser operations
- Health check endpoint at `/health`
- Non-root user for security
- Optimized for 512MB RAM limit (Render free tier)

### Monitoring
- Health endpoint returns service status
- Telegram status messages for bot state
- Console logs for debugging
- Automatic restart on failures

## Recent Changes: Latest modifications with dates

### July 15, 2025
- ✅ **Bot deployment complete** - Successfully deployed and running
- ✅ **WebDriver compatibility fixed** - Firefox driver working as fallback for Chrome
- ✅ **Login automation working** - Successfully logs into ivasms.com
- ✅ **SMS monitoring active** - Bot monitoring live SMS page without refresh
- ✅ **Telegram integration complete** - OTP messages forwarded to channel -1002541578739
- ✅ **Session management** - 24-hour session with Remember Me checkbox
- ✅ **Duplicate prevention** - Tracks sent OTPs to avoid resending
- ✅ **Keep-alive functionality** - Unlimited restarts prevent automatic shutdown
- ✅ **Enhanced session checking** - Multiple validation checks for login status
- ✅ **Automatic re-login** - Smart retry logic with exponential backoff
- ✅ **Error recovery** - Handles WebDriver crashes and network issues gracefully
- ✅ **Render deployment ready** - Docker container with health checks and environment variables