"""
Data Reader Library for Robot Framework
Handles reading test data from Excel and managing test execution
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
from base_library import BaseLibrary
from excel_library import ExcelLibrary


class DataReader(BaseLibrary):
    """Library for reading and managing test data"""

    def __init__(self):
        self.excel_lib = ExcelLibrary()
        self.test_data_file: Optional[str] = None

    def get_browser_config(self, browser_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get browser configuration from settings"""
        if browser_name:
            browsers = self.get_setting('browsers', default={})
            if browser_name in browsers and browsers[browser_name].get('enabled', False):
                return browsers[browser_name]
            return None
        return self.get_setting('browser', default={})

    def get_enabled_browsers(self) -> List[str]:
        """Get list of enabled browsers"""
        browsers = self.get_setting('browsers', default={})
        return [name for name, config in browsers.items() if config.get('enabled', False)]

    def load_test_data_file(self, excel_file_path: Optional[str] = None) -> str:
        """Load test data Excel file"""
        if not excel_file_path:
            excel_file_path = self.get_setting('test_data', 'excel_file', default='test_data/test_data.xlsx')

        resolved_path = self.resolve_path(excel_file_path)
        self.test_data_file = str(resolved_path)
        self.excel_lib.load_excel_file(self.test_data_file)
        return self.test_data_file

    def _ensure_workbook_loaded(self) -> None:
        """Ensure workbook is loaded before operations"""
        if not self.excel_lib.workbook:
            if not self.test_data_file:
                self.load_test_data_file()
            else:
                self.excel_lib.load_excel_file(self.test_data_file)

    def get_test_case_by_id(self, test_case_no: str) -> Dict[str, Any]:
        """Get complete test case data (TestCases + TestData + ExpectedResults)"""
        self._ensure_workbook_loaded()

        test_case: Dict[str, Any] = {}
        sheets = ["TestCases", "TestData", "ExpectedResults"]

        for sheet in sheets:
            try:
                test_case.update(self.excel_lib.get_test_case_data(test_case_no, sheet))
            except ValueError:
                pass

        return test_case

    def get_all_executable_test_cases(self) -> List[Dict[str, Any]]:
        """Get all test cases where Execute = Yes, merged with TestData"""
        self._ensure_workbook_loaded()

        # Get test cases from TestCases sheet
        test_cases = self.excel_lib.get_all_test_cases("TestCases", execute_only=True)

        # Merge with TestData for each test case
        for test_case in test_cases:
            test_case_no = test_case.get('TestCaseNo')
            if test_case_no:
                try:
                    test_data = self.excel_lib.get_test_case_data(test_case_no, "TestData")
                    test_case.update(test_data)
                except ValueError:
                    pass

        return test_cases

    def update_test_result(self, test_case_no: str, test_result: str, fail_description: str = "") -> bool:
        """Update test result in Excel file"""
        self._ensure_workbook_loaded()
        return self.excel_lib.update_test_result(test_case_no, test_result, fail_description)


# Module-level keyword wrappers (module-style library)
_data_reader_instance = DataReader()


def load_test_data_file(excel_file_path: Optional[str] = None) -> str:
    """Load test data Excel file"""
    return _data_reader_instance.load_test_data_file(excel_file_path)


def get_test_case_by_id(test_case_no: str) -> Dict[str, Any]:
    """Get complete test case data by TestCaseNo"""
    return _data_reader_instance.get_test_case_by_id(test_case_no)


def get_all_executable_test_cases() -> List[Dict[str, Any]]:
    """Get all executable test cases from Excel"""
    return _data_reader_instance.get_all_executable_test_cases()


def update_test_result(test_case_no: str, test_result: str, fail_description: str = "") -> bool:
    """Update test result in Excel"""
    return _data_reader_instance.update_test_result(test_case_no, test_result, fail_description)
