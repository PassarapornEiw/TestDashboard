# Dashboard Report - Detailed Technical Specification

## 1. Latest Test Result (Section 1) - Technical Details

### 1.1 Summary Cards Implementation (5 Cards)
```javascript
// Summary cards update logic - Updated for 5 cards with new colors
function updateSummaryCards() {
    if (!currentData) return;
    
    document.getElementById('total-tests').textContent = currentData.total || 0;
    document.getElementById('passed-tests').textContent = currentData.passed || 0;
    
    // Separate failed major and blocker into different cards
    const failedMajor = currentData.failed_major || 0;
    const failedBlocker = currentData.failed_blocker || 0;
    
    document.getElementById('failed-major-tests').textContent = failedMajor;
    document.getElementById('failed-blocker-tests').textContent = failedBlocker;
    
    const passRate = currentData.pass_rate || currentData.passRate || 0;
    document.getElementById('pass-rate').textContent = passRate.toFixed(2) + '%';
}
```

**Data Flow:**
1. `loadDashboardData()` ดึงข้อมูลจาก `/api/data`
2. `updateSummaryCards()` คำนวณสถิติจาก `testData`
3. อัปเดต DOM elements ด้วยข้อมูลที่คำนวณได้

**5 Summary Cards:**
- **Total Executed**: จำนวน test cases ทั้งหมด
- **Passed**: จำนวน test cases ที่ผ่าน
- **FAIL (Major)**: จำนวน test cases ที่ล้มเหลวระดับ Major
- **FAIL (Blocker)**: จำนวน test cases ที่ล้มเหลวระดับ Blocker
- **Pass Rate**: อัตราการผ่านเป็นเปอร์เซ็นต์

### 1.2 Pie Chart Implementation
```javascript
function initializePieChart() {
    const ctx = document.getElementById('pieChart').getContext('2d');
    pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Passed', 'FAIL (Major)', 'FAIL (Blocker)'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#28a745', '#ff5722', '#e51c23']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Updated pie chart data update function
function updatePieChart() {
    if (!currentData || !pieChart) return;
    
    const passed = currentData.passed || 0;
    const failedMajor = currentData.failed_major || 0;
    const failedBlocker = currentData.failed_blocker || 0;
    
    // Update chart data for 3 statuses
    pieChart.data.labels = ['Passed', 'FAIL (Major)', 'FAIL (Blocker)'];
    pieChart.data.datasets[0].data = [passed, failedMajor, failedBlocker];
    pieChart.data.datasets[0].backgroundColor = ['#28a745', '#ff5722', '#e51c23'];
    
    pieChart.update();
}
```

**Chart.js Integration:**
- ใช้ CDN: `https://cdn.jsdelivr.net/npm/chart.js`
- Responsive design รองรับการปรับขนาด
- Custom colors สำหรับ 3 statuses:
  - Pass: #28a745 (เขียว)
  - FAIL Major: #ff5722 (ส้ม)
  - FAIL Blocker: #e51c23 (แดง)

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
            "failed_major": 1,
            "failed_blocker": 0,
            "status": "failed_major"
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
    <td colspan="5">
        <span class="chevron">▶</span>
        <strong>2025-05-16 16:11:32</strong>
        <span class="status-badge status-passed">PASS</span>
    </td>
</tr>
<tr class="accordion-body" data-run-index="0">
    <td colspan="5">
        <!-- Feature details -->
    </td>
</tr>
```

**Updated Column Headers:**
- **Timestamp Tab**: "Summary (Total) Passed/Failed Major/Failed Blocker"
- **Feature Tab**: "Summary (Total) Passed/Failed Major/Failed Blocker"

---

## 3. View Details Modal - Technical Details

### 3.1 Modal Structure
```html
<div id="featureModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>Feature Details: ${featureName}</h2>
            <span class="close">&times;</span>
        </div>
        <div class="modal-body">
            <!-- Test case details with updated status badges -->
        </div>
    </div>
</div>
```

### 3.2 Status Badge Implementation
```javascript
// Status badge generation with new colors and text
function generateStatusBadge(status) {
    switch(status) {
        case 'pass':
            return '<span class="status-badge status-passed">PASS</span>';
        case 'fail (major)':
            return '<span class="status-badge status-failed-major">FAIL (Major)</span>';
        case 'fail (blocker)':
            return '<span class="status-badge status-failed-blocker">FAIL (Blocker)</span>';
        default:
            return '<span class="status-badge status-not-run">NOT RUN</span>';
    }
}
```

---

## 4. Status Priority System - Technical Implementation

### 4.1 Backend Status Logic (Python)
```python
# Status determination with priority system
if total == 0:
    status = "not_run"  # No tests were executed
elif failed == 0:
    status = "passed"   # All valid tests passed
