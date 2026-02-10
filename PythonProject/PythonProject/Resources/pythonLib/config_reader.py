"""
Config Reader Library for Robot Framework
Handles reading LDP_UI.yaml and configuring browser
"""
from typing import Any, Dict, List, Optional
from base_library import BaseLibrary


class ConfigReader(BaseLibrary):
    """Library for reading configuration from LDP_UI.yaml"""

    def get_browser_name(self) -> str:
        """Get default browser name from settings"""
        return self.get_setting('browser', 'name', default='Chrome')

    def get_browser_options(self, browser_name: Optional[str] = None) -> Dict[str, Any]:
        """Get browser options"""
        if browser_name:
            browsers = self.get_setting('browsers', default={})
            if browser_name in browsers:
                return browsers[browser_name].get('options', {})
            return {}
        return self.get_setting('browser', 'options', default={})

    def get_test_data_file(self) -> str:
        """Get test data Excel file path (uses GDR_InputFileName from YAML)"""
        return self.get_setting('Input_Test_Data', 'GDR_InputFileName', default='GDR_InputFileName.xlsx')
    
    def get_sms_smart_username(self) -> str:
        return self.get_setting('SMSSmart_environment', 'username', default='')

    def get_sms_smart_password(self) -> str:
        return self.get_setting('SMSSmart_environment', 'password', default='')
    
    # แก้ไขจาก @classmethod เป็น Instance Method
    def get_sms_smart_url(self) -> str:
        return self.get_setting('SMSSmart_environment', 'sms_url', default='')

    def get_ldp_base_url(self) -> str:
        """Get LDP base URL from settings"""
        return self.get_setting('LDP_environment', 'ldp_base_url', default='')
    
    def get_drdb_base_url(self) -> str:
        """Get base URL from settings"""
        return self.get_setting('DRDB_environment', 'drdb_base_url', default='')

# ---------- Module-level keyword wrappers ----------
# ส่วนนี้จะช่วยให้เรียกใช้ Keyword ได้โดยตรงหาก Import แบบ Module

_config_reader_instance = ConfigReader()

def get_browser_name() -> str:
    return _config_reader_instance.get_browser_name()

def get_ldp_base_url() -> str:
    return _config_reader_instance.get_ldp_base_url()

def get_drdb_base_url() -> str:
    return _config_reader_instance.get_drdb_base_url()

def get_timeout() -> int:
    return _config_reader_instance.get_timeout()

def get_implicit_wait() -> int:
    return _config_reader_instance.get_implicit_wait()

def get_sms_smart_url() -> str:
    return _config_reader_instance.get_sms_smart_url()

def get_sms_smart_username() -> str:
    return _config_reader_instance.get_sms_smart_username()

def get_sms_smart_password() -> str:
    return _config_reader_instance.get_sms_smart_password()