# LDP Project Test Automation

Robot Framework test automation for LDP (Loan Debt Plan) Project

## Project Structure

```
LDP_Test_Automation/
├── tests/              # Test suites
├── resources/          # Keywords, page objects, variables
├── test_data/          # Excel test data files
├── config/             # Configuration files
└── results/            # Test results
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure browser in `config/settings.json`

3. Prepare test data in `test_data/test_data.xlsx`

## Running Tests

**Important:** Always use `-d results` to output files to the `results/` directory.

### Run all tests:
```bash
robot -d results tests/
```

### Run specific suite:
```bash
robot -d results tests/test_suites/01_authentication/
```

### Run by tags:
```bash
robot -d results --include debt_re tests/
robot -d results --include rewrite_settlement tests/
```

### Run regression suite:
```bash
robot -d results tests/regression/test_regression_suite.robot
```

## Test Data

Test data is stored in Excel files with columns:
- TestCaseNo
- ResultFolder
- Execute
- Module/Feature
- TestCaseDescription
- TestResult
- Fail_Description
- ExpectedResult
- Priority
- Status

## Configuration

Browser selection is configured in `config/settings.json`






