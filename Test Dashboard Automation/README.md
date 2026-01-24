# Test Dashboard Automation

Robot Framework test automation suite for regression testing of the Test Dashboard application.

## Overview

This test suite provides comprehensive coverage for both UI and API testing of the Test Dashboard, including:

- **Homepage (Project Selection Page)**: Project discovery, card display, statistics, navigation
- **Dashboard Page**: Summary cards, pie charts, data tables, search functionality
- **API Endpoints**: Projects, data, Excel preview, PDF export, thumbnails
- **Navigation Flows**: Homepage ↔ Dashboard navigation
- **Evidence Gallery**: Modal display, image gallery, Excel preview, PDF download

## Project Structure

```
Test Dashboard Automation/
├── tests/
│   ├── ui/                          # UI test suites
│   │   ├── homepage_tests.robot
│   │   ├── dashboard_tests.robot
│   │   ├── navigation_tests.robot
│   │   └── evidence_gallery_tests.robot
│   ├── api/                         # API test suites
│   │   ├── projects_api_tests.robot
│   │   ├── data_api_tests.robot
│   │   ├── excel_preview_api_tests.robot
│   │   ├── pdf_export_api_tests.robot
│   │   └── thumbnail_api_tests.robot
│   └── regression/                  # Regression test suite
│       └── regression_suite.robot
├── resources/
│   ├── keywords/                    # Reusable keywords
│   │   ├── common_keywords.robot
│   │   ├── homepage_keywords.robot
│   │   ├── dashboard_keywords.robot
│   │   └── api_keywords.robot
│   ├── page_objects/                # Page object models
│   │   ├── homepage_page.robot
│   │   └── dashboard_page.robot
│   └── variables/                    # Configuration and selectors
│       ├── config.robot
│       └── selectors.robot
├── test_data/                        # Test data files
│   └── test_data.json
├── results/                          # Test execution results
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Chrome browser (for UI tests)
- Flask Dashboard Server running on `http://127.0.0.1:5000`

## Installation

1. Navigate to the project directory:
```bash
cd "Test Dashboard Automation"
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Ensure the Dashboard server is running:
```bash
# From Test Dashboard/Dashboard_Report directory
python dashboard_server.py
```

## Test Execution

### Run All Tests
```bash
robot -d results tests/
```

### Run UI Tests Only
```bash
robot -d results --include ui tests/ui/
```

### Run API Tests Only
```bash
robot -d results --include api tests/api/
```

### Run Regression Suite
```bash
robot -d results tests/regression/regression_suite.robot
```

### Run with Specific Tags
```bash
# Run smoke tests
robot -d results --include smoke tests/

# Run critical tests
robot -d results --include critical tests/

# Run homepage tests
robot -d results --include homepage tests/

# Run dashboard tests
robot -d results --include dashboard tests/
```

### Run Specific Test Suite
```bash
robot -d results tests/ui/homepage_tests.robot
robot -d results tests/api/projects_api_tests.robot
```

## Test Coverage

### UI Tests (29 test cases)
- **Homepage**: 8 test cases
  - Homepage loading
  - Project cards display
  - Project statistics
  - Project card colors
  - Loading/error/empty states
  - Navigation

- **Dashboard**: 10 test cases
  - Dashboard loading
  - Navigation header
  - Summary cards (5 cards)
  - Pie chart
  - Latest run info
  - Tab navigation
  - Search functionality
  - Data table
  - Expand/collapse

- **Navigation**: 4 test cases
  - Homepage → Dashboard flow
  - Dashboard → Homepage flow
  - Project selection
  - URL parameters

- **Evidence Gallery**: 7 test cases
  - Modal display
  - Test case information
  - Evidence images
  - Image gallery
  - Image sorting
  - Excel preview
  - PDF download

### API Tests (31 test cases)
- **Projects API**: 6 test cases
  - GET /api/projects
  - Response structure
  - Project object structure
  - Stats calculation
  - Projects filtering
  - Empty list handling

- **Data API**: 8 test cases
  - GET /api/data
  - Project parameter
  - Response structure
  - Backward compatibility
  - Error handling
  - Timestamp grouping
  - Feature grouping
  - Status priority

- **Excel Preview API**: 5 test cases
  - GET /api/excel_preview
  - Excel data parsing
  - Table structure
  - Error handling
  - Path resolution

- **PDF Export API**: 6 test cases
  - POST /api/export_pdf
  - POST /api/export_testcase_pdf
  - POST /api/export_feature_pdfs_zip
  - PDF content verification
  - Evidence images in PDF
  - Thai font rendering

- **Thumbnail API**: 6 test cases
  - GET /api/evidence_thumbnail
  - Image thumbnail generation
  - HTML thumbnail generation
  - Thumbnail caching
  - Error handling
  - Cache info

### Regression Suite (10 test cases)
- Critical path tests covering:
  - Homepage → Dashboard flow
  - Dashboard data loading
  - API response validation
  - Navigation flows
  - Summary cards
  - Project discovery
  - Status priority logic
  - Backward compatibility
  - Error handling

**Total: 60 test cases**

## Test Tags

- `smoke` - Critical smoke tests
- `regression` - Regression test suite
- `api` - API tests
- `ui` - UI tests
- `homepage` - Homepage tests
- `dashboard` - Dashboard tests
- `gallery` - Evidence gallery tests
- `navigation` - Navigation flow tests
- `critical` - Critical path tests
- `negative` - Negative test cases

## Configuration

### Environment Variables

- `AUTOMATION_PROJECT_DIR` - Path to Automation_Project directory (default: `../../Automation_Project`)
- `DASHBOARD_URL` - Dashboard server URL (default: `http://127.0.0.1:5000`)

### Configuration Files

- `resources/variables/config.robot` - Main configuration variables
- `resources/variables/selectors.robot` - CSS/XPath selectors
- `test_data/test_data.json` - Test data (project names, expected values)

## Troubleshooting

### Dashboard Server Not Running
- Ensure Flask server is running on `http://127.0.0.1:5000`
- Check server logs for errors
- Verify `AUTOMATION_PROJECT_DIR` environment variable is set correctly

### Browser Issues
- Ensure Chrome browser is installed
- Update ChromeDriver if needed
- Check browser version compatibility

### Test Failures
- Check test execution logs in `results/` directory
- Review screenshots in `results/` directory (on failure)
- Verify test data in `test_data/test_data.json`
- Ensure Automation_Project has valid test results

## Best Practices

1. **Run smoke tests first**: Verify critical functionality before running full suite
2. **Use tags**: Filter tests by tags for faster execution
3. **Check results**: Review test reports in `results/` directory
4. **Update selectors**: Keep selectors updated if UI changes
5. **Maintain test data**: Keep `test_data.json` updated with valid project names

## Continuous Integration

This test suite can be integrated into CI/CD pipelines:

```bash
# Example CI command
robot -d results --include smoke --exclude skip tests/
```

## Maintenance

- **Selectors**: Update `resources/variables/selectors.robot` if UI changes
- **Keywords**: Add reusable keywords in `resources/keywords/`
- **Test Data**: Update `test_data/test_data.json` with new projects
- **Configuration**: Adjust `resources/variables/config.robot` for different environments

## Support

For issues or questions:
1. Check test execution logs
2. Review Dashboard server logs
3. Verify configuration and test data
4. Check Robot Framework documentation

## License

This test automation suite is part of the Test Dashboard project.
