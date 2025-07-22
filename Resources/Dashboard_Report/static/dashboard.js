// Global variables
let pieChart = null;
let testData = [];
let currentData = null;
let activeGallery = null; // To hold the active lightgallery instance
let excelPreviewState = {};

// Helper function to format timestamp for display
function formatTimestamp(timestamp) {
    try {
        // Handle different timestamp formats
        let dateStr = timestamp.trim();
        
        // If format is YYYYMMDD_HHMMSS (e.g., "20250516_161132") or YYYYMMDD-HHMMSS (e.g., "20250516-161132")
        if (dateStr.match(/^\d{8}[-_]\d{6}$/)) {
            const year = dateStr.substring(0, 4);
            const month = dateStr.substring(4, 6);
            const day = dateStr.substring(6, 8);
            const hour = dateStr.substring(9, 11);
            const minute = dateStr.substring(11, 13);
            const second = dateStr.substring(13, 15);
            
            // Create date object and format as dd/mm/yyyy hh:mm:ss
            const date = new Date(year, month - 1, day, hour, minute, second);
            if (!isNaN(date.getTime())) {
                const dd = String(date.getDate()).padStart(2, '0');
                const mm = String(date.getMonth() + 1).padStart(2, '0');
                const yyyy = date.getFullYear();
                const hh = String(date.getHours()).padStart(2, '0');
                const min = String(date.getMinutes()).padStart(2, '0');
                const ss = String(date.getSeconds()).padStart(2, '0');
                
                return `${dd}/${mm}/${yyyy} ${hh}:${min}:${ss}`;
            }
        }
        
        // If format is YYYY-MM-DD HH:MM:SS or similar
        if (dateStr.match(/^\d{4}-\d{2}-\d{2}/) || dateStr.includes('T')) {
            const date = new Date(dateStr);
            if (!isNaN(date.getTime())) {
                const dd = String(date.getDate()).padStart(2, '0');
                const mm = String(date.getMonth() + 1).padStart(2, '0');
                const yyyy = date.getFullYear();
                const hh = String(date.getHours()).padStart(2, '0');
                const min = String(date.getMinutes()).padStart(2, '0');
                const ss = String(date.getSeconds()).padStart(2, '0');
                
                return `${dd}/${mm}/${yyyy} ${hh}:${min}:${ss}`;
            }
        }
        
        // Fallback: return original timestamp
        return timestamp;
    } catch (error) {
        console.error('Error formatting timestamp:', error);
        return timestamp;
    }
}

// Define headers
const timestampHeader = `
    <tr>
        <th style="width: 20%; text-align: left;">Run Timestamp</th>
        <th style="width: 12%; text-align: center;">Status</th>
        <th style="width: 25%; text-align: center;">Summary (Total) Passed/Failed</th>
        <th style="width: 12%; text-align: center;">Pass Rate</th>
        <th style="width: 31%; text-align: center;">Reports & Actions</th>
    </tr>
`;
const featureHeader = `
    <tr>
        <th style="width: 50%; text-align: left;">Feature Name</th>
        <th style="width: 20%; text-align: center;">Latest Status</th>
        <th style="width: 15%; text-align: center;">Total Runs</th>
        <th style="width: 15%; text-align: center;">Latest Pass Rate</th>
    </tr>
`;

// Define column groups to enforce widths
const timestampColgroup = `
    <colgroup>
        <col style="width: 20%;">
        <col style="width: 12%;">
        <col style="width: 25%;">
        <col style="width: 12%;">
        <col style="width: 31%;">
    </colgroup>
`;
const featureColgroup = `
    <colgroup>
        <col style="width: 50%;">
        <col style="width: 20%;">
        <col style="width: 15%;">
        <col style="width: 15%;">
    </colgroup>
`;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    const exportBtn = document.getElementById('exportPdfBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', showExportModal);
    }
    const exportModal = document.getElementById('exportPdfModal');
    const exportForm = document.getElementById('exportPdfForm');
    const exportSubmitBtn = document.getElementById('exportPdfSubmitBtn');
    if (exportSubmitBtn) {
        exportSubmitBtn.addEventListener('click', handleExportRequest);
    }
    // Show/hide date range and feature list fields
    if (exportForm) {
        exportForm.scope.forEach(radio => {
            radio.addEventListener('change', function() {
                document.getElementById('dateRangeFields').style.display = (this.value === 'date_range') ? 'block' : 'none';
                document.getElementById('featureListFields').style.display = (this.value === 'features') ? 'block' : 'none';
            });
        });
    }
});

// Initialize dashboard
async function initializeDashboard() {
    // Load data from the API
    await loadDashboardData();
    
    // Initialize pie chart
    initializePieChart();
    
    // Render dashboard
    renderDashboard();
}

// Setup event listeners
function setupEventListeners() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const mainTableHeader = document.getElementById('main-table-header');

    // Function to update header and colgroup
    const updateHeader = (tabName) => {
        if (tabName === 'timestamp') {
            mainTableHeader.innerHTML = timestampColgroup + `<thead id="main-thead">${timestampHeader}</thead>`;
        } else if (tabName === 'feature') {
            mainTableHeader.innerHTML = featureColgroup + `<thead id="main-thead">${featureHeader}</thead>`;
        }
    };
    
    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');

            // Deactivate all tabs and buttons
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            tabButtons.forEach(btn => btn.classList.remove('active'));

            // Activate the selected tab and button
            document.getElementById(`tab-${tabName}`).classList.add('active');
            button.classList.add('active');
            
            // Update the table header
            updateHeader(tabName);

            // Clear search input on tab switch
            document.getElementById('mainSearchInput').value = '';
            filterAccordionTable('', `${tabName}-table-body`); // Clear any existing filter
        });
    });
    
    // Search functionality for the single search input
    const mainSearchInput = document.getElementById('mainSearchInput');
    if (mainSearchInput) {
        mainSearchInput.addEventListener('input', (e) => {
            const activeTab = document.querySelector('.tab-btn.active').getAttribute('data-tab');
            filterAccordionTable(e.target.value, `${activeTab}-table-body`);
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('detailModal');
        if (event.target === modal) {
            closeModal();
        }
    });

    // Export PDF button event listener
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', showExportModal);
    }

    // Robot Report button event listener
    const robotReportBtn = document.getElementById('robotReportBtn');
    if (robotReportBtn) {
        robotReportBtn.addEventListener('click', function() {
            // Open the latest robot report if available
            if (testData && testData.length > 0) {
                const latestRun = testData[0]; // Get the most recent run
                const cleanTimestamp = latestRun.timestamp.trim();
                const reportFilename = `report-${cleanTimestamp.replace(/_/g, '-')}.html`;
                const reportUrl = `/results/${cleanTimestamp}/${reportFilename}`;
                
                console.log('Attempting to open robot report:', reportUrl);
                window.open(reportUrl, '_blank');
            } else {
                alert('No robot report available. Please run tests first.');
            }
        });
    }

    // Set initial header
    updateHeader('timestamp');
}

