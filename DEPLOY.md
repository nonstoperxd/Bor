# Deploying Telegram OTP Bot to Render

## Prerequisites
1. A Render account (free tier available)
2. Your Telegram bot token
3. Your Telegram chat/channel ID
4. Your ivasms.com login credentials

## Deployment Steps

### 1. Create New Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository or upload files

### 2. Configure Build Settings
- **Environment**: Docker
- **Build Command**: (leave empty - Docker handles this)
- **Start Command**: (leave empty - Docker handles this)

### 3. Set Environment Variables
In the Render dashboard, add these environment variables:

**Required:**
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram channel/chat ID
- `WEBSITE_EMAIL`: Your ivasms.com email
- `WEBSITE_PASSWORD`: Your ivasms.com password

**Optional:**
- `PORT`: 10000 (default, usually auto-set by Render)
- `DISPLAY`: :99 (default)

### 4. Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy your bot
3. Monitor the logs for successful startup

## Files Created for Render Deployment

- `Dockerfile`: Container configuration
- `requirements.txt`: Python dependencies
- `start.sh`: Startup script with virtual display
- `health_server.py`: Health check endpoint
- `render.yaml`: Render-specific configuration (optional)
- `.env.example`: Environment variables template

## Health Check

The bot includes a health check endpoint at `/health` that Render uses to monitor the service status.

## Logs and Monitoring

Monitor your bot through:
- Render dashboard logs
- Telegram status messages
- Health check endpoint responses

## Troubleshooting

1. **Build failures**: Check requirements.txt and Dockerfile
2. **Browser issues**: Firefox is configured for headless operation
3. **Login problems**: Verify website credentials in environment variables
4. **Memory issues**: Render free tier has 512MB RAM limit

## Security Notes

- Never commit credentials to your repository
- Use environment variables for all sensitive data
- The bot runs in a secure Docker container
- All browser operations are headless and isolated

## Support

If you encounter issues:
1. Check Render logs for error messages
2. Verify all environment variables are set correctly
3. Test the bot locally first using the same environment variables