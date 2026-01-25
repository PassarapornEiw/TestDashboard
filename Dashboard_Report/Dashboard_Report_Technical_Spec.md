# Dashboard Report - Technical Specification
## Test Automation Dashboard - Implementation Details

### Document Information
- **Version**: 1.0
- **Last Updated**: January 2026
- **Based on**: `dashboard_server.py` (4,407 lines)
- **Purpose**: Technical implementation details for developers and maintainers

---

## 1. System Architecture

### 1.1 Technology Stack

**Backend**:
- **Framework**: Flask 2.0+
- **Language**: Python 3.x
- **Data Processing**: pandas, openpyxl
- **PDF Generation**: ReportLab (optional)
- **Image Processing**: PIL/Pillow (optional)
- **HTML Rendering**: Playwright (optional)
- **Chart Generation**: Matplotlib (optional)

**Frontend**:
- **HTML/CSS/JavaScript**: Vanilla JS (no frameworks)
- **Chart Library**: Chart.js
- **Gallery**: LightGallery
- **Styling**: Custom CSS with gradient themes

**Dependencies** (Optional Features):
- `REPORTLAB_AVAILABLE`: PDF export functionality
- `PIL_AVAILABLE`: Image processing and Excel placeholders
- `PLAYWRIGHT_AVAILABLE`: HTML screenshot generation
- `MATPLOTLIB_AVAILABLE`: Chart generation in PDFs

### 1.2 Project Structure

```
Test Dashboard/
└── Dashboard_Report/
    ├── dashboard_server.py          # Main Flask application (4,407 lines)
    ├── templates/
    │   ├── Homepage.html            # Project selection page
    │   └── dashboard.html           # Main dashboard page
    ├── static/
    │   ├── dashboard.js              # Frontend logic
    │   ├── dashboard.css             # Styling
    │   └── homepage.js               # Homepage logic
    └── chrome-win/                   # Playwright browser binaries
```

### 1.3 Configuration

**Global Variables**:
- `SERVER_DIR`: Directory of server script (`Path(__file__).parent`)
- `PROJECT_ROOT`: Two levels up from server (`SERVER_DIR.parent.parent`)
- `AUTOMATION_PROJECT_DIR`: Configurable via `AUTOMATION_PROJECT_DIR` environment variable
- `RESULTS_DIR`: Auto-discovered or project-specific results directory

**Path Resolution**:
- Results are stored in: `Automation_Project/<project_name>/results/`
- Timestamp folders: `YYYYMMDD-HHMMSS` or `YYYYMMDD_HHMMSS` format
- Evidence files: `results/<timestamp>/<feature>/<test_case_id>/`

---

## 2. Core Classes and Design Patterns

### 2.1 EvidenceProcessor Class

**Purpose**: Centralized evidence file processing for consistent behavior across Gallery, PDF, and ZIP exports.

**Location**: `dashboard_server.py` (line 220-439)

**Class Constants**:
- `MEDIA_EXTENSIONS`: `{'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.html', '.htm'}`
- `EXCEL_EXTENSIONS`: `{'.xlsx', '.xls'}`

**Static Methods**:

#### `extract_sort_key(file_path: str) -> tuple`
- **Purpose**: Extract sort key for evidence file sorting
- **Returns**: `(is_excel: bool, number: int, filename: str)`
- **Sorting Logic**:
  - Excel files sort after media files (`True > False`)
  - Files sorted by leading number (numeric), then by filename
  - HTML screenshots (`_preview.png`) use original HTML filename for sorting
  - HTML paths (lazy mode) use HTML filename for sorting

#### `process_html_to_screenshot(evidence_list: list, project_root: Path = None, lazy: bool = True) -> list`
- **Purpose**: Process HTML files and return PNG screenshot paths
- **Parameters**:
  - `evidence_list`: List of evidence file paths (relative to PROJECT_ROOT)
  - `project_root`: Path to project root (defaults to global PROJECT_ROOT)
  - `lazy`: If `True`, don't generate screenshots immediately (for homepage)
- **Lazy Mode** (`lazy=True`):
  - Checks if cached screenshot exists
  - If exists: returns PNG path
  - If not: returns HTML path (will be generated on-demand)
- **Eager Mode** (`lazy=False`):
  - Generates screenshot immediately via `ensure_thumbnail_exists()`
  - Returns PNG path if successful
- **Returns**: List of evidence paths with HTML files replaced by PNG screenshots (if available)

