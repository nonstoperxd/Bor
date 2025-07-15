import re
from typing import Optional, Dict
from logger import logger

class OTPExtractor:
    def __init__(self):
        # Common OTP patterns - matches 4-8 digit codes
        self.otp_patterns = [
            r'\b(\d{4,8})\b(?:\s+is\s+your)',  # "12345 is your"
            r'(?:code|otp|pin)[\s:]*(\d{4,8})',  # "code: 12345" or "OTP 12345"
            r'<#>\s*(\d{4,8})',  # "<#> 12345"
            r'verification[\s\w]*?(\d{4,8})',  # "verification code 12345"
            r'confirm[\s\w]*?(\d{4,8})',  # "confirm with 12345"
            r'\b(\d{4,8})\s*$',  # Numbers at end of message
            r'^\s*(\d{4,8})\b',  # Numbers at start of message
        ]
        
        # Service identification patterns
        self.service_patterns = {
            'facebook': r'facebook|fb',
            'google': r'google|gmail',
            'whatsapp': r'whatsapp|whats app',
            'instagram': r'instagram|insta',
            'twitter': r'twitter|x\.com',
            'telegram': r'telegram',
            'uber': r'uber',
            'amazon': r'amazon',
            'netflix': r'netflix',
            'spotify': r'spotify',
        }
    
    def extract_otp(self, message_content: str) -> Optional[str]:
        """
        Extract OTP from message content using multiple patterns
        """
        if not message_content:
            return None
        
        message_lower = message_content.lower()
        
        # Try each pattern
        for pattern in self.otp_patterns:
            match = re.search(pattern, message_lower)
            if match:
                otp = match.group(1)
                logger.info(f"OTP extracted using pattern '{pattern}': {otp}")
                return otp
        
        logger.warning(f"No OTP found in message: {message_content[:100]}...")
        return None
    
    def identify_service(self, message_content: str) -> str:
        """
        Identify the service from message content
        """
        if not message_content:
            return "Unknown"
        
        message_lower = message_content.lower()
        
        for service, pattern in self.service_patterns.items():
            if re.search(pattern, message_lower):
                return service.title()
        
        return "Unknown"
    
    def extract_message_data(self, sms_element) -> Optional[Dict]:
        """
        Extract all relevant data from SMS element
        """
        try:
            # Try to find message content in various possible selectors
            message_content = ""
            mobile_number = ""
            
            # Common selectors for message content
            content_selectors = [
                ".message-content",
                ".sms-content", 
                ".content",
                "[data-message]",
                ".text-content"
            ]
            
            for selector in content_selectors:
                try:
                    element = sms_element.find_element("css selector", selector)
                    if element and element.text.strip():
                        message_content = element.text.strip()
                        break
                except:
                    continue
            
            # If no specific selector works, get all text from the element
            if not message_content:
                message_content = sms_element.text.strip()
            
            # Try to find mobile number
            mobile_selectors = [
                ".mobile-number",
                ".phone-number",
                ".number",
                "[data-mobile]"
            ]
            
            for selector in mobile_selectors:
                try:
                    element = sms_element.find_element("css selector", selector)
                    if element and element.text.strip():
                        mobile_number = element.text.strip()
                        break
                except:
                    continue
            
            # Extract mobile number from message if not found separately
            if not mobile_number:
                mobile_match = re.search(r'\+?[\d\s\-\(\)]{10,15}', message_content)
                if mobile_match:
                    mobile_number = mobile_match.group().strip()
            
            # Extract OTP
            otp = self.extract_otp(message_content)
            if not otp:
                return None
            
            # Identify service
            service = self.identify_service(message_content)
            
            return {
                'otp': otp,
                'mobile': mobile_number or "Unknown",
                'service': service,
                'message_content': message_content,
                'timestamp': None  # Will be set by caller
            }
            
        except Exception as e:
            logger.error(f"Error extracting message data: {e}")
            return None