else:
    # Determine specific failure type with priority
    if failed_blocker > 0:
        status = "failed_blocker"   # Has blocker failures - PRIORITY HIGHEST
    else:
        status = "failed_major"     # Has major failures only
```

### 4.2 Frontend Status Logic (JavaScript)
```javascript
// Run level status determination
if (run.total === 0) {
    run.status = 'not_run';
} else if ((run.failed_blocker || 0) > 0) {
    run.status = 'failed_blocker';        // PRIORITY HIGHEST
} else if ((run.failed_major || 0) > 0 || (run.failed || 0) > 0) {
    run.status = 'failed_major';          // PRIORITY SECOND
} else {
    run.status = 'passed';
}

// Feature level status determination
if (feature.failed_blocker > 0) {
    featureStatusClass = 'status-failed-blocker';    // PRIORITY HIGHEST
    featureStatusText = 'FAIL (Blocker)';
} else {
    featureStatusClass = 'status-failed-major';      // PRIORITY SECOND
    featureStatusText = 'FAIL (Major)';
}
```

### 4.3 Status Priority Order
1. **FAIL (Blocker)** - Priority สูงสุด (สีแดง #e51c23)
2. **FAIL (Major)** - Priority ที่สอง (สีส้ม #ff5722)
3. **PASS** - Priority ที่สาม (สีเขียว #28a745)
4. **UNKNOWN** - Priority ต่ำสุด (สีเทา #6c757d)

---

## 5. CSS Implementation - Status Badge Colors

### 5.1 Status Badge CSS Classes
```css
/* PASS Status Badge - Green */
.status-badge.status-passed {
    background: linear-gradient(135deg, #28a745 0%, #20a23a 100%);
    color: white;
    font-weight: 600;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
}

/* FAIL (Major) Status Badge - Orange */
.status-badge.status-failed-major {
    background: linear-gradient(135deg, #ff5722 0%, #f4511e 100%);
    color: white;
    font-weight: 600;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
}

/* FAIL (Blocker) Status Badge - Red */
.status-badge.status-failed-blocker {
    background: linear-gradient(135deg, #e51c23 0%, #c62828 100%);
    color: white;
    font-weight: 600;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    box-shadow: 0 4px 15px rgba(229, 28, 35, 0.4);
}

/* NOT RUN Status Badge */
.status-badge.status-not-run {
    background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
    color: white;
    font-weight: 600;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    box-shadow: 0 4px 15px rgba(108, 117, 125, 0.4);
}
```

### 5.2 Summary Card CSS
```css
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.summary-card.failed-major .card-icon {
    background: linear-gradient(135deg, #ff5722, #f4511e);
}

.summary-card.failed-blocker .card-icon {
    background: linear-gradient(135deg, #e51c23, #c62828);
}
```

---

## 6. Data Display Format

### 6.1 Summary Table Format
```javascript
// Summary table with new color scheme
<td style="text-align: center; font-weight: bold;">
    (<span style="color: #8B4513;">${total}</span>) 
    <span style="color: #28a745;">${passed}</span>/
    <span style="color: #ff5722;">${failed_major || 0}</span>/
    <span style="color: #e51c23;">${failed_blocker || 0}</span>
</td>
```

**Color Scheme:**
- **Total**: สีน้ำตาล #8B4513
- **Passed**: สีเขียว #28a745
- **Failed Major**: สีส้ม #ff5722
- **Failed Blocker**: สีแดง #e51c23

### 6.2 Status Badge Text Format
- **PASS**: แสดงเป็น "PASS"
- **FAIL (Major)**: แสดงเป็น "FAIL (Major)"
- **FAIL (Blocker)**: แสดงเป็น "FAIL (Blocker)"
- **UNKNOWN**: แสดงเป็น "UNKNOWN"

---

## 7. Responsive Design Implementation

### 7.1 Mobile-First Approach
```css
@media (max-width: 768px) {
    .summary-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
    }
}

@media (max-width: 480px) {
    .summary-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .summary-card {
        padding: 20px;
    }
    
    .card-icon {
        font-size: 2rem;
        width: 50px;
        height: 50px;
    }
}
```

### 7.2 Table Responsiveness
```css
.table-container {
    overflow-x: auto;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.sub-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}
```

---

## 8. Performance Optimization

### 8.1 Thumbnail Caching
```javascript
// Thumbnail cache management
function prefetchEvidenceThumbnails(imagePaths) {
    imagePaths.forEach(path => {
        if (!thumbnailCache.has(path)) {
            // Preload thumbnail
            const img = new Image();
            img.src = path;
            thumbnailCache.set(path, img);
        }
    });
}
```

### 8.2 Lazy Loading
```javascript
// Lazy load feature details
async function viewFeatureDetailsInRunAsync(runIndex, featureIndex) {
    if (featureDetailsCache.has(`${runIndex}-${featureIndex}`)) {
        return featureDetailsCache.get(`${runIndex}-${featureIndex}`);
    }
    
    // Load and cache feature details
    const details = await loadFeatureDetails(runIndex, featureIndex);
    featureDetailsCache.set(`${runIndex}-${featureIndex}`, details);
    return details;
}
```

---

## 9. Error Handling and Validation

### 9.1 Status Validation
```javascript
// Validate status priority logic
function validateStatusPriority(features) {
    let hasBlocker = false;
    let hasMajor = false;
    
    features.forEach(feature => {
        if (feature.failed_blocker > 0) hasBlocker = true;
        if (feature.failed_major > 0) hasMajor = true;
    });
    
    // Priority validation
    if (hasBlocker && hasMajor) {
        console.log('Status Priority: FAIL (Blocker) takes precedence over FAIL (Major)');
    }
    
    return { hasBlocker, hasMajor };
}
```

### 9.2 Data Integrity Checks
```javascript
// Check data consistency
function validateFeatureData(feature) {
    const total = feature.total || 0;
    const passed = feature.passed || 0;
    const failedMajor = feature.failed_major || 0;
    const failedBlocker = feature.failed_blocker || 0;
    
    const calculatedTotal = passed + failedMajor + failedBlocker;
    
    if (total !== calculatedTotal) {
        console.warn(`Data inconsistency in feature ${feature.feature_name}: total=${total}, calculated=${calculatedTotal}`);
    }
    
    return total === calculatedTotal;
}
```

---

## 10. Testing and Validation

### 10.1 Status Priority Testing
```javascript
// Test status priority logic
function testStatusPriority() {
    const testCases = [
        { failed_major: 1, failed_blocker: 0, expected: 'failed_major' },
        { failed_major: 0, failed_blocker: 1, expected: 'failed_blocker' },
        { failed_major: 1, failed_blocker: 1, expected: 'failed_blocker' },
        { failed_major: 0, failed_blocker: 0, expected: 'passed' }
    ];
    
    testCases.forEach(testCase => {
        const result = determineStatus(testCase);
        console.assert(result === testCase.expected, 
            `Expected ${testCase.expected}, got ${result}`);
    });
}
```

### 10.2 Color Scheme Testing
```javascript
// Test color scheme consistency
function testColorScheme() {
    const expectedColors = {
        'status-passed': '#28a745',
        'status-failed-major': '#ff5722',
        'status-failed-blocker': '#e51c23',
        'status-not-run': '#6c757d'
    };
    
    Object.entries(expectedColors).forEach(([className, expectedColor]) => {
        const element = document.querySelector(`.${className}`);
        if (element) {
            const computedColor = getComputedStyle(element).backgroundColor;
            console.log(`${className}: ${computedColor} (expected: ${expectedColor})`);
        }
    });
}
```

---

## 11. Future Enhancements

### 11.1 Dynamic Color Scheme
```javascript
// Future: Dynamic color scheme management
const COLOR_SCHEMES = {
    default: {
        pass: '#28a745',
        failed_major: '#ff5722',
        failed_blocker: '#e51c23',
        not_run: '#6c757d'
    },
    high_contrast: {
        pass: '#00ff00',
        failed_major: '#ff8000',
        failed_blocker: '#ff0000',
        not_run: '#808080'
    }
};

function applyColorScheme(schemeName) {
    const scheme = COLOR_SCHEMES[schemeName];
    // Apply color scheme dynamically
}
```

### 11.2 Status Customization
```javascript
// Future: Custom status definitions
const CUSTOM_STATUSES = [
    { name: 'FAIL (Critical)', priority: 1, color: '#8B0000' },
    { name: 'FAIL (Blocker)', priority: 2, color: '#e51c23' },
    { name: 'FAIL (Major)', priority: 3, color: '#ff5722' },
    { name: 'FAIL (Minor)', priority: 4, color: '#ff9800' },
    { name: 'PASS', priority: 5, color: '#28a745' }
];
```

---

## 12. Conclusion

Dashboard Report ได้รับการอัพเดตให้รองรับ:

1. **5 Summary Cards** แทน 4 cards เดิม
2. **Status Priority System** ที่ให้ FAIL (Blocker) priority สูงสุด
3. **Updated Color Scheme** ที่ใช้สีใหม่ตาม specification
4. **Consistent Status Display** ในทุกส่วนของระบบ
5. **Responsive Design** ที่รองรับการแสดงผลบนอุปกรณ์ทุกขนาด

ระบบมีความเสถียรและรองรับการขยายตัวในอนาคต โดยมีการจัดการ priority และสีที่ชัดเจนและสอดคล้องกัน