#### `collect_and_sort_evidence(evidence_list: list, project_root: Path = None, lazy: bool = True) -> list`
- **Purpose**: Sort evidence files and convert HTML files to PNG screenshots
- **Parameters**:
  - `lazy`: If `True`, don't generate screenshots immediately (for homepage)
- **Process**:
  1. Calls `process_html_to_screenshot()` to handle HTML files
  2. Sorts using `extract_sort_key()`
- **Returns**: Sorted list of evidence file paths

#### `ensure_thumbnail_exists(file_path: Path) -> Path`
- **Purpose**: Ensure thumbnail exists for HTML file, generate if missing
- **Process**:
  1. Checks if file exists
  2. Only processes HTML files (`.html`, `.htm`)
  3. Checks if cached thumbnail exists and is up-to-date (mtime comparison)
  4. Generates thumbnail if missing or outdated via `_html_to_thumbnail()`
- **Returns**: Path to thumbnail (for HTML) or original file path (for others)

#### `prepare_evidence_for_pdf(evidence_list: list, project_root: Path = None) -> list`
- **Purpose**: Prepare evidence list with thumbnails ready for PDF generation
- **Process**: Calls `collect_and_sort_evidence()` with `lazy=False` to ensure screenshots are generated
- **Returns**: Sorted list with thumbnails ready

### 2.2 ExcelColumnFinder Class

**Purpose**: Utility class for finding Excel columns by multiple candidate names.

**Location**: `dashboard_server.py` (line 178-218)

**Static Methods**:

#### `find_column(headers, candidates: list) -> str | None`
- **Purpose**: Find first matching column from candidates list
- **Parameters**:
  - `headers`: pandas Index or list of column names
  - `candidates`: List of candidate column names to search for
- **Returns**: First matching column name or `None`

**Usage**: Used to find columns like "TestResult", "Status", "Result" with case-insensitive matching.

### 2.3 ExcelRowAccessor Class

**Purpose**: Wrapper for accessing row data from pandas Series or dict.

**Location**: `dashboard_server.py` (line 442-500)

**Methods**:

#### `__init__(row)`
- **Purpose**: Initialize with a row (pandas Series or dict)
- **Attributes**:
  - `row`: Original row data
  - `available_fields`: List of available field names

#### `get(key, default=None)`
- **Purpose**: Get value from row by key
- **Returns**: Value from row or default

#### `get_by_candidates(candidates: list, default=None)`
- **Purpose**: Get value using first matching candidate key
- **Returns**: Value or default

**Usage**: Provides consistent access to Excel row data regardless of whether it's a pandas Series or dict.

### 2.4 PathNormalizer Class

**Purpose**: Utility class for normalizing file paths.

**Location**: `dashboard_server.py` (line 502-538)

**Static Methods**:

#### `normalize(path: str) -> str`
- **Purpose**: Normalize path separators to forward slashes
- **Returns**: Normalized path string

---

## 3. Core Functions

### 3.1 Status Normalization Functions

#### `normalize_test_status(status_series) -> pandas.Series`
- **Purpose**: Normalize test status values to standard lowercase format
- **Location**: `dashboard_server.py` (line 541-571)
- **Process**:
  1. Fills NaN and converts to string
  2. Applies regex-based normalization mapping:
     - `"failed"`, `"FAILED"`, `"Failed"` → `"fail"`
     - `"fail (major)"`, `"FAIL (MAJOR)"` → `"fail (major)"`
     - `"fail (block)"`, `"FAIL (BLOCK)"` → `"fail (block)"`
  3. Converts to lowercase
- **Returns**: Normalized pandas Series with lowercase status values

#### `normalize_status_for_display(status_raw) -> str`
- **Purpose**: Normalize status for display in UI/PDF
- **Location**: `dashboard_server.py` (line 574-612)
- **Input Formats Supported**:
  - `"pass"`, `"PASS"` → `"PASS"`
  - `"fail (major)"`, `"FAIL (MAJOR)"`, `"fail(major)"` → `"FAIL (Major)"`
  - `"fail (block)"`, `"FAIL (BLOCK)"`, `"fail(block)"` → `"FAIL (Block)"`
  - `"fail"`, `"failed"` (legacy) → `"FAIL (Major)"` (ตาม spec Section 8.2)
  - Others → `"UNKNOWN"`
- **Returns**: Normalized status string in display format

### 3.2 Excel Data Processing

