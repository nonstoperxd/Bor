#!/usr/bin/env python3
"""
Health check server for Render deployment
This runs alongside the bot to provide a health endpoint
"""

import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'telegram-otp-bot',
                'version': '1.0.0'
            }
            
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_health_server():
    """Start health check server in background thread"""
    port = int(os.getenv('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Import and run the main bot
    from run import main
    main()