"""
Script to create Excel template files for test data
Run this script to generate Excel templates with proper column headers
"""
from pathlib import Path
from resources.libraries.excel_library import ExcelLibrary

def create_excel_templates():
    """Create all Excel template files"""
    project_root = Path(__file__).parent
    test_data_dir = project_root / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    excel_lib = ExcelLibrary()
    
    # Create main test data file
    main_file = test_data_dir / "test_data.xlsx"
    excel_lib.create_excel_template(
        str(main_file),
        sheet_names=["TestCases", "TestData", "ExpectedResults"]
    )
    print(f"Created: {main_file}")
    
    # Create debt re specific file
    debt_re_file = test_data_dir / "test_data_debt_re.xlsx"
    excel_lib.create_excel_template(
        str(debt_re_file),
        sheet_names=["TestCases", "TestData", "ExpectedResults"]
    )
    print(f"Created: {debt_re_file}")
    
    # Create rewrite settlement specific file
    rewrite_file = test_data_dir / "test_data_rewrite_settlement.xlsx"
    excel_lib.create_excel_template(
        str(rewrite_file),
        sheet_names=["TestCases", "TestData", "ExpectedResults"]
    )
    print(f"Created: {rewrite_file}")
    
    # Create error test cases file
    error_file = test_data_dir / "test_data_errors.xlsx"
    excel_lib.create_excel_template(
        str(error_file),
        sheet_names=["TestCases", "TestData", "ExpectedResults"]
    )
    print(f"Created: {error_file}")
    
    print("\nExcel templates created successfully!")
    print("Please fill in test case data in the TestCases sheet.")

if __name__ == "__main__":
    create_excel_templates()






