#!/usr/bin/env python3
"""
Test script to diagnose ChromeDriver issues
"""
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_chrome_setup():
    """Test different ChromeDriver setups"""
    print("Testing Chrome setup...")
    
    # Test 1: Check if chromium exists
    chrome_path = "/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium"
    print(f"Chrome binary exists: {os.path.exists(chrome_path)}")
    
    # Test 2: Check chromium version
    try:
        result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True)
        print(f"Chrome version: {result.stdout.strip()}")
    except Exception as e:
        print(f"Failed to get Chrome version: {e}")
    
    # Test 3: Try simple Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = chrome_path
    
    print("Testing webdriver creation...")
    try:
        # Try without service first
        driver = webdriver.Chrome(options=options)
        print("✅ WebDriver created successfully!")
        driver.get("https://www.google.com")
        print(f"✅ Successfully navigated to Google. Title: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ WebDriver creation failed: {e}")
        return False

if __name__ == "__main__":
    test_chrome_setup()