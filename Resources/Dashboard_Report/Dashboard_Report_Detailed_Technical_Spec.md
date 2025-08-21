# Dashboard Report - Detailed Technical Specification

## 1. Latest Test Result (Section 1) - Technical Details

### 1.1 Summary Cards Implementation
```javascript
// Summary cards update logic
function updateSummaryCards() {
    const total = testData.length;
    const passed = testData.filter(tc => tc.status === 'PASS').length;
    const failed = testData.filter(tc => tc.status === 'FAIL').length;
    const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
    
    document.getElementById('total-tests').textContent = total;
    document.getElementById('passed-tests').textContent = passed;
    document.getElementById('failed-tests').textContent = failed;
    document.getElementById('pass-rate').textContent = passRate + '%';
}
```

**Data Flow:**
1. `loadDashboardData()` ดึงข้อมูลจาก `/api/data`
2. `updateSummaryCards()` คำนวณสถิติจาก `testData`
3. อัปเดต DOM elements ด้วยข้อมูลที่คำนวณได้

### 1.2 Pie Chart Implementation
```javascript
function initializePieChart() {
    const ctx = document.getElementById('pieChart').getContext('2d');
    pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Passed', 'Failed'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#28a745', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
```

**Chart.js Integration:**
- ใช้ CDN: `https://cdn.jsdelivr.net/npm/chart.js`
- Responsive design รองรับการปรับขนาด
- Custom colors สำหรับ Pass/Fail status

### 1.3 Latest Run Information
```javascript
function renderLatestRunInfo() {
    if (!currentData || currentData.length === 0) return;
    
    const latestRun = currentData[0]; // First item is latest
    const latestRunInfo = document.getElementById('latest-run-info');
    
    latestRunInfo.innerHTML = `
        <div class="run-label">Latest Run:</div>
        <div class="run-timestamp">${formatTimestamp(latestRun.timestamp)}</div>
        <div class="run-features">${latestRun.features.length} features</div>
    `;
}
```

**Data Structure:**
```python
# Backend data structure
{
    "timestamp": "20250516_161132",
    "features": [
        {
            "name": "Payment",
            "total": 5,
            "passed": 4,
            "failed": 1
        }
    ]
}
```

---

## 2. History Section (Section 2) - Technical Details

### 2.1 Tab Navigation System
```javascript
function setupEventListeners() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Render appropriate content
    if (tabName === 'timestamp') {
        renderTimestampAccordion();
    } else if (tabName === 'feature') {
        renderFeatureAccordion();
    }
}
```

**Tab Content Management:**
- **Timestamp Tab**: แสดงข้อมูลตามลำดับเวลา
- **Feature Tab**: จัดกลุ่มตาม Feature name

### 2.2 Search Functionality
```javascript
function filterAccordionTable(searchTerm, tbodyId) {
    const tbody = document.getElementById(tbodyId);
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const isVisible = text.includes(searchTerm.toLowerCase());
        row.style.display = isVisible ? '' : 'none';
    });
}
```

**Search Implementation:**
- Real-time filtering
- Case-insensitive search
- Search across all columns

### 2.3 Accordion Data Structure
```javascript
function renderTimestampAccordion() {
    const accordionContainer = document.querySelector('.tab-content.active tbody');
    
    currentData.forEach((run, runIndex) => {
        const runRow = createRunRow(run, runIndex);
        const featureRows = createFeatureRows(run.features, runIndex);
        
        accordionContainer.appendChild(runRow);
        featureRows.forEach(row => accordionContainer.appendChild(row));
    });
}
```

**Accordion Structure:**
```html
<tr class="accordion-header" data-run-index="0">
    <td colspan="4">
        <span class="chevron">▶</span>
        <strong>2025-05-16 16:11:32</strong>
        <span class="status-badge status-passed">PASS</span>
    </td>
</tr>
<tr class="accordion-body" data-run-index="0">
    <td colspan="4">
        <!-- Feature details -->
    </td>
</tr>
```

---

## 3. View Details Modal - Technical Details

### 3.1 Modal Structure
```html
<div id="featureModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>Feature Details</h2>
            <span class="close">&times;</span>
        </div>
        <div class="modal-body">
            <!-- Dynamic content -->
        </div>
    </div>
</div>
```