// Load dashboard data from the Flask API
async function loadDashboardData() {
    try {
        const response = await fetch('/api/data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Update to use new API structure
        testData = data.runs || [];
        
        // Calculate currentData from the latest run (first in sorted array)
        if (testData.length > 0) {
            const latestRun = testData[0];
            currentData = {
                total: latestRun.features.reduce((sum, f) => sum + (f.total || 0), 0),
                passed: latestRun.features.reduce((sum, f) => sum + (f.passed || 0), 0),
                failed: latestRun.features.reduce((sum, f) => sum + (f.failed || 0), 0),
                timestamp: latestRun.timestamp,
                features: latestRun.features
            };
            
            // Calculate overall status and pass rate
            currentData.pass_rate = currentData.total > 0 ? parseFloat(((currentData.passed / currentData.total) * 100).toFixed(2)) : 0;
            currentData.status = currentData.failed > 0 ? 'failed' : (currentData.total > 0 ? 'passed' : 'not_run');
            
            // Add calculated fields to each run for compatibility
            testData.forEach(run => {
                run.total = run.features.reduce((sum, f) => sum + (f.total || 0), 0);
                run.passed = run.features.reduce((sum, f) => sum + (f.passed || 0), 0);
                run.failed = run.features.reduce((sum, f) => sum + (f.failed || 0), 0);
                run.pass_rate = run.total > 0 ? parseFloat(((run.passed / run.total) * 100).toFixed(2)) : 0;
                run.status = run.failed > 0 ? 'failed' : (run.total > 0 ? 'passed' : 'not_run');
            });
        } else {
            currentData = null;
        }
        
        console.log('Successfully loaded data from API:', data);
        console.log('Processed testData:', testData);
        console.log('Processed currentData:', currentData);

    } catch (error) {
        console.error("Failed to load dashboard data:", error);
        // show error state on the dashboard
        showEmptyState("<h3>Failed to load test data</h3><p>Could not fetch data from the server. Please check the server logs and try again.</p>");
    }
}

// Initialize pie chart
function initializePieChart() {
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;
    
    if (pieChart) {
        pieChart.destroy();
    }
    
    pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Passed', 'Failed'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#28a745', '#dc3545'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label;
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

// Render dashboard with current data
function renderDashboard() {
    if (!currentData) {
        showEmptyState();
        return;
    }
    
    // Update summary cards
    updateSummaryCards();
    
    // Update pie chart
    updatePieChart();
    
    // Render latest run info
    renderLatestRunInfo();
    
    // Render new accordion tables
    renderTimestampAccordion();
    renderFeatureAccordion();
}

// Show empty state when no data
function showEmptyState(message = null) {
    const container = document.getElementById('featuresContainer');
    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                ${message || '📊 No Test Data Available'}
                <p>No test results found. Please run your test automation scripts first.</p>
            </div>
        `;
    }
    
    // Clear summary cards
    document.getElementById('total-tests').textContent = '0';
    document.getElementById('passed-tests').textContent = '0';
    document.getElementById('failed-tests').textContent = '0';
    document.getElementById('pass-rate').textContent = '0%';
}

// Update summary cards
function updateSummaryCards() {
    if (!currentData) return;
    
    document.getElementById('total-tests').textContent = currentData.total || 0;
    document.getElementById('passed-tests').textContent = currentData.passed || 0;
    document.getElementById('failed-tests').textContent = currentData.failed || 0;
    
    const passRate = currentData.pass_rate || currentData.passRate || 0;
    document.getElementById('pass-rate').textContent = passRate.toFixed(2) + '%';
}

// Update pie chart
function updatePieChart() {
    if (!currentData || !pieChart) return;
    
    const passed = currentData.passed || 0;
    const failed = currentData.failed || 0;
    
    pieChart.data.datasets[0].data = [passed, failed];
    pieChart.update();
}

// Render Timestamp Accordion (Tab 1)
function renderTimestampAccordion() {
    const table = document.getElementById('timestamp-table');
    const tbody = document.getElementById('timestamp-table-body');
    if (!tbody || !table) return;

    if (!testData || testData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><p>No test history available</p></div></td></tr>`;
        return;
    }
    
    // Set the column structure first
    table.innerHTML = timestampColgroup;
    
    let html = '';
    testData.forEach((run, runIndex) => {
        const statusClass = run.status === 'passed' ? 'status-passed' : 
                           run.status === 'not_run' ? 'status-not-run' : 'status-failed';
        const statusText = run.status === 'passed' ? 'PASSED' : 
                          run.status === 'not_run' ? 'NOT RUN' : 'FAILED';
        const passRate = run.pass_rate || run.passRate || 0;
        const cleanTimestamp = run.timestamp.trim(); // Remove any leading/trailing whitespace

        // Create the correct report filename, e.g., report-20250516-161132.html
        const reportFilename = `report-${cleanTimestamp.replace(/_/g, '-')}.html`;

        // Parent Row
        html += `
            <tr class="accordion-header" data-run-index="${runIndex}">
                <td style="text-align: left;"><span class="chevron">▶</span>${formatTimestamp(cleanTimestamp)}</td>
                <td style="text-align: center;"><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td style="text-align: center; font-weight: bold;">(<span style="color: #8B4513;">${run.total}</span>) <span style="color: #28a745;">${run.passed}</span>/<span style="color: #dc3545;">${run.failed}</span></td>
                <td style="text-align: center; font-weight: bold;">${passRate.toFixed(2)}%</td>
                <td style="text-align: center; white-space: nowrap;">
                    <button class="btn btn-primary" onclick="exportRunPDF('${cleanTimestamp}')" style="margin-right: 8px; display: inline-block;">📄 Export PDF</button>
                    <a href="/results/${cleanTimestamp}/${reportFilename}" target="_blank" class="btn btn-secondary" style="display: inline-block;">🤖 Robot Report</a>
                </td>
            </tr>
        `;

        // Child Row (Sub-table)
        html += `<tr class="accordion-body"><td colspan="5">`;
        if (run.features && run.features.length > 0) {
            html += `<table class="sub-table"><thead><tr>
                        <th style="text-align: left;">Feature Name</th>
                        <th style="text-align: center;">Status</th>
                        <th style="text-align: center;">Summary (Total) Passed/Failed</th>
                        <th style="text-align: center;">Pass Rate</th>
                        <th style="text-align: center;">Actions</th>
                    </tr></thead><tbody>`;
            run.features.forEach((feature, featureIndex) => {
                const featureStatusClass = feature.status === 'passed' ? 'status-passed' : 
                                          feature.status === 'not_run' ? 'status-not-run' : 'status-failed';
                const featureStatusText = feature.status === 'passed' ? 'PASSED' : 
                                         feature.status === 'not_run' ? 'NOT RUN' : 'FAILED';
                const featurePassRate = feature.total > 0 ? ((feature.passed / feature.total) * 100).toFixed(2) : 0;
                html += `
                    <tr>
                        <td style="text-align: left;">${feature.feature_name}</td>
                        <td style="text-align: center;"><span class="status-badge ${featureStatusClass}">${featureStatusText}</span></td>
                        <td style="text-align: center; font-weight: bold;">(<span style="color: #8B4513;">${feature.total}</span>) <span style="color: #28a745;">${feature.passed}</span>/<span style="color: #dc3545;">${feature.failed}</span></td>
                        <td style="text-align: center; font-weight: bold;">${featurePassRate}%</td>
                        <td style="text-align: center;">
                            <button class="btn btn-primary" onclick="viewFeatureDetailsInRunAsync(${runIndex}, ${featureIndex})">
                                👁️ View Details
                            </button>
                        </td>
                    </tr>
                `;
            });
            html += `</tbody></table>`;
        } else {
            html += `<div class="empty-state" style="padding: 20px;">No feature data for this run.</div>`;
        }
        html += `</td></tr>`;
    });

    const newTbody = document.createElement('tbody');
    newTbody.id = 'timestamp-table-body';
    newTbody.innerHTML = html;
    table.appendChild(newTbody);

    addAccordionListeners(newTbody);
}

// Group data by feature for Tab 2
function groupByFeature(data) {
    const featureGroups = {};

    data.forEach(run => {
        if (!run.features) return;
        run.features.forEach(feature => {
            if (!featureGroups[feature.feature_name]) {
                featureGroups[feature.feature_name] = {
                    name: feature.feature_name,
                    history: [],
                };
            }
            featureGroups[feature.feature_name].history.push({
                ...feature,
                timestamp: run.timestamp,
                run_id: run.id,
                // store original run and feature index for modal
                runIndex: testData.indexOf(run),
                featureIndex: run.features.indexOf(feature),
            });
        });
    });

    // Convert to array and add latest status/stats
    return Object.values(featureGroups).map(group => {
        const latestRun = group.history[0]; // Assumes data is sorted newest to oldest
        group.latestStatus = latestRun.status;
        group.totalRuns = group.history.length;
        group.latestPassRate = latestRun.total > 0 ? parseFloat(((latestRun.passed / latestRun.total) * 100).toFixed(2)) : 0;
        return group;
    });
}


// Render Feature Accordion (Tab 2)
function renderFeatureAccordion() {
    const table = document.getElementById('feature-table');
    const tbody = document.getElementById('feature-table-body');
    if (!tbody || !table) return;

    const features = groupByFeature(testData);

    if (Object.keys(features).length === 0) {
        tbody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><p>No feature data available</p></div></td></tr>`;
        return;
    }
    
    // Set the column structure first
    table.innerHTML = featureColgroup;

    let html = '';
    Object.values(features).forEach((feature, featureIndex) => {
        const latestRun = feature.history[0]; // Most recent run for this feature
        const latestStatusClass = latestRun.status === 'passed' ? 'status-passed' : 
                                 latestRun.status === 'not_run' ? 'status-not-run' : 'status-failed';
        const latestStatusText = latestRun.status === 'passed' ? 'PASSED' : 
                                latestRun.status === 'not_run' ? 'NOT RUN' : 'FAILED';
        
        // Parent Row
        html += `
            <tr class="accordion-header" data-feature-name="${feature.name}">
                <td style="text-align: left;"><span class="chevron">▶</span>${feature.name}</td>
                <td style="text-align: center;"><span class="status-badge ${latestStatusClass}">${latestStatusText}</span></td>
                <td style="text-align: center;">${feature.totalRuns}</td>
                <td style="text-align: center; font-weight: bold;">${feature.latestPassRate.toFixed(2)}%</td>
            </tr>
        `;

        // Child Row (Sub-table)
        html += `<tr class="accordion-body"><td colspan="4">
                    <table class="sub-table"><thead><tr>
                        <th style="text-align: left;">Run Timestamp</th>
                        <th style="text-align: center;">Status</th>
                        <th style="text-align: center;">Summary (Total) Passed/Failed</th>
                        <th style="text-align: center;">Pass Rate</th>
                        <th style="text-align: center;">Actions</th>
                    </tr></thead><tbody>`;
        
        feature.history.forEach(featureRun => {
            const featureStatusClass = featureRun.status === 'passed' ? 'status-passed' : 
                                      featureRun.status === 'not_run' ? 'status-not-run' : 'status-failed';
            const featureStatusText = featureRun.status === 'passed' ? 'PASSED' : 
                                     featureRun.status === 'not_run' ? 'NOT RUN' : 'FAILED';
            const featureRunPassRate = featureRun.total > 0 ? ((featureRun.passed / featureRun.total) * 100).toFixed(2) : 0;
            html += `
                <tr>
                    <td style="text-align: left;">${formatTimestamp(featureRun.timestamp)}</td>
                    <td style="text-align: center;"><span class="status-badge ${featureStatusClass}">${featureStatusText}</span></td>
                    <td style="text-align: center; font-weight: bold;">(<span style="color: #8B4513;">${featureRun.total}</span>) <span style="color: #28a745;">${featureRun.passed}</span>/<span style="color: #dc3545;">${featureRun.failed}</span></td>
                    <td style="text-align: center; font-weight: bold;">${featureRunPassRate}%</td>
                    <td style="text-align: center;">
                        <button class="btn btn-primary" onclick="viewFeatureDetailsInRunAsync(${featureRun.runIndex}, ${featureRun.featureIndex})">
                            👁️ View Details
                        </button>
                    </td>
                </tr>
            `;
        });
        html += `</tbody></table></td></tr>`;
    });
    
    const newTbody = document.createElement('tbody');
    newTbody.id = 'feature-table-body';
    newTbody.innerHTML = html;
    table.appendChild(newTbody);

    addAccordionListeners(newTbody);
}


// Generic function to add accordion click listeners
function addAccordionListeners(tbody) {
    tbody.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            header.classList.toggle('open');
            const body = header.nextElementSibling;
            if (body.style.display === "table-row") {
                body.style.display = "none";
            } else {
                body.style.display = "table-row";
            }
        });
    });
}

// Filter accordion table based on search input
function filterAccordionTable(searchTerm, tbodyId) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;

    const term = searchTerm.toLowerCase();
    
    // Get all parent rows
    const rows = tbody.querySelectorAll('.accordion-header');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        // Hide both parent and child row if no match
        const bodyRow = row.nextElementSibling;
        const isMatch = text.includes(term);
        
        row.style.display = isMatch ? '' : 'none';
        // Also hide the child row if parent is hidden
        if (bodyRow) {
             bodyRow.style.display = isMatch ? (row.classList.contains('open') ? 'table-row' : 'none') : 'none';
        }
    });
}

// View test run details (modified to be feature-specific)
async function viewFeatureDetailsInRun(runIndex, featureIndex) {
    const run = testData[runIndex];
    if (!run || !run.features || !run.features[featureIndex]) return;

    const feature = run.features[featureIndex];
    const modal = document.getElementById('detailModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = `Feature Details: ${feature.feature_name} (${formatTimestamp(run.timestamp)})`;
    
    const passRate = feature.total > 0 ? ((feature.passed / feature.total) * 100).toFixed(2) : 0;
    const statusClass = feature.status === 'passed' ? 'status-passed' : 
                       feature.status === 'not_run' ? 'status-not-run' : 'status-failed';
    const statusText = feature.status === 'passed' ? 'PASSED' : 
                      feature.status === 'not_run' ? 'NOT RUN' : 'FAILED';
    
    // --- Gallery ID ---
    const galleryId = `gallery-${runIndex}-${featureIndex}`;

    // --- Excel Preview HTML ---
    const excelPreviewId = `excel-preview-${runIndex}-${featureIndex}`;
    let excelSectionHtml = `
        <div class="excel-section">
            <h4>Test Data & Results File</h4>
            <p>${feature.excel_path.split('/').pop()}</p>
            <button class="btn btn-secondary" onclick="previewExcel('${feature.excel_path}', '${excelPreviewId}')">📄 Preview</button>
            <a href="/results/${feature.excel_path.replace(/^results[\\/]/, '')}" download class="btn btn-primary">⬇️ Download</a>
            <div id="${excelPreviewId}" class="excel-preview-container mt-20"></div>
        </div>
    `;

    // Get test case details with pass/fail status
    const testCaseDetails = await getTestCaseDetails(feature.excel_path);
    
    // --- Final Modal HTML ---
    modalBody.innerHTML = `
        <div class="mb-20">
            <div class="modal-header-section">
                <h3>Feature Summary <span class="status-badge feature-summary-badge ${statusClass}">${statusText}</span></h3>
            </div>
            <div class="feature-stats">
                <span class="stat-total">📊 Total: <strong>${feature.total}</strong></span>
                <span class="stat-passed">✅ Passed: <strong>${feature.passed}</strong></span>
                <span class="stat-failed">❌ Failed: <strong>${feature.failed}</strong></span>
                <span class="stat-rate">📈 Pass Rate: <strong>${passRate}%</strong></span>
            </div>
        </div>

        <div class="mb-20">
            <h3>📄 Excel Report</h3>
            ${excelSectionHtml}
        </div>
        
        <div class="mb-20">
            <h3>📸 TEST EVIDENCE SCREENSHOTS</h3>
            <div class="feature-label-large"><strong>Feature:</strong> ${feature.feature_name}</div>
            ${await generateTestCaseGallery(feature, testCaseDetails, galleryId)}
        </div>
    `;
    
    modal.style.display = 'block';

    // Initialize separate LightGallery instances for each test case
    initializeTestCaseGalleries(galleryId);
}

// Function to get test case details with pass/fail status
async function getTestCaseDetails(excelPath) {
    try {
        const response = await fetch(`/api/excel_preview?path=${encodeURIComponent(excelPath)}`);
        if (!response.ok) return {};
        
        const data = await response.json();
        if (!data.headers || !data.rows) return {};
        
        const testCaseDetails = {};
        
        // Find relevant columns
        const idColumns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo'];
        const statusColumns = ['TestResult', 'Status', 'Result'];
        const executeColumns = ['Execute'];
        
        const idCol = data.headers.find(h => idColumns.includes(h));
        const statusCol = data.headers.find(h => statusColumns.includes(h));
        const executeCol = data.headers.find(h => executeColumns.includes(h));
        
        if (!idCol || !statusCol) return {};
        
        // Process each row
        data.rows.forEach(row => {
            const testCaseId = row[idCol];
            const status = row[statusCol];
            const execute = row[executeCol];
            
            // Only include test cases with Execute = 'Y'
            if (execute && execute.toString().toLowerCase() === 'y' && testCaseId) {
                testCaseDetails[testCaseId] = {
                    status: status ? status.toString().toLowerCase() : 'unknown',
                    execute: true
                };
            }
        });
        
        return testCaseDetails;
    } catch (error) {
        console.error('Error getting test case details:', error);
        return {};
    }
}



// Function to get Excel data once
async function getExcelData(excelPath) {
    try {
        const response = await fetch(`/api/excel_preview?path=${encodeURIComponent(excelPath)}`);
        if (!response.ok) return null;
        
        const data = await response.json();
        if (!data.headers || !data.rows) return null;
        
        return data;
    } catch (error) {
        console.error('Error getting Excel data:', error);
        return null;
    }
}

// Function to get description from Excel data
function getDescriptionFromExcelData(excelData, testCaseId) {
    if (!excelData) return null;
    
    // Find relevant columns
    const idColumns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo'];
    const descColumns = ['TestCaseDescription', 'Test Case Description', 'Description', 'Name'];
    
    const idCol = excelData.headers.find(h => idColumns.includes(h));
    const descCol = excelData.headers.find(h => descColumns.includes(h));
    
    if (!idCol || !descCol) return null;
    
    // Find matching row
    const matchingRow = excelData.rows.find(row => {
        const rowId = row[idCol];
        return rowId && (rowId.toString() === testCaseId.toString() || 
                       testCaseId.startsWith(rowId.toString() + '_'));
    });
    
    if (matchingRow && matchingRow[descCol]) {
        return matchingRow[descCol].toString().trim();
    }
    
    return null;
}

// Function to get error message from Excel data
function getErrorFromExcelData(excelData, testCaseId) {
    if (!excelData) return null;
    
    // Find relevant columns
    const idColumns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo'];
    const errorColumns = ['Fail_Description', 'TestResult_Description', 'Error', 'Failure Reason', 'Error Message'];
    
    const idCol = excelData.headers.find(h => idColumns.includes(h));
    const errorCol = excelData.headers.find(h => errorColumns.includes(h));
    
    if (!idCol || !errorCol) return null;
    
    // Find matching row
    const matchingRow = excelData.rows.find(row => {
        const rowId = row[idCol];
        return rowId && (rowId.toString() === testCaseId.toString() || 
                       testCaseId.startsWith(rowId.toString() + '_'));
    });
    
    if (matchingRow && matchingRow[errorCol]) {
        const errorMsg = matchingRow[errorCol].toString().trim();
        return errorMsg !== '' ? errorMsg : null;
    }
    
    return null;
}

// Function to generate test case gallery with pass/fail status
async function generateTestCaseGallery(feature, testCaseDetails, galleryId) {
    // Get Excel data once for descriptions and error messages
    const excelData = await getExcelData(feature.excel_path);
    
    let html = `<div id="${galleryId}">`;
    let testCaseIndex = 0;
    
    // Loop through Excel test cases instead of screenshot folders
    for (const [excelTestCaseId, testCaseDetail] of Object.entries(testCaseDetails)) {
        // Only show test cases that have Execute = Y
        if (!testCaseDetail || !testCaseDetail.execute) {
            continue;
        }
        
        // Get status and create status badge
        const status = testCaseDetail.status;
        let statusBadge = '';
        if (status === 'pass') {
            statusBadge = '<span class="status-badge test-case-badge status-passed">PASSED</span>';
        } else if (status === 'fail') {
            statusBadge = '<span class="status-badge test-case-badge status-failed">FAILED</span>';
        } else {
            statusBadge = '<span class="status-badge test-case-badge" style="background: linear-gradient(135deg, #999 0%, #777 100%); color: white; box-shadow: 0 4px 15px rgba(153, 153, 153, 0.4);">UNKNOWN</span>';
        }
        
        // Get test case description and error message from Excel data
        const testCaseDescription = getDescriptionFromExcelData(excelData, excelTestCaseId);
        const errorMessage = status === 'fail' ? getErrorFromExcelData(excelData, excelTestCaseId) : null;
        
        // Add test case header with status
        html += `
            <div class="test-case-header">
                <div class="test-case-title-group">
                    <span class="test-case-title">Test Case: ${excelTestCaseId}</span>
                    ${statusBadge}
                </div>
            </div>
        `;
        
        // Add description if available
        if (testCaseDescription) {
            html += `<div class="test-case-description"><strong>Description:</strong> ${testCaseDescription}</div>`;
        }
        
        // Add error message if failed
        if (errorMessage) {
            html += `<div class="test-case-error"><div class="test-case-error-title">❌ Failure Reason:</div>${errorMessage}</div>`;
        }
        
        // Create unique gallery ID for this specific test case
        const testCaseGalleryId = `${galleryId}-testcase-${testCaseIndex}`;
        
        // Find matching screenshot folder for this Excel test case
        let matchingImages = [];
        let actualFolderName = excelTestCaseId;
        
        if (feature.test_evidence && Object.keys(feature.test_evidence).length > 0) {
            // Try exact match first
            if (feature.test_evidence[excelTestCaseId]) {
                matchingImages = feature.test_evidence[excelTestCaseId];
                actualFolderName = excelTestCaseId;
            } else {
                // Try fuzzy matching: find folders that start with excelTestCaseId + "_"
                // e.g., "TC001" matches folder "TC001_52224444444"
                for (const [folderName, folderImages] of Object.entries(feature.test_evidence)) {
                    if (folderName.startsWith(excelTestCaseId + '_') || folderName === excelTestCaseId) {
                        matchingImages = folderImages;
                        actualFolderName = folderName;
                        break;
                    }
                }
            }
        }
        
        // Grid for images of this test case
        if (matchingImages && matchingImages.length > 0) {
            // Filter out files with "PDF" in the filename (case insensitive)
            const filteredImages = matchingImages.filter(imgPath => {
                // Check if imgPath is valid
                if (!imgPath || typeof imgPath !== 'string' || imgPath.trim() === '') {
                    console.warn('[DEBUG] Invalid imgPath in test evidence:', imgPath);
                    return false; // Remove invalid paths
                }
                const imgFileName = imgPath.split('/').pop();
                return !imgFileName.toUpperCase().includes('PDF');
            });
            
            if (filteredImages.length > 0) {
                const maxPreviewImages = 3; // แสดง 3 รูปแรก
                const previewImages = filteredImages.slice(0, maxPreviewImages);
            
                html += `<div class="features-grid test-case-gallery" data-gallery-id="${testCaseGalleryId}">`;
                
                // Show preview images
                previewImages.forEach(imgPath => {
                    // Validate imgPath before using
                    if (!imgPath || typeof imgPath !== 'string' || imgPath.trim() === '') {
                        console.warn('[DEBUG] Invalid imgPath detected:', imgPath);
                        return; // Skip this image
                    }
                    
                    const imgFileName = imgPath.split('/').pop();
                    // Fix image path for serving
                    let fixedPath = imgPath;
                    if (!imgPath.startsWith('/results/')) {
                        if (imgPath.startsWith('results/')) {
                            fixedPath = '/' + imgPath;
                        } else {
                            fixedPath = '/results/' + imgPath;
                        }
                    }
                    
                    html += `
                        <a href="${fixedPath}" data-lg-size="1600-1200" class="gallery-item" data-sub-html="<h4>${imgFileName}</h4><p>Test Case: ${excelTestCaseId} (${status.toUpperCase()})</p>">
                            <img src="${fixedPath}" alt="Test Evidence for ${excelTestCaseId}: ${imgFileName}" />
                            <div class="gallery-item-info">
                                <span>${imgFileName}</span>
                                <br><small>Test Case: ${excelTestCaseId}</small>
                            </div>
                        </a>
                    `;
                });
                
                // Add "ดูรูปเพิ่มเติม" button if there are more than 4 images
                if (filteredImages.length > 4) {
                    // Ensure filteredImages are all valid before stringifying
                    const safeImages = filteredImages.filter(img => img && typeof img === 'string' && img.trim() !== '');
                    console.log('[DEBUG] Safe images for more button:', safeImages.length, 'out of', filteredImages.length);
                    
                    html += `
                        <button class="btn btn-secondary"
                            data-testcase-name="${excelTestCaseId}"
                            data-status="${status}"
                            data-images='${JSON.stringify(safeImages)}'
                            onclick="openAllImagesFromData(this)">
                            ดูรูปเพิ่มเติม
                        </button>
                    `;
                }
                
                html += '</div>';
            } else {
                html += '<div class="features-grid test-case-gallery" data-gallery-id="${testCaseGalleryId}">';
                html += '<div class="no-screenshot-placeholder">No screenshot found</div>';
                html += '</div>';
            }
        } else {
            // No matching screenshot folder found - show "No screenshot found"
            html += '<div class="features-grid test-case-gallery" data-gallery-id="${testCaseGalleryId}">';
            html += '<div class="no-screenshot-placeholder">No screenshot found</div>';
            html += '</div>';
        }
        
        testCaseIndex++;
    }
    
    html += '</div>';
    return html;
}

// Function to preview/hide Excel file content (toggle)
async function previewExcel(excelPath, targetElementId) {
    const targetDiv = document.getElementById(targetElementId);
    const btn = document.querySelector(`[onclick*="previewExcel('${excelPath}', '${targetElementId}')"]`);
    if (!targetDiv) return;
    // Toggle: if already shown, hide
    if (targetDiv.style.display === 'block' || targetDiv.innerHTML.trim() !== '') {
        targetDiv.innerHTML = '';
        targetDiv.style.display = 'none';
        if (btn) btn.textContent = '📄 Preview';
        return;
    }
    // Show preview
    targetDiv.innerHTML = '<div class="loading"></div><p>Loading preview...</p>';
    targetDiv.style.display = 'block';
    if (btn) btn.textContent = '✖ Hide Preview';
    try {
        const response = await fetch(`/api/excel_preview?path=${encodeURIComponent(excelPath)}`);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to load preview: ${errorText}`);
        }
        const data = await response.json();
        if (!data.headers || !data.rows || data.rows.length === 0) {
            targetDiv.innerHTML = '<p>No data to display in this file.</p>';
            return;
        }
        
        // Define the columns we want to show based on the example file
        const allowedColumns = ['TestCaseNo', 'Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCaseNo', 'TestCase', 'Execute', 'Module/Feature', 'TestCaseDescription', 'TestResult', 'Fail_Description', 'ExpectedResult'];
        
        // Filter headers to only include allowed columns that exist in the data
        const filteredHeaders = data.headers.filter(header => allowedColumns.includes(header));
        
        // Filter rows to exclude those with Execute == "N" or empty Execute
        const filteredRows = data.rows.filter(row => {
            const executeValue = row['Execute'] || row['execute'] || '';
            return executeValue.toString().trim().toUpperCase() !== 'N' && executeValue.toString().trim() !== '';
        });
        
        let tableHtml = '<div class="table-container"><table class="excel-preview-table"><thead><tr>';
        filteredHeaders.forEach(header => {
            tableHtml += `<th>${header}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
        filteredRows.forEach(row => {
            tableHtml += '<tr>';
            filteredHeaders.forEach(header => {
                const cellValue = row[header] || '';
                tableHtml += `<td>${cellValue}</td>`;
            });
            tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table></div>';
        targetDiv.innerHTML = tableHtml;
    } catch (error) {
        targetDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        console.error("Excel preview error:", error);
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('detailModal');
    if (modal) {
        modal.style.display = 'none';
    }

    // Destroy the active lightgallery instance to prevent issues
    if (activeGallery) {
        activeGallery.destroy();
        activeGallery = null;
    }
}

// Export PDF for specific run
async function exportRunPDF(timestamp) {
    try {
        // Find the specific run based on timestamp
        const targetRun = testData.find(run => run.timestamp === timestamp);
        if (!targetRun) {
            alert('Run not found!');
            return;
        }

        // Get all feature names from this run
        const runFeatures = targetRun.features.map(f => f.feature_name);
        
        // Use date_range scope with specific timestamp to ensure only this run is included
        const options = {
            scope: 'date_range',
            features: runFeatures,
            start_date: timestamp,
            end_date: timestamp,
            include_screenshots: true,
            include_details: true,
            include_summary: true
        };

        console.log(`Exporting PDF for specific run ${timestamp} with options:`, options);
        
        const response = await fetch('/api/export_pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(options)
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const formattedDate = formatTimestamp(timestamp).replace(/[\/\s:]/g, '_');
            downloadPDF(blob, `TestReport_${formattedDate}`);
        } else {
            const errorText = await response.text();
            console.error('PDF export failed:', response.status, errorText);
            alert(`Export failed: ${response.status} - ${errorText}`);
        }
    } catch (error) {
        console.error('PDF export error:', error);
        alert(`Export error: ${error.message}`);
    }
}

// Export functions for global access
window.viewFeatureDetailsInRun = viewFeatureDetailsInRun;
window.closeModal = closeModal;
window.previewExcel = previewExcel;
window.exportRunPDF = exportRunPDF;

// Async wrapper for global access
window.viewFeatureDetailsInRunAsync = async function(runIndex, featureIndex) {
    await viewFeatureDetailsInRun(runIndex, featureIndex);
};

function renderLatestRunInfo() {
    const infoDiv = document.getElementById('latest-run-info');
    const badgeDiv = document.getElementById('latest-status-badge');
    if (!infoDiv || !currentData) return;
    const timestamp = formatTimestamp(currentData.timestamp || '-');
    const features = (currentData.features || []).map((f, idx) => {
        const name = f.feature_name || f.name;
        return `<span class=\"feature-simple-link\" data-feature-idx=\"${idx}\">${name}</span>`;
    }).filter(Boolean);
    // Badge for test result
    const status = currentData.status === 'passed' ? 'PASSED' : 
                  currentData.status === 'not_run' ? 'NOT RUN' :
                  currentData.status === 'failed' ? 'FAILED' : 'UNKNOWN';
    const statusClass = currentData.status === 'passed' ? 'status-passed' : 
                       currentData.status === 'not_run' ? 'status-not-run' :
                       currentData.status === 'failed' ? 'status-failed' : 'status-unknown';
    
    infoDiv.innerHTML = `
        <div class="run-label">Latest Run:</div>
        <div class="run-timestamp">${timestamp}</div>
        <div class="run-features"><strong>View Details:</strong> ${features.join(', ')}</div>
    `;
    
    if (badgeDiv) {
        badgeDiv.innerHTML = `<span class="status-badge ${statusClass}">${status}</span>`;
    }
    
    // Add event listeners for feature simple links
    infoDiv.querySelectorAll('.feature-simple-link').forEach(link => {
        link.addEventListener('click', async function() {
            const idx = parseInt(this.getAttribute('data-feature-idx'));
            await viewFeatureDetailsInRun(0, idx);
        });
    });
}

