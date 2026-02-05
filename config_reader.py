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
        """Get test data Excel file path"""
        return self.get_setting('test_data', 'excel_file', default='test_data/test_data.xlsx')

    def get_results_config(self) -> Dict[str, Any]:
        """Get results configuration"""
        return self.get_setting('results', default={})


# Module-level keyword wrappers (module-style library)
_config_reader_instance = ConfigReader()


def get_browser_name() -> str:
    """Get default browser name from settings"""
    return _config_reader_instance.get_browser_name()


def get_base_url() -> str:
    """Get base URL from settings"""
    return _config_reader_instance.get_base_url()


def get_timeout() -> int:
    """Get timeout from settings"""
    return _config_reader_instance.get_timeout()


def get_implicit_wait() -> int:
    """Get implicit wait from settings"""
    return _config_reader_instance.get_implicit_wait()


def get_test_data_file() -> str:
    """Get test data Excel file path"""
    return _config_reader_instance.get_test_data_file()


def get_results_config() -> Dict[str, Any]:
    """Get results configuration"""
    return _config_reader_instance.get_results_config()