**Modal Management:**
```javascript
function viewFeatureDetailsInRun(runIndex, featureIndex) {
    const run = currentData[runIndex];
    const feature = run.features[featureIndex];
    
    // Populate modal content
    populateModalContent(feature, run.timestamp);
    
    // Show modal
    document.getElementById('featureModal').style.display = 'block';
}
```

### 3.2 Test Case Information Display
```javascript
function createTestCaseRow(testCase, featureName, runTimestamp) {
    return `
        <div class="test-case-header">
            <div class="test-case-title-group">
                <h3 class="test-case-title">${testCase.id}</h3>
                <button class="test-case-pdf-btn" 
                        onclick="exportTestCasePDF('${testCase.id}', '${featureName}', '${runTimestamp}')">
                    📄 PDF
                </button>
            </div>
            <div class="test-case-description">${testCase.description || 'No description'}</div>
            <div class="status-badge test-case-badge status-${testCase.status.toLowerCase()}">
                ${testCase.status}
            </div>
        </div>
    `;
}
```

**Data Binding:**
- Test Case ID และ Description จาก Excel data
- Status badge แสดงผลตามสถานะจริง
- PDF download button สำหรับแต่ละ Test Case

---

## 4. Excel Preview - Technical Details

### 4.1 Excel Data Parsing
```python
def parse_excel_data(excel_path):
    """Parse Excel file and extract test case information"""
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
        
        # Find relevant columns
        headers = [str(h).strip() for h in df.columns]
        id_col = find_first_column(headers, ['ID', 'Test Case ID', 'TC ID'])
        desc_col = find_first_column(headers, ['Description', 'Desc', 'Test Description'])
        status_col = find_first_column(headers, ['Status', 'Result', 'Test Result'])
        
        # Filter executed rows
        executed_df = filter_executed_rows(df)
        
        return {
            'headers': headers,
            'data': executed_df.to_dict('records'),
            'id_column': id_col,
            'description_column': desc_col,
            'status_column': status_col
        }
    except Exception as e:
        return {'error': str(e)}
```

**Column Detection Logic:**
```python
def find_first_column(headers, candidates):
    """Find the first matching column from candidates"""
    for candidate in candidates:
        for header in headers:
            if candidate.lower() in header.lower():
                return header
    return None
```