#### `parse_excel_data(excel_path) -> dict | None`
- **Purpose**: Parse a single feature's Excel file to extract summary data
- **Location**: `dashboard_server.py` (line 1000-1244)
- **Process**:
  1. Reads Excel file using pandas
  2. Finds status column using `ExcelColumnFinder`
  3. Filters executed rows (`Execute = 'Y'`)
  4. Normalizes status using `normalize_test_status()`
  5. Counts passed/failed tests (including Major and Blocker)
  6. Determines feature status based on priority:
     - `failed_blocker` if any blocker failures
     - `failed_major` if any major failures
     - `passed` if all passed
     - `not_run` if no executed tests
  7. Collects evidence files from ResultFolder column
  8. Uses `EvidenceProcessor.collect_and_sort_evidence()` with `lazy=True`
- **Returns**: Dictionary with feature data or `None` on error

**Return Dictionary Structure**:
```python
{
    "feature_name": str,
    "excel_path": str,  # Relative to PROJECT_ROOT
    "total": int,
    "passed": int,
    "failed": int,
    "failed_major": int,
    "failed_blocker": int,
    "pass_rate": float,
    "status": str,  # "passed", "failed_major", "failed_blocker", "not_run"
    "run_timestamp": str,
    "test_evidence": dict  # {test_case_id: [list of evidence paths]}
}
```

### 3.3 Project Discovery

#### `discover_projects() -> list`
- **Purpose**: Discover all projects in AUTOMATION_PROJECT_DIR that have a 'results' folder
- **Location**: `dashboard_server.py` (line 1246-1280)
- **Process**:
  1. Scans `AUTOMATION_PROJECT_DIR` for subdirectories
  2. Checks if each has a `results` folder
  3. Validates timestamp folders using `is_valid_timestamp_folder()`
  4. Returns list of project dictionaries
- **Returns**: List of project dictionaries with `name` and `path` keys

#### `get_project_stats(project_path: Path) -> dict`
- **Purpose**: Get statistics for a specific project
- **Location**: `dashboard_server.py` (line 1281-1380)
- **Process**:
  1. Finds latest run (most recent timestamp folder)
  2. Parses Excel files in latest run
  3. Aggregates statistics across all features
  4. Calculates pass rate and overall status
- **Returns**: Dictionary with project statistics

### 3.4 HTML Screenshot Generation

#### `_get_thumbnail_path(html_path: Path) -> Path`
- **Purpose**: Generate thumbnail path for HTML file
- **Location**: `dashboard_server.py` (line 3728-3736)
- **Naming Convention**: `{html_filename}_preview.png`
- **Storage**: Same directory as HTML file (not in separate `.thumbnails` folder)

#### `_html_to_thumbnail(html_abs_path: Path, thumb_abs_path: Path = None, width: int = 800, height: int = 450) -> bool`
- **Purpose**: Generate PNG thumbnail for HTML file
- **Location**: `dashboard_server.py` (line 3738-3854)
- **Process**:
  1. Tries Playwright first (best quality):
     - Launches Chromium browser
     - Loads HTML file via `file://` URI
     - Takes full-page screenshot
     - Validates screenshot size (>10KB)
  2. Falls back to PIL if Playwright fails:
     - Creates placeholder PNG with HTML filename
- **Returns**: `True` if successful, `False` otherwise

### 3.5 PDF Generation

#### `generate_test_case_pdf_core(test_case_id, feature_name, run_timestamp, feature_data, test_case_row, mode='full') -> bytes`
- **Purpose**: Core PDF generation logic for individual test case
- **Location**: `dashboard_server.py` (line 2425-3052)
- **Parameters**:
  - `test_case_id`: Test case identifier
  - `feature_name`: Feature name
  - `run_timestamp`: Execution timestamp
  - `feature_data`: Feature data dictionary
  - `test_case_row`: Row data (pandas Series or dict)
  - `mode`: `'full'` for complete PDF, `'optimized'` for reduced content