// Initialize separate LightGallery instances for each test case
function initializeTestCaseGalleries(galleryId) {
    const mainGallery = document.getElementById(galleryId);
    if (!mainGallery) return;
    
    // Find all test case galleries within this main gallery
    const testCaseGalleries = mainGallery.querySelectorAll('.test-case-gallery');
    
    testCaseGalleries.forEach(galleryElement => {
        if (galleryElement) {
            // Initialize separate LightGallery for each test case
            lightGallery(galleryElement, {
                plugins: [window.lgZoom, window.lgFullscreen],
                speed: 800,                 // เพิ่มความเร็วจาก 500ms เป็น 800ms (ช้าลง)
                scale: 1.5,
                actualSize: true,
                download: true,
                counter: true,
                selector: '.gallery-item',
                appendSubHtmlTo: '.lg-item',
                backdropDuration: 500, // เพิ่ม backdrop duration ด้วย
                // ปรับความเร็วสำหรับ touch/swipe บนมือถือ
                swipeThreshold: 50, // ต้องเลื่อนไกลกว่าเดิมถึงจะเปลี่ยนรูป
                touchMove: true,
                enableSwipe: true,
                enableTouch: true,
                // Ensure z-index is higher than modal
                onBeforeOpen: () => {
                    setTimeout(() => {
                        const backdrop = document.querySelector('.lg-backdrop');
                        const outer = document.querySelector('.lg-outer');
                        
                        // Use base z-index 3000 for View Details modal LightGallery
                        const baseZIndex = 3000;
                        
                        if (backdrop) {
                            backdrop.style.zIndex = baseZIndex.toString();
                        }
                        if (outer) {
                            outer.style.zIndex = (baseZIndex + 1).toString();
                        }
                        
                        // Set all other LightGallery elements
                        const lgElements = [
                            { selector: '.lg-container', offset: 2 },
                            { selector: '.lg-toolbar', offset: 3 },
                            { selector: '.lg-actions', offset: 4 },
                            { selector: '.lg-prev, .lg-next, .lg-close', offset: 5 }
                        ];
                        
                        lgElements.forEach(({selector, offset}) => {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach(el => {
                                el.style.zIndex = (baseZIndex + offset).toString();
                            });
                        });
                    }, 50);
                }
            });
        }
    });
}



