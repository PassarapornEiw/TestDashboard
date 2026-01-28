"""
OTP Provider Library for Robot Framework
Helper functions for SMS_OTP Gateway integration
"""
import re
from base_library import BaseLibrary


class OTPProvider(BaseLibrary):
    """Library for SMS_OTP Gateway helper functions"""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0'
    
    def format_phone_for_sms_gateway(self, phone: str) -> str:
        """
        Format phone number for SMS Gateway
        Converts 082-999-9999 or 0829999999 to +66829999999
        
        Args:
            phone: Phone number in any format
        
        Returns:
            Formatted phone number with +66 prefix
        """
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # If starts with 0, replace with +66
        if digits.startswith('0'):
            digits = '+66' + digits[1:]
        elif not digits.startswith('+'):
            digits = '+66' + digits
        
        return digits
    
    def get_sms_otp_config(self, key: str = None) -> str:
        """
        Get SMS_OTP configuration from settings
        
        Args:
            key: Config key to retrieve (url, username, password)
                 If None, returns all config as dict
        
        Returns:
            Config value or dict of all config
        """
        if key:
            return self.get_setting('sms_otp', key, default='')
        else:
            return {
                'url': self.get_setting('sms_otp', 'url', default='http://localhost:3000'),
                'username': self.get_setting('sms_otp', 'username', default='admin'),
                'password': self.get_setting('sms_otp', 'password', default='123456')
            }


# Module-level wrapper functions for Robot Framework
_otp_provider_instance = OTPProvider()


def format_phone_for_sms_gateway(phone: str) -> str:
    """Format phone number for SMS Gateway"""
    return _otp_provider_instance.format_phone_for_sms_gateway(phone)


def get_sms_otp_config(key: str = None) -> str:
    """Get SMS_OTP configuration from settings"""
    return _otp_provider_instance.get_sms_otp_config(key)