### 4.2 Excel Preview Display
```javascript
async function previewExcel(excelPath, targetElementId) {
    try {
        const response = await fetch(`/api/excel_preview?path=${encodeURIComponent(excelPath)}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        renderExcelTable(data, targetElementId);
    } catch (error) {
        console.error('Error previewing Excel:', error);
        showError(`Failed to load Excel preview: ${error.message}`);
    }
}
```

**Table Rendering:**
```javascript
function renderExcelTable(excelData, targetElementId) {
    const container = document.getElementById(targetElementId);
    
    let tableHTML = '<table class="excel-preview-table">';
    
    // Headers
    tableHTML += '<thead><tr>';
    excelData.headers.forEach(header => {
        tableHTML += `<th>${header}</th>`;
    });
    tableHTML += '</tr></thead>';
    
    // Data rows
    tableHTML += '<tbody>';
    excelData.data.forEach(row => {
        tableHTML += '<tr>';
        excelData.headers.forEach(header => {
            const value = row[header] || '';
            tableHTML += `<td>${formatTextWithLineBreaks(value)}</td>`;
        });
        tableHTML += '</tr>';
    });
    tableHTML += '</tbody></table>';
    
    container.innerHTML = tableHTML;
}
```

---

## 5. PDF Download - Technical Details

### 5.1 PDF Generation Backend
```python
@app.route('/api/export_pdf', methods=['POST'])
def export_pdf():
    """Generate PDF for entire run"""
    try:
        data = request.get_json()
        timestamp = data.get('timestamp')
        
        # Find run data
        run_data = find_run_by_timestamp(timestamp)
        if not run_data:
            return jsonify({'error': 'Run not found'}), 404
        
        # Generate PDF
        pdf_buffer = generate_run_pdf(run_data)
        
        # Return PDF file
        return send_file(
            io.BytesIO(pdf_buffer),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Test_Report_{timestamp}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**PDF Generation Process:**
1. รับ timestamp จาก frontend
2. ค้นหาข้อมูลการรัน
3. สร้าง PDF content
4. ส่งไฟล์กลับไปยัง frontend

### 5.2 PDF Content Generation
```python
def generate_run_pdf(run_data):
    """Generate PDF content for a test run"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Setup fonts
    setup_thai_fonts()
    
    # Build content
    story = []
    
    # Title
    title_style = getSampleStyleSheet()['Title']
    title_style.fontName = PDF_FONT_BOLD
    story.append(Paragraph(f"Test Run Report - {run_data['timestamp']}", title_style))
    story.append(Spacer(1, 20))
    
    # Summary table
    summary_data = create_summary_table(run_data)
    summary_table = Table(summary_data)
    story.append(summary_table)
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()
```

**Font Management:**
```python
def setup_thai_fonts():
    """Setup Thai fonts for PDF generation"""
    try:
        # Try Unicode CID fonts first
        if setup_unicode_cid_fonts():
            return True
        
        # Fallback to local TTF fonts
        font_dir = SERVER_DIR / "fonts"
        if font_dir.exists():
            for ttf_file in font_dir.glob("*.ttf"):
                register_font(ttf_file)
            return True
            
    except Exception as e:
        print(f"Font setup failed: {e}")
        return False
```

---

## 6. Gallery Modal - Technical Details

### 6.1 Gallery Structure
```javascript
function showAllImagesModal(testCaseName, images, status, actualFolderName = null) {
    const modal = document.getElementById('allImagesModal');
    const gallery = document.getElementById('allImagesGallery');
    
    // Clear previous content
    gallery.innerHTML = '';
    
    // Add images to gallery
    images.forEach((imagePath, index) => {
        const galleryItem = createGalleryItem(imagePath, index, testCaseName);
        gallery.appendChild(galleryItem);
    });
    
    // Update modal title
    const title = modal.querySelector('.modal-header h2');
    title.textContent = `Evidence for: ${testCaseName}`;
    
    // Show modal
    modal.style.display = 'block';
    
    // Initialize lightgallery
    initializeLightGallery(gallery);
}
```

**Gallery Item Creation:**
```javascript
function createGalleryItem(imagePath, index, testCaseName) {
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.innerHTML = `
        <img src="${imagePath}" alt="Evidence ${index + 1}" 
             data-src="${imagePath}" data-sub-html="${testCaseName}">
        <div class="gallery-item-info">
            <span>Evidence ${index + 1}</span>
        </div>
    `;
    return item;
}
```

### 6.2 LightGallery Integration
```javascript
function initializeLightGallery(galleryElement) {
    if (activeGallery) {
        activeGallery.destroy();
    }
    
    activeGallery = lightGallery(galleryElement, {
        selector: 'img',
        download: true,
        counter: true,
        enableDrag: true,
        enableSwipe: true,
        fullScreen: true,
        zoom: true,
        plugins: [lgZoom, lgFullscreen]
    });
}
```

**LightGallery Configuration:**
- **Selector**: ใช้ `img` elements
- **Download**: เปิดใช้งานการดาวน์โหลด
- **Counter**: แสดงจำนวนภาพ
- **Zoom**: รองรับการซูม
- **Fullscreen**: รองรับการแสดงผลเต็มหน้าจอ

---

## 7. Thumbnail Generation - Technical Details

### 7.1 HTML Thumbnail Generation
```python
def _html_to_thumbnail(html_abs_path: Path, thumb_abs_path: Path = None, 
                       width: int = 800, height: int = 450):
    """Generate thumbnail from HTML file using Playwright"""
    if not PLAYWRIGHT_AVAILABLE:
        return False
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': width, 'height': height})
            
            # Load HTML file
            page.goto(f"file://{html_abs_path}")
            
            # Wait for content to load
            page.wait_for_timeout(1000)
            
            # Take screenshot
            screenshot = page.screenshot(
                type='png',
                full_page=False,
                clip={'x': 0, 'y': 0, 'width': width, 'height': height}
            )
            
            # Save thumbnail
            if thumb_abs_path:
                thumb_abs_path.parent.mkdir(parents=True, exist_ok=True)
                thumb_abs_path.write_bytes(screenshot)
            
            browser.close()
            return True
            
    except Exception as e:
        print(f"HTML thumbnail generation failed: {e}")
        return False
```

**Playwright Configuration:**
- Headless mode สำหรับ server environment
- Custom viewport size
- Wait for content loading
- Screenshot capture

### 7.2 Evidence Thumbnail Generation
```python
def _create_evidence_thumbnail(image_path: Path, thumb_path: Path, 
                              max_width: int = 200, max_height: int = 150):
    """Create thumbnail from evidence image"""
    if not PIL_AVAILABLE:
        return False
    
    try:
        with PILImage.open(image_path) as img:
            # Calculate thumbnail size
            img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(thumb_path, 'PNG', optimize=True)
            
            return True
            
    except Exception as e:
        print(f"Evidence thumbnail generation failed: {e}")
        return False
```

**PIL Configuration:**
- LANCZOS resampling สำหรับคุณภาพที่ดี
- Optimize PNG output
- Maintain aspect ratio

---

## 8. Performance Optimization - Technical Details

### 8.1 Thumbnail Caching Strategy
```python
def _ensure_thumbnail_dir(html_path: Path = None) -> Path:
    """Ensure thumbnail directory exists and return path"""
    if html_path:
        # Create thumbnail path based on HTML file location
        thumb_dir = html_path.parent / "thumbnails"
    else:
        # Use default thumbnail directory
        thumb_dir = SERVER_DIR / "thumbnails"
    
    thumb_dir.mkdir(parents=True, exist_ok=True)
    return thumb_dir
```

**Cache Management:**
- Thumbnail ถูกสร้างในโฟลเดอร์ `thumbnails`
- ใช้ path-based naming convention
- Automatic cleanup ของ thumbnail เก่า

### 8.2 Lazy Loading Implementation
```javascript
async function prefetchEvidenceThumbnails(imagePaths) {
    // Prefetch thumbnails for better performance
    const thumbnailPromises = imagePaths.map(async (imagePath) => {
        try {
            const response = await fetch(`/api/evidence_thumbnail?path=${encodeURIComponent(imagePath)}`);
            if (response.ok) {
                return await response.blob();
            }
        } catch (error) {
            console.warn('Failed to prefetch thumbnail:', error);
        }
    });
    
    await Promise.allSettled(thumbnailPromises);
}
```

**Prefetching Strategy:**
- โหลด thumbnail ล่วงหน้า
- ใช้ Promise.allSettled สำหรับ error handling
- ไม่ block UI thread

---

## 9. Error Handling - Technical Details

### 9.1 Frontend Error Handling
```javascript
function showError(message, duration = 5000) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, duration);
}
```

**Error Display:**
- Temporary error messages
- Auto-dismissal
- Non-blocking user experience

### 9.2 Backend Error Handling
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    print(f"Unhandled exception: {e}")
    return jsonify({'error': 'An unexpected error occurred'}), 500
```

**Error Response Format:**
```json
{
    "error": "Error message description",
    "details": "Additional error details (optional)"
}
```

---

## 10. Security Implementation - Technical Details

### 10.1 File Path Validation
```python
def sanitize_filename(name: str, replacement: str = "_") -> str:
    """Sanitize filename to prevent path traversal attacks"""
    # Remove or replace dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        name = name.replace(char, replacement)
    
    # Limit length
    if len(name) > 255:
        name = name[:255]
    
    return name
```

**Security Measures:**
- Path traversal prevention
- Filename sanitization
- Length limitation

### 10.2 Directory Access Control
```python
def is_safe_path(path: Path, base_dir: Path) -> bool:
    """Check if path is within safe base directory"""
    try:
        path = path.resolve()
        base_dir = base_dir.resolve()
        return path.is_relative_to(base_dir)
    except ValueError:
        return False
```

**Access Control:**
- Restrict file access to results directory
- Path validation
- Directory traversal prevention

---

## 11. Configuration Management - Technical Details

### 11.1 Environment Configuration
```python
# Configuration constants
SERVER_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SERVER_DIR.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# Font configuration
PDF_FONT_NORMAL = 'Helvetica'
PDF_FONT_BOLD = 'Helvetica-Bold'

# Thumbnail configuration
THUMBNAIL_WIDTH = 800
THUMBNAIL_HEIGHT = 450
EVIDENCE_THUMBNAIL_WIDTH = 200
EVIDENCE_THUMBNAIL_HEIGHT = 150
```

**Configuration Structure:**
- Path-based configuration
- Font settings
- Thumbnail dimensions
- Feature flags

### 11.2 Feature Detection
```python
# Check for required dependencies
REPORTLAB_AVAILABLE = True if 'reportlab' in sys.modules else False
MATPLOTLIB_AVAILABLE = True if 'matplotlib' in sys.modules else False
PIL_AVAILABLE = True if 'PIL' in sys.modules else False
PLAYWRIGHT_AVAILABLE = True if 'playwright' in sys.modules else False

# Set capability flags
THUMBNAIL_CAPABLE = PIL_AVAILABLE or PLAYWRIGHT_AVAILABLE
PDF_CAPABLE = REPORTLAB_AVAILABLE
```

**Capability Management:**
- Dynamic feature detection
- Graceful degradation
- User notification

---

## 12. Testing Strategy - Technical Details

### 12.1 Unit Test Structure
```python
def test_excel_parsing():
    """Test Excel data parsing functionality"""
    test_file = "test_data.xlsx"
    result = parse_excel_data(test_file)
    
    assert 'headers' in result
    assert 'data' in result
    assert len(result['data']) > 0

def test_pdf_generation():
    """Test PDF generation functionality"""
    test_data = create_test_run_data()
    pdf_buffer = generate_run_pdf(test_data)
    
    assert len(pdf_buffer) > 0
    assert pdf_buffer.startswith(b'%PDF')
```

**Test Coverage:**
- Excel parsing
- PDF generation
- Thumbnail creation
- API endpoints

### 12.2 Integration Test Structure
```python
def test_end_to_end_workflow():
    """Test complete workflow from data loading to PDF generation"""
    # Load test data
    data = load_test_data()
    
    # Generate thumbnails
    thumbnails = generate_thumbnails(data)
    
    # Create PDF
    pdf = generate_pdf(data, thumbnails)
    
    # Verify results
    assert pdf is not None
    assert len(thumbnails) > 0
```

**Integration Testing:**
- End-to-end workflows
- Component interaction
- Performance testing

---

## 13. Monitoring and Logging - Technical Details

### 13.1 Performance Monitoring
```python
import time
import logging

def monitor_performance(func):
    """Decorator to monitor function performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logging.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        
        return result
    return wrapper
```

**Monitoring Features:**
- Function execution time
- Memory usage tracking
- Error rate monitoring

### 13.2 Logging Configuration
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**Logging Levels:**
- INFO: General operations
- WARNING: Non-critical issues
- ERROR: Critical failures
- DEBUG: Detailed debugging information

---

## 14. Deployment Considerations - Technical Details

### 14.1 Production Deployment
```python
# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Enable production logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    # Production error handling
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

**Production Features:**
- Disabled debug mode
- Enhanced error handling
- Production logging
- Security hardening

### 14.2 Docker Configuration
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright
RUN playwright install chromium

# Copy application
COPY . /app
WORKDIR /app

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "dashboard_server.py"]
```

**Docker Features:**
- Chromium installation
- Playwright setup
- Port exposure
- Volume mounting

---

## 15. Conclusion

เอกสาร Technical Specification นี้ครอบคลุมรายละเอียดการทำงานของทุกส่วนใน Dashboard Report ระบบได้รับการออกแบบให้มีความยืดหยุ่น ประสิทธิภาพ และความปลอดภัย โดยใช้เทคโนโลยีที่ทันสมัยและเหมาะสมสำหรับการใช้งานจริง

**Key Technical Highlights:**
- **Modular Architecture**: แยกส่วนการทำงานเป็นโมดูลที่ชัดเจน
- **Performance Optimization**: ใช้ caching และ lazy loading
- **Security**: ป้องกัน path traversal และ file access
- **Scalability**: รองรับการขยายระบบในอนาคต
- **Maintainability**: โค้ดที่อ่านง่ายและบำรุงรักษาได้
