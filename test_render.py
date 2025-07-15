#!/usr/bin/env python3
"""
Test script to verify Render deployment setup
"""

import os
import sys
import requests
import time
import threading
from health_server import start_health_server

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test health endpoint
    try:
        port = int(os.getenv('PORT', 10000))
        response = requests.get(f'http://localhost:{port}/health', timeout=5)
        
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def check_environment():
    """Check if all required environment variables are set"""
    print("Checking environment variables...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'WEBSITE_EMAIL',
        'WEBSITE_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Set these variables before deployment to Render")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
        
        import telegram
        print("✅ Telegram imported successfully")
        
        from webdriver_manager.firefox import GeckoDriverManager
        print("✅ WebDriver Manager imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Render deployment setup...\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", check_environment),
        ("Health Endpoint", test_health_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 All tests passed! Ready for Render deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Fix issues before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())