- **Process**:
  1. Uses `ExcelRowAccessor` to access row data
  2. Normalizes status using `normalize_status_for_display()`
  3. Gets evidence files from `feature_data['test_evidence']`
  4. Uses `EvidenceProcessor.prepare_evidence_for_pdf()` (lazy=False)
  5. Generates PDF using ReportLab:
     - Test case header with status badge
     - Status colors: PASS (#28a745), FAIL (Major) (#ff5722), FAIL (Block) (#e51c23), UNKNOWN (#6c757d)
     - Evidence images (with HTML screenshots)
     - Excel file placeholders
  6. Returns PDF bytes
- **Returns**: PDF file bytes

---

## 4. API Endpoints

### 4.1 Page Routes

#### `GET /`
- **Handler**: `index()`
- **Purpose**: Render Homepage (Project Selection Page)
- **Returns**: Rendered `Homepage.html` template

#### `GET /dashboard`
- **Handler**: `dashboard()`
- **Purpose**: Render Dashboard Page
- **Query Parameters**: `project` (optional) - Project name
- **Returns**: Rendered `dashboard.html` template

### 4.2 Data Endpoints

#### `GET /api/projects`
- **Handler**: `get_projects()`
- **Purpose**: Get list of all projects with statistics
- **Returns**: JSON with projects array and metadata
- **Response Structure**:
```json
{
    "projects": [
        {
            "name": "string",
            "path": "string",
            "stats": {
                "pass_rate": float,
                "total_tests": int,
                "passed": int,
                "failed": int,
                "last_run": "string"
            }
        }
    ],
    "total_projects": int,
    "automation_project_dir": "string"
}
```

#### `GET /api/data`
- **Handler**: `get_dashboard_data()`
- **Purpose**: Get dashboard data for a specific project
- **Query Parameters**: `project` (optional) - Project name
- **Process**:
  1. Sets `RESULTS_DIR` to project-specific results folder if project provided
  2. Finds all Excel files in `RESULTS_DIR`
  3. Parses each Excel file using `parse_excel_data()`
  4. Groups by run timestamp
  5. Sorts runs by timestamp (most recent first)
  6. Restores original `RESULTS_DIR` in finally block
- **Returns**: JSON with runs array
- **Response Structure**:
```json
{
    "runs": [
        {
            "timestamp": "string",
            "features": [
                {
                    "feature_name": "string",
                    "excel_path": "string",
                    "total": int,
                    "passed": int,
                    "failed": int,
                    "failed_major": int,
                    "failed_blocker": int,
                    "pass_rate": float,
                    "status": "string",
                    "run_timestamp": "string",
                    "test_evidence": {
                        "test_case_id": ["list of evidence paths"]
                    }
                }
            ]
        }
    ],
    "total_runs": int
}
```

#### `GET /api/excel_preview`
- **Handler**: `excel_preview()`
- **Purpose**: Preview Excel file content
- **Query Parameters**: `path` - Path to Excel file (relative to PROJECT_ROOT)
- **Returns**: JSON with Excel data (headers, rows, total_rows)

### 4.3 PDF Export Endpoints

#### `POST /api/export_pdf`
- **Handler**: `export_pdf()`
- **Purpose**: Export full PDF report for all runs/features
- **Request Body**: JSON with run selection criteria
- **Returns**: PDF file (application/pdf)

#### `POST /api/export_testcase_pdf`
- **Handler**: `export_testcase_pdf()`
- **Purpose**: Export individual test case to PDF
- **Request Body**:
```json
{
    "test_case_id": "string",
    "feature_name": "string",
    "run_timestamp": "string",
    "project": "string"  // optional
}
```
- **Process**:
  1. Sets `RESULTS_DIR` to project-specific results folder if project provided
  2. Finds matching feature data
  3. Calls `generate_test_case_pdf_core()` with `mode='full'`
  4. Restores original `RESULTS_DIR` in finally block
- **Returns**: PDF file (application/pdf)

#### `POST /api/export_feature_pdfs_zip`
- **Handler**: `export_feature_pdfs_zip()`
- **Purpose**: Export all test case PDFs for a feature as ZIP
- **Request Body**:
```json
{
    "feature_name": "string",
    "run_timestamp": "string",
    "run_index": int,
    "feature_index": int,
    "project": "string"  // optional
}
```
- **Process**:
  1. Sets `RESULTS_DIR` to project-specific results folder if project provided
  2. Finds matching feature data
  3. Generates PDF for each test case
  4. Creates ZIP file with all PDFs
  5. Restores original `RESULTS_DIR` in finally block
- **Returns**: ZIP file (application/zip)

### 4.4 Thumbnail Endpoints

#### `GET /api/evidence_thumbnail`
- **Handler**: `api_evidence_thumbnail()`
- **Purpose**: Return (and cache) thumbnail for evidence files
- **Query Parameters**: `path` - Path to file (relative to PROJECT_ROOT)
- **Supported File Types**: `.xlsx`, `.xls`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.html`, `.htm`
- **Process**:
  - **Excel files**: Returns SVG placeholder
  - **Image files**: Returns image file directly
  - **HTML files**: 
    1. Checks if cached screenshot exists
    2. Generates screenshot if missing or outdated
    3. Returns PNG screenshot
    4. Falls back to SVG placeholder if generation fails
- **Returns**: Image file (PNG, SVG, or original image format)

#### `GET /api/html_thumbnail`
- **Handler**: Legacy endpoint - redirects to `/api/evidence_thumbnail`

### 4.5 File Serving

#### `GET /results/<path:filepath>`
- **Handler**: `serve_results(filepath)`
- **Purpose**: Serve files from results directory
- **Path Resolution**: 
  1. Tries `PROJECT_ROOT / filepath`
  2. Falls back to `RESULTS_DIR / filepath` for backward compatibility
- **Returns**: File content with appropriate MIME type

---

## 5. Data Flow and Processing

### 5.1 Homepage Data Flow

```
User visits / 
  → index() renders Homepage.html
  → Frontend calls /api/projects
  → get_projects() 
    → discover_projects()
    → get_project_stats() for each project
      → parse_excel_data() for latest run
    → Returns projects with statistics
  → Frontend renders project cards
```

### 5.2 Dashboard Data Flow

```
User visits /dashboard?project=<name>
  → dashboard() renders dashboard.html
  → Frontend calls /api/data?project=<name>
  → get_dashboard_data()
    → Sets RESULTS_DIR to project-specific folder
    → find_excel_files(RESULTS_DIR)
    → parse_excel_data() for each Excel file
      → EvidenceProcessor.collect_and_sort_evidence(lazy=True)
        → process_html_to_screenshot(lazy=True)
          → Returns cached PNG or HTML path (no generation)
    → Groups by timestamp
    → Returns runs array
  → Frontend renders dashboard with data
```

### 5.3 View Details Flow

```
User clicks "View Details"
  → Frontend calls getTestCaseDetails()
  → Frontend renders modal with evidence
  → Frontend requests thumbnails via /api/evidence_thumbnail
  → api_evidence_thumbnail()
    → For HTML files: generates screenshot on-demand
    → Returns thumbnail image
  → Frontend displays gallery
```

### 5.4 PDF Generation Flow

```
User clicks "Download PDF"
  → Frontend calls /api/export_testcase_pdf
  → export_testcase_pdf()
    → Sets RESULTS_DIR to project-specific folder
    → Finds feature data
    → generate_test_case_pdf_core()
      → normalize_status_for_display() - normalizes status
      → EvidenceProcessor.prepare_evidence_for_pdf()
        → collect_and_sort_evidence(lazy=False)
          → process_html_to_screenshot(lazy=False)
            → ensure_thumbnail_exists() - generates screenshots
      → Generates PDF with ReportLab
    → Restores RESULTS_DIR
  → Returns PDF file
```

---

## 6. Status Management

### 6.1 Status Values

**Internal Status Values** (lowercase, for processing):
- `"pass"`: Test passed
- `"fail (major)"`: Test failed (major severity)
- `"fail (block)"`: Test failed (blocker severity)
- `"fail"`: Legacy fail status (treated as major)
- `"not_run"`: Test not executed

**Display Status Values** (for UI/PDF):
- `"PASS"`: Test passed
- `"FAIL (Major)"`: Test failed (major severity)
- `"FAIL (Block)"`: Test failed (blocker severity)
- `"UNKNOWN"`: Unknown status

### 6.2 Status Priority System

**Priority Order** (highest to lowest):
1. `failed_blocker` - FAIL (Block)
2. `failed_major` - FAIL (Major)
3. `passed` - PASS
4. `not_run` - UNKNOWN

**Status Determination Logic**:
- **Feature Level**: If any test case is blocker → `failed_blocker`, else if any major → `failed_major`, else if all passed → `passed`
- **Run Level**: If any feature is blocker → `failed_blocker`, else if any major → `failed_major`, else → `passed`

### 6.3 Status Colors

**UI Colors** (CSS):
- PASS: `#28a745` (green)
- FAIL (Major): `#ff5722` (orange)
- FAIL (Block): `#e51c23` (red)
- UNKNOWN: `#6c757d` (gray)

**PDF Colors** (ReportLab):
- PASS: `#28a745`
- FAIL (Major): `#ff5722`
- FAIL (Block): `#e51c23`
- UNKNOWN: `#6c757d`

---

## 7. Performance Optimizations

### 7.1 Lazy Screenshot Generation

**Problem**: Generating HTML screenshots for 10,000+ files on homepage load is too slow.

**Solution**: Lazy loading with two modes:
- **Lazy Mode** (`lazy=True`): 
  - Used in `parse_excel_data()` for homepage
  - Checks for cached screenshots
  - Returns HTML path if screenshot doesn't exist (generated on-demand)
  - No Playwright browser launch during homepage load
- **Eager Mode** (`lazy=False`):
  - Used in `prepare_evidence_for_pdf()` for PDF generation
  - Generates screenshots immediately
  - Ensures all screenshots are ready for PDF

**Impact**: Homepage load time reduced from minutes to seconds for large datasets.

### 7.2 Screenshot Caching

**Caching Strategy**:
- Screenshots stored as `{html_filename}_preview.png` in same directory as HTML file
- Cache validation: Compares `mtime` of HTML file vs screenshot
- Regenerates only if HTML file is newer than screenshot
- No separate cache directory (simpler structure)

### 7.3 Evidence Sorting Optimization

**Single-Pass Sorting**:
- `EvidenceProcessor.collect_and_sort_evidence()` does sorting once
- Reused across Gallery, PDF, and ZIP exports
- No duplicate sorting operations

### 7.4 Project-Specific Results Directory

**Dynamic RESULTS_DIR**:
- `RESULTS_DIR` is set per-request based on project parameter
- Restored in `finally` block to prevent side effects
- Allows multiple projects without code changes

---

## 8. Error Handling

### 8.1 Graceful Degradation

**Optional Dependencies**:
- Features check availability flags before use:
  - `REPORTLAB_AVAILABLE`: PDF export disabled if False
  - `PIL_AVAILABLE`: Image processing disabled if False
  - `PLAYWRIGHT_AVAILABLE`: HTML screenshots disabled if False
- Fallback mechanisms:
  - HTML screenshots → SVG placeholder if Playwright unavailable
  - Excel thumbnails → SVG placeholder
  - PDF charts → Text summary if Matplotlib unavailable

### 8.2 Exception Handling

**Pattern**: Try-except blocks with logging:
- Errors logged with context (file path, operation)
- Functions return `None` or empty list on error
- API endpoints return appropriate HTTP status codes
- Frontend handles errors gracefully with user-friendly messages

### 8.3 Path Validation

**Security**:
- Path traversal protection: Validates paths are within `PROJECT_ROOT`
- File existence checks before operations
- Safe filename sanitization for downloads

---

## 9. Frontend Architecture

### 9.1 Data Loading

**Initial Load**:
```javascript
initializeDashboard()
  → loadDashboardData()
    → fetch('/api/data?project=<name>')
    → Process response into testData array
    → Calculate currentData from latest run
    → Render dashboard
```

### 9.2 Status Display

**Status Badge Generation**:
- Function: `getStatusBadge(status)` in `dashboard.js`
- Maps internal status to display format:
  - `'pass'` → `'PASS'` (green)
  - `'fail (major)'` → `'FAIL (Major)'` (orange)
  - `'fail (block)'` → `'FAIL (Block)'` (red)
  - `'not_run'` → `'UNKNOWN'` (gray)
  - Legacy `'fail'` → `'FAIL (Major)'` (orange)

### 9.3 Evidence Gallery

**Gallery Generation**:
- Function: `generateTestCaseGallery()` in `dashboard.js`
- Process:
  1. Gets test case details from Excel
  2. Gets evidence files from `test_evidence` dictionary
  3. Creates gallery items with thumbnails
  4. Uses `/api/evidence_thumbnail` for all file types
  5. Initializes LightGallery for image viewing

---

## 10. Configuration and Environment Variables

### 10.1 Environment Variables

**AUTOMATION_PROJECT_DIR**:
- **Purpose**: Override default Automation Project directory
- **Default**: `PROJECT_ROOT / "Automation_Project"`
- **Usage**: `set AUTOMATION_PROJECT_DIR=C:\Projects\Automation_Project`

**RESULTS_DIR** (Legacy):
- **Purpose**: Override auto-discovery for backward compatibility
- **Note**: Not recommended for new deployments

### 10.2 Path Configuration

**PROJECT_ROOT**:
- Calculated as: `SERVER_DIR.parent.parent`
- Base path for all relative paths

**AUTOMATION_PROJECT_DIR**:
- Configurable via environment variable
- Default: `PROJECT_ROOT / "Automation_Project"`

**RESULTS_DIR**:
- Auto-discovered or project-specific
- Set dynamically per request for project-specific operations

---

## 11. File Structure and Naming Conventions

### 11.1 Results Directory Structure

```
Automation_Project/
└── <project_name>/
    └── results/
        └── <timestamp>/          # YYYYMMDD-HHMMSS or YYYYMMDD_HHMMSS
            └── <feature>/        # e.g., Payment, Transfer
                └── <test_case_id>/  # e.g., TC001_225522422
                    ├── *.png, *.jpg  # Screenshots
                    ├── *.html        # HTML evidence
                    ├── *.xlsx        # Excel files
                    └── *_preview.png # Generated HTML screenshots
```

### 11.2 Excel File Naming

**Format**: `{prefix}_{feature}_Output_{timestamp}.xlsx`
- Example: `DRDB_Payment_Output_20250516-161132.xlsx`
- Feature name extracted from token before "Output"

### 11.3 Screenshot Naming

**HTML Screenshots**:
- Format: `{html_filename}_preview.png`
- Example: `testresult.html` → `testresult_preview.png`
- Stored in same directory as HTML file

---

## 12. API Request/Response Formats

### 12.1 Request Formats

**POST Endpoints** (JSON body):
```json
{
    "test_case_id": "string",
    "feature_name": "string",
    "run_timestamp": "string",
    "project": "string"  // optional
}
```

### 12.2 Response Formats

**Success Response** (JSON):
```json
{
    "runs": [...],
    "total_runs": int
}
```

**Error Response** (JSON):
```json
{
    "error": "string"
}
```

**File Responses**:
- PDF: `application/pdf`
- ZIP: `application/zip`
- Images: `image/png`, `image/jpeg`, `image/svg+xml`

---

## 13. Testing and Validation

### 13.1 Status Validation

**Validation Points**:
- Status normalization in `normalize_test_status()`
- Status display normalization in `normalize_status_for_display()`
- Status priority logic in `parse_excel_data()`
- Status badge display in frontend

### 13.2 Path Validation

**Validation Functions**:
- `is_valid_timestamp_folder()`: Validates timestamp format
- Path traversal checks in API endpoints
- File existence checks before operations

---

## 14. Maintenance and Updates

### 14.1 Code Organization

**Current Structure**: Monolithic file (4,407 lines)
- All functionality in single `dashboard_server.py`
- Classes and functions organized by purpose
- Clear separation of concerns within file

### 14.2 Extension Points

**Adding New Status Types**:
1. Update `normalize_test_status()` mapping
2. Update `normalize_status_for_display()` logic
3. Update status priority logic in `parse_excel_data()`
4. Update frontend status badge generation
5. Update CSS for new status colors

**Adding New Evidence Types**:
1. Update `EvidenceProcessor.MEDIA_EXTENSIONS` or `EXCEL_EXTENSIONS`
2. Update `evidence_patterns` in `parse_excel_data()`
3. Update `/api/evidence_thumbnail` handler if needed

---

## 15. Known Limitations and Future Improvements

### 15.1 Current Limitations

1. **Monolithic File**: Single 4,407-line file (consider refactoring)
2. **Synchronous Screenshot Generation**: Playwright blocks during screenshot generation
3. **No Background Processing**: All operations are request-synchronous
4. **Limited Caching**: Screenshot cache only (no data caching)

### 15.2 Potential Improvements

1. **Modular Architecture**: Split into separate modules (routes, services, utils)
2. **Background Jobs**: Use Celery or similar for async screenshot generation
3. **Data Caching**: Implement Redis or in-memory cache for parsed Excel data
4. **Batch Screenshot Generation**: Generate screenshots in background for all HTML files
5. **Database Integration**: Store metadata in database instead of parsing Excel each time

---

## Appendix A: Function Reference

### Utility Functions

- `is_valid_timestamp_folder(folder_name) -> bool`
- `discover_results_directory() -> Path`
- `escape_html_for_pdf(text) -> str`
- `sanitize_filename(name, replacement="_") -> str`
- `extract_timestamp_from_path(path_obj) -> str`
- `find_excel_files(base_dir) -> list[Path]`
- `safe_str_lower(series) -> pandas.Series`
- `find_first_column(headers, candidates) -> str | None`
- `filter_executed_rows(df) -> pandas.DataFrame`
- `get_row_by_id(df, id_candidates, target_id) -> pandas.Series | None`
- `get_test_case_description(excel_path, test_case_id) -> str`
- `format_timestamp_professional(timestamp_str) -> str`

### Thumbnail Functions

- `_get_thumbnail_path(html_path) -> Path`
- `_html_to_thumbnail(html_abs_path, thumb_abs_path, width, height) -> bool`
- `_html_preview_placeholder_svg(filename) -> bytes`
- `_excel_preview_placeholder_svg(filename) -> bytes`

### Font Management Functions

- `setup_unicode_cid_fonts() -> bool`
- `_try_register_font(font_name, ttf_path) -> bool`
- `verify_font_settings() -> None`
- `ensure_thai_fonts() -> None`

---

## Appendix B: Constants and Configuration

### Column Name Mappings

**Location**: `dashboard_server.py` (line 167-175)

```python
COLUMN_NAMES = {
    'test_case': ['TestCaseNo', 'Test Case No', 'TestCase', 'TC', 'Test Case'],
    'result_folder': ['ResultFolder', 'Result Folder', 'Folder', 'Path'],
    'status': ['TestResult', 'Status', 'Result'],
    'execute': ['Execute'],
    'description': ['Test Case Description', 'TestCaseDescription', 'Description', 'Test Description', 'Name', 'TestCaseDesc'],
    'error': ['Fail_Description', 'Fail Description', 'TestResult Description', 'Result Description', 'Error', 'Message', 'Failure Reason'],
    'expected': ['ExpectedResult', 'Expected Result', 'Expected', 'Expected Outcome'],
}
```

**Usage**: Used with `ExcelColumnFinder.find_column()` to find columns with flexible naming.

### Status Color Constants

**UI Colors** (CSS in `dashboard.css`):
```css
.status-passed: #28a745 (green)
.status-failed-major: #ff5722 (orange)
.status-failed-blocker: #e51c23 (red)
.status-not-run: #6c757d (gray)
```

**PDF Colors** (ReportLab in `dashboard_server.py`):
```python
STATUS_COLORS = {
    'PASS': '#28a745',
    'FAIL (Major)': '#ff5722',
    'FAIL (Block)': '#e51c23',
    'UNKNOWN': '#6c757d'
}
```

### PDF Font Configuration

**Location**: `dashboard_server.py` (line 613-614, 626-627)

**Default Fonts**:
- `PDF_FONT_NORMAL`: `'Helvetica'` (fallback)
- `PDF_FONT_BOLD`: `'Helvetica-Bold'` (fallback)

**Thai Font Support**:
- **Unicode CID Fonts** (preferred): `'HeiseiMin-W3'` (normal), `'HeiseiKakuGo-W5'` (bold)
- **TTF Fonts** (fallback): Searches for common Thai fonts (THSarabunNew, etc.)
- **Font Registration**: `setup_unicode_cid_fonts()` attempts to register Unicode CID fonts first
- **Font Fallback**: `ensure_thai_fonts()` searches for TTF fonts if CID fonts unavailable

**Font Initialization**:
- Called at module load time
- Updates global `PDF_FONT_NORMAL` and `PDF_FONT_BOLD` variables
- Uses `globals()` to ensure font names persist across function calls

---

## Appendix C: Data Models

### Feature Data Dictionary

**Structure** (returned by `parse_excel_data()`):
```python
{
    "feature_name": str,              # Extracted from Excel filename
    "excel_path": str,                # Relative to PROJECT_ROOT
    "total": int,                      # Total executed tests
    "passed": int,                     # Passed tests
    "failed": int,                     # Total failed tests (major + blocker)
    "failed_major": int,               # Failed tests (major severity)
    "failed_blocker": int,             # Failed tests (blocker severity)
    "pass_rate": float,                # (passed / total) * 100
    "status": str,                     # "passed", "failed_major", "failed_blocker", "not_run"
    "run_timestamp": str,              # YYYYMMDD-HHMMSS or YYYYMMDD_HHMMSS
    "test_evidence": {                # Dictionary of test case evidence
        "test_case_id": [              # List of evidence file paths (relative to PROJECT_ROOT)
            "results/.../image1.png",
            "results/.../testresult_preview.png",  # HTML screenshot
            "results/.../file.xlsx"
        ]
    }
}
```

### Project Dictionary

**Structure** (returned by `discover_projects()`):
```python
{
    "name": str,                       # Project folder name
    "path": str                        # Relative path from AUTOMATION_PROJECT_DIR
}
```

### Project Statistics Dictionary

**Structure** (returned by `get_project_stats()`):
```python
{
    "pass_rate": float,                # Overall pass rate
    "total_tests": int,                # Total tests in latest run
    "passed": int,                     # Passed tests
    "failed": int,                     # Failed tests
    "last_run": str                    # Timestamp of latest run
}
```

### Run Dictionary

**Structure** (in API response):
```python
{
    "timestamp": str,                  # YYYYMMDD-HHMMSS or YYYYMMDD_HHMMSS
    "features": [                      # List of feature dictionaries
        {
            # Feature data dictionary (see above)
        }
    ]
}
```

---

## Document History

- **v1.0** (January 2026): Initial technical specification based on current codebase (4,407 lines)