// --- Export PDF Logic ---
function showExportModal() {
    const modal = document.getElementById('exportPdfModal');
    if (modal) {
        modal.style.display = 'block';
    }
    // Populate feature list
    const featureCheckboxList = document.getElementById('featureCheckboxList');
    if (featureCheckboxList) {
        // Get unique feature names from all runs
        const allFeatures = testData.flatMap(run => run.features.map(f => f.feature_name));
        const uniqueFeatures = [...new Set(allFeatures)];
        if (uniqueFeatures.length > 0) {
            featureCheckboxList.innerHTML = uniqueFeatures.map(feature => `
                <label>
                    <input type="checkbox" name="selected_features" value="${feature}">
                    ${feature}
                </label><br>
            `).join('');
        } else {
            featureCheckboxList.innerHTML = 'No features found.';
        }
    }
}

function hideExportModal() {
    const modal = document.getElementById('exportPdfModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function handleExportRequest() {
    const form = document.getElementById('exportPdfForm');
    
    // Fix: Get scope value correctly
    const scopeRadio = form.querySelector('input[name="scope"]:checked');
    const scope = scopeRadio ? scopeRadio.value : 'latest';
    
    let start_date = null, end_date = null, features = [];
    if (scope === 'date_range') {
        start_date = form.start_date ? form.start_date.value : null;
        end_date = form.end_date ? form.end_date.value : null;
    }
    if (scope === 'features') {
        features = Array.from(form.querySelectorAll('input[name="selected_features"]:checked')).map(cb => cb.value);
    }
    const options = {
        scope,
        start_date,
        end_date,
        features,
        include_screenshots: form.include_screenshots.checked,
        include_details: form.include_details.checked,
        include_summary: form.include_summary.checked
    };
    // Show loading spinner on button
    const btn = document.getElementById('exportPdfSubmitBtn');
    btn.disabled = true;
    btn.textContent = 'Exporting...';
    try {
        console.log('Sending PDF export request with options:', options);
        
        const response = await fetch('/api/export_pdf', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(options)
        });
        
        console.log('PDF export response status:', response.status);
        
        if (response.ok) {
            const blob = await response.blob();
            console.log('PDF blob size:', blob.size);
            downloadPDF(blob);
            hideExportModal();
        } else {
            const errorText = await response.text();
            console.error('PDF export failed:', response.status, errorText);
            alert(`Export failed: ${response.status} - ${errorText}`);
        }
    } catch (e) {
        console.error('PDF export error:', e);
        alert(`Network error: ${e.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Export';
    }
}

function downloadPDF(blob, filename = null) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename ? `${filename}.pdf` : `test_report_${new Date().toISOString().replace(/[:.]/g, '-')}.pdf`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }, 100);
}

// Helper function to open all images modal from data attributes
function openAllImagesFromData(element) {
    try {
        console.log('[DEBUG] openAllImagesFromData called');
        
        const testCaseName = element.getAttribute('data-testcase-name');
        const status = element.getAttribute('data-status');
        const imagesJson = element.getAttribute('data-images');
        
        console.log('[DEBUG] Raw attributes:', {
            testCaseName,
            status, 
            imagesJson: imagesJson ? imagesJson.substring(0, 200) + '...' : 'null'
        });
        
        if (!testCaseName || !status || !imagesJson) {
            console.error('Missing required data attributes:', {testCaseName, status, hasImages: !!imagesJson});
            alert('เกิดข้อผิดพลาด: ข้อมูลไม่ครบถ้วน');
            return;
        }
        
        let images;
        try {
            images = JSON.parse(imagesJson);
            console.log('[DEBUG] Successfully parsed images:', images);
        } catch (parseError) {
            console.error('[DEBUG] JSON parse error:', parseError);
            console.error('[DEBUG] Raw JSON string:', imagesJson);
            alert('เกิดข้อผิดพลาดในการอ่านข้อมูลรูปภาพ');
            return;
        }
        
        if (!images || !Array.isArray(images) || images.length === 0) {
            console.warn('[DEBUG] No valid images array:', images);
            alert('ไม่พบรูปภาพสำหรับ test case นี้');
            return;
        }
        
        console.log('[DEBUG] Processing', images.length, 'images...');
        
        // Validate and fix each image path
        const validImages = [];
        images.forEach((imgPath, index) => {
            console.log(`[DEBUG] Processing image ${index + 1}/${images.length}:`, imgPath);
            
            if (!imgPath || typeof imgPath !== 'string' || imgPath.trim() === '') {
                console.warn(`[DEBUG] Invalid image path at index ${index}:`, imgPath);
                return; // Skip invalid paths
            }
            
            // Fix path for serving
            let fixedPath = imgPath.trim();
            
            // Ensure proper /results/ prefix
            if (!fixedPath.startsWith('/results/')) {
                if (fixedPath.startsWith('results/')) {
                    fixedPath = '/' + fixedPath;
                } else {
                    // Handle relative paths - prepend /results/
                    fixedPath = '/results/' + fixedPath;
                }
            }
            
            console.log(`[DEBUG] Path ${index + 1} transformation:`, imgPath, '->', fixedPath);
            validImages.push(fixedPath);
        });
        
        if (validImages.length === 0) {
            console.error('[DEBUG] No valid images after processing');
            alert('ไม่มีรูปภาพที่ถูกต้องสำหรับ test case นี้');
            return;
        }
        
        console.log('[DEBUG] Final valid images count:', validImages.length);
        console.log('[DEBUG] Sample valid paths:', validImages.slice(0, 3));
        
        showAllImagesModal(testCaseName, validImages, status);
    } catch (error) {
        console.error('[DEBUG] Unexpected error in openAllImagesFromData:', error);
        console.error('[DEBUG] Error stack:', error.stack);
        alert('เกิดข้อผิดพลาดไม่คาดคิด: ' + error.message);
    }
}

// Function to show all images modal for specific test case
function showAllImagesModal(testCaseName, images, status) {
    console.log('[DEBUG] showAllImagesModal called with:', {
        testCaseName, 
        status, 
        imageCount: images.length,
        firstImage: images[0]
    });
    
    // Additional validation at modal level
    if (!images || !Array.isArray(images) || images.length === 0) {
        console.error('[DEBUG] Invalid images array passed to modal:', images);
        alert('เกิดข้อผิดพลาด: ไม่มีรูปภาพที่ถูกต้อง');
        return;
    }
    
    const modalId = 'allImagesModal';
    
    // Remove existing modal if any with thorough cleanup
    const existingModal = document.getElementById(modalId);
    if (existingModal) {
        console.log('[DEBUG] Removing existing modal');
        
        // Clean up any existing LightGallery instances first
        if (window.currentAllImagesLG) {
            try {
                window.currentAllImagesLG.destroy(true);
                window.currentAllImagesLG = null;
                console.log('[DEBUG] Cleaned up existing LG instance');
            } catch (e) {
                console.log('[DEBUG] Error cleaning up previous LG instance:', e);
            }
        }
        
        // Remove any leftover LightGallery elements
        const leftoverLG = document.querySelectorAll('.lg-backdrop, .lg-outer, .lg-container');
        leftoverLG.forEach(el => el.remove());
        
        existingModal.remove();
    }
    
    // Create new modal with forced visibility
    const modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal';
    
    // Force immediate visibility with inline styles
    modal.style.cssText = `
        display: block !important;
        position: fixed !important;
        z-index: 2000 !important;
        left: 0 !important;
        top: 0 !important;
        width: 100% !important;
        height: 100% !important;
        background-color: rgba(0,0,0,0.6) !important;
        opacity: 1 !important;
        visibility: visible !important;
    `;
    
    const statusBadge = status === 'pass' ? '<span class="status-badge status-passed">PASSED</span>' :
                       status === 'fail' ? '<span class="status-badge status-failed">FAILED</span>' :
                       '<span class="status-badge" style="background: #999; color: white;">UNKNOWN</span>';
    
    // Create simple gallery HTML without complex attributes initially
    const galleryHTML = images.map((imgPath, index) => {
        const imgFileName = imgPath.split('/').pop();
        
        return `
            <div class="gallery-item simple-gallery-item" data-index="${index}" data-src="${imgPath}">
                <img src="${imgPath}" 
                     alt="Test Evidence: ${imgFileName}" 
                     loading="lazy"
                     style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" />
                <div class="gallery-item-info">
                    <span>${imgFileName}</span>
                    <br><small>Test Case: ${testCaseName}</small>
                </div>
            </div>
        `;
    }).join('');
    
    modal.innerHTML = `
        <div class="modal-content" style="
            max-height: 90vh !important;
            overflow-y: auto !important;
            display: block !important;
            opacity: 1 !important;
            visibility: visible !important;
            background-color: white !important;
            margin: 2% auto !important;
            padding: 0 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
            width: 90vw !important;
            max-width: 1400px !important;
        ">
            <div class="modal-header" style="
                padding: 20px 25px !important;
                border-bottom: 1px solid #e5e5e5 !important;
                background-color: #f8f9fa !important;
                border-radius: 8px 8px 0 0 !important;
                position: relative !important;
            ">
                <h2 style="margin: 0; color: #333;">📸 รูปภาพทั้งหมดของ Test Case: ${testCaseName} ${statusBadge}</h2>
                <span class="close" id="closeAllImagesBtn" style="
                    position: absolute !important;
                    top: 15px !important;
                    right: 20px !important;
                    color: #aaa !important;
                    font-size: 28px !important;
                    font-weight: bold !important;
                    cursor: pointer !important;
                    z-index: 2001 !important;
                ">&times;</span>
            </div>
            <div class="modal-body" style="padding: 25px !important;">
                <div class="images-count-info" style="text-align: center; margin-bottom: 20px; color: #666; font-size: 1.1rem;">
                    จำนวนรูปทั้งหมด: ${images.length} รูป (คลิกที่รูปเพื่อดูขนาดใหญ่)
                </div>
                <div id="allImagesGallery" class="features-grid" style="
                    display: grid !important;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)) !important;
                    gap: 20px !important;
                    opacity: 1 !important;
                    visibility: visible !important;
                ">
                    ${galleryHTML}
                </div>
            </div>
        </div>
    `;
    
    console.log('[DEBUG] Adding modal to document body');
    document.body.appendChild(modal);
    
    // Force reflow to ensure modal is rendered
    modal.offsetHeight;
    
    console.log('[DEBUG] Modal added and forced visible');
    
    // Enhanced close button handling
    const closeBtn = document.getElementById('closeAllImagesBtn');
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('[DEBUG] Close button clicked');
            closeAllImagesModal();
        });
        
        // Add hover effect
        closeBtn.addEventListener('mouseenter', function() {
            this.style.color = '#000';
        });
        closeBtn.addEventListener('mouseleave', function() {
            this.style.color = '#aaa';
        });
    }
    
    // Handle escape key
    const handleEscape = (e) => {
        if (e.key === 'Escape' && document.getElementById('allImagesModal')) {
            e.preventDefault();
            closeAllImagesModal();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);
    
    // Close modal when clicking outside
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            event.preventDefault();
            event.stopPropagation();
            console.log('[DEBUG] Clicked outside modal, closing');
            closeAllImagesModal();
        }
    });
    
    // Prevent modal content clicks from bubbling up
    const modalContent = modal.querySelector('.modal-content');
    if (modalContent) {
        modalContent.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
    
    // Add immediate click handlers for images (simple new tab opening)
    const galleryItems = modal.querySelectorAll('.simple-gallery-item');
    console.log(`[DEBUG] Adding immediate click handlers to ${galleryItems.length} items`);
    
    galleryItems.forEach((item, index) => {
        const img = item.querySelector('img');
        const imgSrc = item.getAttribute('data-src');
        
        // Add immediate click handler
        item.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(`[DEBUG] Image ${index + 1} clicked, opening:`, imgSrc);
            window.open(imgSrc, '_blank');
        });
        
        // Add visual feedback
        item.style.cursor = 'pointer';
        item.style.transition = 'transform 0.2s ease';
        
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });
        
        // Add loading indicator
        if (img) {
            img.addEventListener('load', function() {
                console.log(`[DEBUG] Image ${index + 1} loaded successfully`);
                this.style.opacity = '1';
            });
            
            img.addEventListener('error', function() {
                console.error(`[DEBUG] Image ${index + 1} failed to load:`, imgSrc);
                this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4=';
                this.alt = '❌ Image not found';
            });
            
            // Set initial opacity for loading effect
            img.style.opacity = '0.7';
        }
    });
    
    console.log('[DEBUG] Modal setup completed with immediate functionality');
    
    // Optional: Try to upgrade to LightGallery later (non-blocking)
    setTimeout(() => {
        tryUpgradeToLightGallery(modal);
    }, 1000);
}

// Optional function to upgrade to LightGallery (non-blocking)
function tryUpgradeToLightGallery(modal) {
    if (!modal || !document.getElementById('allImagesModal')) {
        console.log('[DEBUG] Modal no longer exists, skipping LightGallery upgrade');
        return;
    }
    
    const galleryElement = document.getElementById('allImagesGallery');
    if (!galleryElement) {
        console.log('[DEBUG] Gallery element not found for LightGallery upgrade');
        return;
    }
    
    // Check if LightGallery is available
    if (typeof lightGallery === 'undefined') {
        console.log('[DEBUG] LightGallery not available, keeping simple handlers');
        return;
    }
    
    try {
        console.log('[DEBUG] Attempting LightGallery upgrade...');
        
        // Convert simple items to LightGallery format
        const galleryItems = galleryElement.querySelectorAll('.simple-gallery-item');
        galleryItems.forEach((item, index) => {
            const imgSrc = item.getAttribute('data-src');
            const img = item.querySelector('img');
            const fileName = imgSrc.split('/').pop();
            
            // Transform to LightGallery format
            item.setAttribute('href', imgSrc);
            item.setAttribute('data-lg-size', '1600-1200');
            item.setAttribute('data-sub-html', `<h4>${fileName}</h4>`);
            item.classList.add('lg-gallery-item');
        });
        
        // Initialize LightGallery
        const lgInstance = lightGallery(galleryElement, {
            plugins: [window.lgZoom, window.lgFullscreen],
            speed: 800,
            scale: 1.5,
            actualSize: true,
            download: true,
            counter: true,
            selector: '.lg-gallery-item',
            appendSubHtmlTo: '.lg-item',
            backdropDuration: 500,
            swipeThreshold: 50,
            touchMove: true,
            enableSwipe: true,
            enableTouch: true,
            onBeforeOpen: () => {
                setTimeout(() => {
                    // Set proper z-index for nested modal
                    const backdrop = document.querySelector('.lg-backdrop');
                    const outer = document.querySelector('.lg-outer');
                    
                    if (backdrop) backdrop.style.zIndex = '4000';
                    if (outer) outer.style.zIndex = '4001';
                    
                    // Set other elements
                    document.querySelectorAll('.lg-container').forEach(el => el.style.zIndex = '4002');
                    document.querySelectorAll('.lg-toolbar').forEach(el => el.style.zIndex = '4003');
                    document.querySelectorAll('.lg-actions').forEach(el => el.style.zIndex = '4004');
                    document.querySelectorAll('.lg-prev, .lg-next, .lg-close').forEach(el => el.style.zIndex = '4005');
                }, 50);
            }
        });
        
        // Store instance for cleanup
        galleryElement.lgInstance = lgInstance;
        window.currentAllImagesLG = lgInstance;
        
        console.log('[DEBUG] LightGallery upgrade successful');
        
        // Update instruction text
        const instructionElement = modal.querySelector('.images-count-info');
        if (instructionElement) {
            instructionElement.innerHTML = `จำนวนรูปทั้งหมด: ${galleryItems.length} รูป (คลิกที่รูปเพื่อเปิด Gallery View)`;
        }
        
    } catch (error) {
        console.log('[DEBUG] LightGallery upgrade failed, keeping simple handlers:', error);
        // Keep existing simple handlers - no problem
    }
}

// Function to close all images modal
function closeAllImagesModal() {
    console.log('[DEBUG] closeAllImagesModal called');
    
    // Destroy LightGallery instance first
    const galleryElement = document.getElementById('allImagesGallery');
    if (galleryElement) {
        try {
            // Multiple ways to destroy LightGallery
            if (window.currentAllImagesLG) {
                console.log('[DEBUG] Destroying LightGallery via global instance');
                window.currentAllImagesLG.destroy(true);
                window.currentAllImagesLG = null;
            }
            
            if (galleryElement.lgInstance) {
                console.log('[DEBUG] Destroying LightGallery via element instance');
                galleryElement.lgInstance.destroy(true);
                galleryElement.lgInstance = null;
            }
            
            // Check for lightGallery data object
            if (galleryElement.lightGallery) {
                galleryElement.lightGallery.destroy(true);
            }
            
            if (galleryElement.lgData) {
                galleryElement.lgData.destroy(true);
            }
        } catch (error) {
            console.log('[DEBUG] Error destroying LightGallery:', error);
        }
    }
    
    // Remove any leftover LightGallery elements
    const lightboxElements = document.querySelectorAll('.lg-backdrop, .lg-outer, .lg-container, .lg-thumb-outer, .lg-toolbar');
    lightboxElements.forEach(element => {
        console.log('[DEBUG] Removing leftover lightbox element:', element.className);
        element.remove();
    });
    
    // Remove the modal
    const modal = document.getElementById('allImagesModal');
    if (modal) {
        console.log('[DEBUG] Removing modal');
        modal.remove();
    }
    
    // Restore body scroll if needed
    document.body.style.overflow = '';
    
    console.log('[DEBUG] All images modal cleanup complete');
    
    // Reinitialize LightGallery instances in the main preview after a short delay
    setTimeout(() => {
        console.log('[DEBUG] Reinitializing main preview LightGallery instances');
        // Find all gallery containers in the current modal
        const detailModal = document.getElementById('detailModal');
        if (detailModal && detailModal.style.display === 'block') {
            // Find all gallery containers
            const galleryContainers = detailModal.querySelectorAll('[id^="gallery-"]');
            galleryContainers.forEach(container => {
                const galleryId = container.id;
                console.log('[DEBUG] Reinitializing gallery:', galleryId);
                initializeTestCaseGalleries(galleryId);
            });
        }
    }, 300); // Wait 300ms for cleanup to complete
}