"""
Data Reader Library for Robot Framework
Handles reading test data from Excel and managing test execution
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from base_library import BaseLibrary
from xreader import excel


# Map logical sheet names to possible physical names (for workbooks using Main/LDPTestData etc.)
SHEET_NAME_ALTERNATIVES: Dict[str, List[str]] = {
    "TestCases": ["TestCases", "Main"],
    "TestData": ["TestData", "LDPTestData"],
    "ExpectedResults": ["ExpectedResults"],
}


class DataReader(BaseLibrary):
    """Library for reading and managing test data"""

    def __init__(self):
        self.excel_lib = excel()
        self.test_data_file: Optional[str] = None
        self._current_sheet: Optional[str] = None

    def _resolve_sheet_name(self, logical_name: str) -> str:
        """Resolve logical sheet name (e.g. TestCases) to actual sheet name in workbook."""
        if not self.excel_lib.wb:
            return logical_name
        candidates = SHEET_NAME_ALTERNATIVES.get(logical_name, [logical_name])
        for name in candidates:
            if name in self.excel_lib.wb.sheetnames:
                return name
        raise ValueError(f"Sheet '{logical_name}' not found. Available: {', '.join(self.excel_lib.wb.sheetnames)}")

    def get_browser_config(self, browser_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get browser configuration from LDP_UI config"""
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

    def load_test_data_file(self, excel_file_path: Optional[str] = None, default_sheet: str = "TestCases") -> str:
        """Load test data Excel file"""
        if not excel_file_path:
            excel_file_path = self.get_setting('test_data', 'excel_file', default='test_data/test_data.xlsx')

        resolved_path = self.resolve_path(excel_file_path)
        self.test_data_file = str(resolved_path)
        candidates = SHEET_NAME_ALTERNATIVES.get(default_sheet, [default_sheet])
        for sheet_name in candidates:
            try:
                self.excel_lib.readExcel(self.test_data_file, sheet_name)
                self._current_sheet = sheet_name
                return self.test_data_file
            except (KeyError, Exception) as e:
                if "does not exist" not in str(e) and "Worksheet" not in str(e):
                    raise
                continue
        raise FileNotFoundError(f"Cannot load Excel: no sheet among {candidates} found in {self.test_data_file}")

    def _ensure_workbook_loaded(self) -> None:
        """Ensure workbook is loaded before operations"""
        if not self.excel_lib.wb:
            if not self.test_data_file:
                self.load_test_data_file()
            else:
                candidates = SHEET_NAME_ALTERNATIVES.get("TestCases", ["TestCases", "Main"])
                for sheet_name in candidates:
                    try:
                        self.excel_lib.readExcel(self.test_data_file, sheet_name)
                        self._current_sheet = sheet_name
                        break
                    except (KeyError, Exception) as e:
                        if "does not exist" not in str(e) and "Worksheet" not in str(e):
                            raise
                        continue
                else:
                    raise FileNotFoundError(f"Cannot load Excel: no sheet among {candidates} in {self.test_data_file}")

    def get_test_case_by_id(self, test_case_no: str) -> Dict[str, Any]:
        """Get complete test case data (TestCases + TestData + ExpectedResults)"""
        self._ensure_workbook_loaded()

        test_case: Dict[str, Any] = {}
        sheets = ["TestCases", "TestData", "ExpectedResults"]

        for sheet in sheets:
            try:
                self.excel_lib.switch_sheet(self._resolve_sheet_name(sheet))
                row_no, data_table = self.excel_lib.get_row_where(
                    headerIndex=1,
                    filterHeader='TestCaseNo',
                    valueToFilter=test_case_no
                )
                if data_table:
                    test_case.update(data_table[0])
            except Exception:
                pass

        return test_case

    def get_all_executable_test_cases(self) -> List[Dict[str, Any]]:
        """Get all test cases where Execute = Yes, merged with TestData"""
        self._ensure_workbook_loaded()

        # Get ALL rows from TestCases sheet
        self.excel_lib.switch_sheet(self._resolve_sheet_name("TestCases"))
        all_rows = self.excel_lib.get_all_rows(headerIndex=1)

        # Filter with case-insensitive comparison (same as original excel_library.py)
        test_cases = [
            row for row in all_rows
            if str(row.get('Execute', '')).strip().lower() == 'yes'
        ]

        # Merge with TestData for each test case
        for test_case in test_cases:
            test_case_no = test_case.get('TestCaseNo')
            if test_case_no:
                try:
                    self.excel_lib.switch_sheet(self._resolve_sheet_name("TestData"))
                    _, test_data_rows = self.excel_lib.get_row_where(
                        headerIndex=1,
                        filterHeader='TestCaseNo',
                        valueToFilter=test_case_no
                    )
                    if test_data_rows:
                        test_case.update(test_data_rows[0])
                except Exception:
                    pass

        return test_cases

    def update_test_result(self, test_case_no: str, test_result: str, fail_description: str = "") -> bool:
        """Update test result in Excel file"""
        self._ensure_workbook_loaded()

        self.excel_lib.switch_sheet(self._resolve_sheet_name("TestCases"))
        row_no_list, data_table = self.excel_lib.get_row_where(
            headerIndex=1,
            filterHeader='TestCaseNo',
            valueToFilter=test_case_no
        )

        if not row_no_list:
            raise ValueError(f"Test case '{test_case_no}' not found")

        row_idx = row_no_list[0]
        row_data = data_table[0].copy()

        row_data['TestResult'] = test_result
        if fail_description:
            row_data['Fail_Description'] = fail_description

        if 'ResultFolder' in row_data:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            row_data['ResultFolder'] = f"results/{timestamp}"

        self.excel_lib.update_row(row_idx, row_data)
        self.excel_lib.saveAllSheets(self.test_data_file)
        return True


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
