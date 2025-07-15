import time
import json
import asyncio
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from config import *
import os
from logger import logger
from otp_extractor import OTPExtractor

class WebMonitor:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.last_login_time = None
        self.sent_otps = set()  # Track sent OTPs to avoid duplicates
        self.otp_extractor = OTPExtractor()
        self.last_message_count = 0
        
    def setup_driver(self):
        """Setup WebDriver with options - try Chrome first, then Firefox"""
        try:
            # First try Chrome
            if self._setup_chrome_driver():
                return True
            
            # If Chrome fails, try Firefox
            logger.info("Chrome setup failed, trying Firefox...")
            if self._setup_firefox_driver():
                return True
            
            logger.error("Failed to setup any WebDriver")
            return False
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            return False
    
    def _setup_chrome_driver(self):
        """Setup Chrome driver"""
        try:
            chrome_options = Options()
            
            # Add all chrome options
            for option in CHROME_OPTIONS:
                chrome_options.add_argument(option)
            
            # Set Chrome binary path for Replit
            if os.path.exists(CHROME_BINARY_PATH):
                chrome_options.binary_location = CHROME_BINARY_PATH
            
            # Additional options for better stability
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try multiple Chrome setup methods
            self.driver = None
            
            # Method 1: Use system PATH
            try:
                # Check if chromedriver is in PATH
                import subprocess
                result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    logger.info("Chrome driver setup using system PATH")
            except Exception:
                pass
            
            # Method 2: Try without service
            if not self.driver:
                try:
                    # Remove --headless and --disable-javascript temporarily for compatibility
                    minimal_options = Options()
                    minimal_options.add_argument("--no-sandbox")
                    minimal_options.add_argument("--disable-dev-shm-usage")
                    minimal_options.add_argument("--headless")
                    minimal_options.binary_location = CHROME_BINARY_PATH
                    
                    self.driver = webdriver.Chrome(options=minimal_options)
                    logger.info("Chrome driver setup with minimal options")
                except Exception as e:
                    logger.error(f"Minimal Chrome setup failed: {e}")
            
            if self.driver:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.implicitly_wait(10)
                self.driver.set_page_load_timeout(30)
                logger.info("Chrome driver setup successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def _setup_firefox_driver(self):
        """Setup Firefox driver as fallback"""
        try:
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            
            # Render/Docker specific settings
            firefox_options.add_argument("--disable-extensions")
            firefox_options.add_argument("--disable-plugins")
            firefox_options.add_argument("--disable-images")
            firefox_options.add_argument("--disable-web-security")
            firefox_options.add_argument("--allow-running-insecure-content")
            firefox_options.add_argument("--window-size=1920,1080")
            firefox_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0")
            
            # Set preferences for better compatibility
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference("useAutomationExtension", False)
            firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0")
            
            # Try to setup Firefox
            try:
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                logger.info("Firefox driver setup successfully")
                
                # Set timeouts
                self.driver.implicitly_wait(10)
                self.driver.set_page_load_timeout(30)
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to setup Firefox driver: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup Firefox driver: {e}")
            return False
    
    def login(self):
        """Login to the website"""
        try:
            logger.info("Attempting to login...")
            
            # Navigate to login page
            self.driver.get(WEBSITE_URL)
            time.sleep(3)
            
            # Wait for login form
            wait = WebDriverWait(self.driver, 20)
            
            # Find and fill email field
            email_selectors = [
                "input[name='email']",
                "input[type='email']",
                "#email",
                ".email-input",
                "input[placeholder*='email' i]"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not email_field:
                logger.error("Could not find email field")
                return False
            
            email_field.clear()
            email_field.send_keys(EMAIL)
            logger.info("Email entered")
            
            # Find and fill password field
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "#password",
                ".password-input"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.error("Could not find password field")
                return False
            
            password_field.clear()
            password_field.send_keys(PASSWORD)
            logger.info("Password entered")
            
            # Try to find and check "Remember Me" checkbox
            remember_selectors = [
                "input[name='remember']",
                "input[type='checkbox']",
                "#remember",
                ".remember-checkbox",
                "input[value='remember']"
            ]
            
            for selector in remember_selectors:
                try:
                    remember_checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if not remember_checkbox.is_selected():
                        remember_checkbox.click()
                        logger.info("Remember Me checkbox checked")
                    break
                except NoSuchElementException:
                    continue
            
            # Find and click login button
            login_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.login-btn",
                ".login-button",
                "button:contains('Login')",
                "input[value*='Login' i]"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                # Try to find by text content
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if "login" in button.text.lower():
                        login_button = button
                        break
            
            if not login_button:
                logger.error("Could not find login button")
                return False
            
            login_button.click()
            logger.info("Login button clicked")
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if self.check_login_success():
                self.is_logged_in = True
                self.last_login_time = datetime.now()
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - credentials might be incorrect")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def check_login_success(self):
        """Check if login was successful"""
        try:
            # Check current URL
            current_url = self.driver.current_url
            
            # If redirected away from login page, likely successful
            if "login" not in current_url.lower():
                return True
            
            # Check for dashboard or portal elements
            success_indicators = [
                ".dashboard",
                ".portal",
                ".user-menu",
                ".logout",
                "[href*='logout']",
                ".welcome"
            ]
            
            for selector in success_indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, selector)
                    return True
                except NoSuchElementException:
                    continue
            
            # Check for error messages
            error_selectors = [
                ".error",
                ".alert-danger",
                ".login-error",
                "[class*='error']"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if error_element.is_displayed():
                        logger.error(f"Login error: {error_element.text}")
                        return False
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking login success: {e}")
            return False
    
    def navigate_to_live_sms(self):
        """Navigate to live SMS page"""
        try:
            logger.info("Navigating to live SMS page...")
            self.driver.get(LIVE_SMS_URL)
            time.sleep(5)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 20)
            
            # Check if page loaded successfully
            try:
                # Look for common elements that indicate the page loaded
                page_indicators = [
                    ".sms-list",
                    ".message-list",
                    ".live-sms",
                    "table",
                    ".content"
                ]
                
                for selector in page_indicators:
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        logger.info("Live SMS page loaded successfully")
                        return True
                    except TimeoutException:
                        continue
                
                # If no specific indicators found, check if we're not on an error page
                if "error" not in self.driver.current_url.lower() and "login" not in self.driver.current_url.lower():
                    logger.info("Live SMS page appears to be loaded")
                    return True
                
            except TimeoutException:
                logger.warning("Timeout waiting for live SMS page elements")
            
            # Check if we got redirected to login (session expired)
            if "login" in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_logged_in = False
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to live SMS page: {e}")
            return False
    
    def get_sms_messages(self):
        """Get all SMS messages from the page"""
        try:
            # Common selectors for SMS messages
            message_selectors = [
                ".sms-message",
                ".message-item",
                ".sms-row",
                "tr[data-message]",
                ".live-sms-item",
                "tbody tr",
                ".message",
                "[class*='sms']",
                "[class*='message']"
            ]
            
            messages = []
            for selector in message_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        messages = elements
                        logger.debug(f"Found {len(messages)} messages using selector: {selector}")
                        break
                except Exception:
                    continue
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting SMS messages: {e}")
            return []
    
    def monitor_new_messages(self, telegram_bot):
        """Monitor for new messages without refreshing the page - with persistent keep-alive"""
        logger.info("Starting message monitoring with keep-alive...")
        
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while True:  # Infinite loop to keep bot alive
            try:
                # Enhanced session validation with multiple checks
                if not self.enhanced_session_check():
                    logger.warning("Session validation failed, attempting to re-login...")
                    retry_count = 0
                    max_retries = 3
                    
                    while retry_count < max_retries:
                        try:
                            if self.login():
                                logger.info("Re-login successful")
                                if self.navigate_to_live_sms():
                                    logger.info("Successfully navigated to live SMS page after re-login")
                                    consecutive_failures = 0
                                    break
                                else:
                                    logger.error("Failed to navigate to live SMS page after re-login")
                            else:
                                logger.error("Re-login failed")
                            
                            retry_count += 1
                            wait_time = 60 * retry_count  # Exponential backoff
                            logger.info(f"Waiting {wait_time} seconds before retry {retry_count}/{max_retries}")
                            time.sleep(wait_time)
                            
                        except Exception as e:
                            logger.error(f"Error during re-login attempt {retry_count}: {e}")
                            retry_count += 1
                            time.sleep(60)
                    
                    if retry_count >= max_retries:
                        logger.error("Max retries exceeded, but continuing to monitor...")
                        consecutive_failures += 1
                        time.sleep(300)  # Wait 5 minutes before trying again
                        continue
                
                # Get current messages
                try:
                    messages = self.get_sms_messages()
                    current_message_count = len(messages)
                    consecutive_failures = 0  # Reset on successful message retrieval
                    
                    # Check if there are new messages
                    if current_message_count > self.last_message_count:
                        logger.info(f"New messages detected: {current_message_count - self.last_message_count}")
                        
                        # Process only the new messages
                        new_messages = messages[self.last_message_count:]
                        
                        for message_element in new_messages:
                            try:
                                # Run in thread pool to avoid event loop issues
                                import threading
                                def run_process_message():
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    try:
                                        loop.run_until_complete(self.process_message(message_element, telegram_bot))
                                    finally:
                                        loop.close()
                                
                                thread = threading.Thread(target=run_process_message)
                                thread.start()
                            except Exception as e:
                                logger.error(f"Error starting message processing thread: {e}")
                        
                        self.last_message_count = current_message_count
                    
                    # Regular health check every 60 seconds
                    time.sleep(CHECK_INTERVAL)
                    
                except Exception as e:
                    logger.error(f"Error getting messages: {e}")
                    consecutive_failures += 1
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                consecutive_failures += 1
                
                # If too many consecutive failures, take longer break
                if consecutive_failures >= max_consecutive_failures:
                    logger.warning(f"Too many consecutive failures ({consecutive_failures}), taking longer break...")
                    time.sleep(600)  # Wait 10 minutes
                    consecutive_failures = 0
                else:
                    time.sleep(60)  # Wait 1 minute and try again
    
    async def process_message(self, message_element, telegram_bot):
        """Process a single message element"""
        try:
            # Extract message data
            message_data = self.otp_extractor.extract_message_data(message_element)
            
            if not message_data:
                return
            
            otp = message_data['otp']
            
            # Check for duplicates
            otp_key = f"{otp}_{message_data['mobile']}_{message_data['service']}"
            if otp_key in self.sent_otps:
                logger.debug(f"Duplicate OTP detected, skipping: {otp}")
                return
            
            # Add timestamp
            message_data['timestamp'] = datetime.now()
            
            # Send to Telegram
            success = await telegram_bot.send_otp_message(message_data)
            
            if success:
                self.sent_otps.add(otp_key)
                logger.info(f"New OTP processed and sent: {otp}")
            else:
                logger.error(f"Failed to send OTP to Telegram: {otp}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def enhanced_session_check(self):
        """Enhanced session validation with multiple checks"""
        try:
            # Check if driver is still alive
            if not self.driver:
                logger.error("Driver is None")
                return False
            
            # Check if we're still logged in
            if not self.is_logged_in:
                logger.info("Not logged in flag is False")
                return False
            
            # Check session timeout
            if self.last_login_time:
                time_elapsed = datetime.now() - self.last_login_time
                if time_elapsed.total_seconds() > SESSION_TIMEOUT:
                    logger.info("Session timeout reached")
                    self.is_logged_in = False
                    return False
            
            # Check current URL
            try:
                current_url = self.driver.current_url
                if "login" in current_url.lower():
                    logger.warning("Redirected to login page")
                    self.is_logged_in = False
                    return False
            except Exception as e:
                logger.error(f"Error getting current URL: {e}")
                return False
            
            # Try to find page elements to ensure page is still accessible
            try:
                # Check for body element
                self.driver.find_element(By.TAG_NAME, "body")
                
                # Check for live SMS specific elements
                live_sms_indicators = [
                    ".sms-list",
                    ".message-list", 
                    ".live-sms",
                    "table",
                    ".content",
                    "tbody"
                ]
                
                found_indicator = False
                for indicator in live_sms_indicators:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, indicator)
                        found_indicator = True
                        break
                    except NoSuchElementException:
                        continue
                
                if not found_indicator:
                    logger.warning("No live SMS page indicators found")
                    return False
                
                return True
                
            except NoSuchElementException:
                logger.error("Page body not found - possible connection issue")
                return False
                
        except Exception as e:
            logger.error(f"Error in enhanced session check: {e}")
            return False
    
    def check_session_valid(self):
        """Backward compatibility method"""
        return self.enhanced_session_check()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Driver cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
