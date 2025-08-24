// Global variables
let pieChart = null;
let testData = [];
let currentData = null;
let activeGallery = null; // To hold the active lightgallery instance
let excelPreviewState = {};

// PDF Loading Overlay Functions
function showPDFLoadingOverlay() {
    const overlay = document.getElementById('pdfLoadingOverlay');
    if (overlay) {
        overlay.classList.add('show');
        document.body.classList.add('overlay-active');
    }
}

function hidePDFLoadingOverlay() {
    const overlay = document.getElementById('pdfLoadingOverlay');
    if (overlay) {
        overlay.classList.remove('show');
        document.body.classList.remove('overlay-active');
    }
}

// Generic blocking overlay using the same PDF overlay element
function showBlockingOverlay(title, message) {
    const overlay = document.getElementById('pdfLoadingOverlay');
    if (!overlay) return;
    const titleEl = overlay.querySelector('.pdf-loading-title');
    const msgEl = overlay.querySelector('.pdf-loading-message');
    // Preserve previous texts to restore later
    if (overlay && !overlay.dataset.prevTitle && titleEl) {
        overlay.dataset.prevTitle = titleEl.textContent || '';
    }
    if (overlay && !overlay.dataset.prevMessage && msgEl) {
        overlay.dataset.prevMessage = msgEl.textContent || '';
    }
    if (titleEl && title) titleEl.textContent = title;
    if (msgEl && message) msgEl.textContent = message;
    overlay.classList.add('show');
    document.body.classList.add('overlay-active');
}

function hideBlockingOverlay() {
    const overlay = document.getElementById('pdfLoadingOverlay');
    if (!overlay) return;
    const titleEl = overlay.querySelector('.pdf-loading-title');
    const msgEl = overlay.querySelector('.pdf-loading-message');
    if (titleEl && overlay.dataset.prevTitle !== undefined) {
        titleEl.textContent = overlay.dataset.prevTitle;
    }
    if (msgEl && overlay.dataset.prevMessage !== undefined) {
        msgEl.textContent = overlay.dataset.prevMessage;
    }
    overlay.classList.remove('show');
    document.body.classList.remove('overlay-active');
    delete overlay.dataset.prevTitle;
    delete overlay.dataset.prevMessage;
}

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
        <th style="width: 25%; text-align: center;">Summary (Total) Passed/Failed Major/Failed Blocker</th>
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

    // Handle window focus to refresh thumbnails when returning from HTML tab
    window.addEventListener('focus', function() {
        console.log('[DEBUG] Window focused - checking for thumbnail refresh');
        refreshAllModalThumbnails();
    });

    // Handle page visibility change (when tab becomes visible again)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            console.log('[DEBUG] Page became visible - checking for thumbnail refresh');
            setTimeout(() => {
                refreshAllModalThumbnails();
            }, 500); // Small delay to ensure tab is fully active
        }
    });

    // Download PDF button event listener
    // Note: exportPdfBtn now uses onclick="downloadLatestPDF()" in HTML
    // No additional event listener needed

    // Robot Report button event listener
    const robotReportBtn = document.getElementById('robotReportBtn');
    if (robotReportBtn) {
        robotReportBtn.addEventListener('click', function() {
            // Use the same logic as downloadLatestRobotReport function
            if (testData && testData.length > 0) {
                const latestRun = testData[0];
                const cleanTimestamp = latestRun.timestamp.trim();
                const reportFilename = `report-${cleanTimestamp.replace(/_/g, '-')}.html`;
                const reportUrl = `/results/${cleanTimestamp}/${reportFilename}`;
                
                // Check if the report file exists before opening
                fetch(reportUrl, { method: 'HEAD' })
                    .then(response => {
                        if (response.ok) {
                            window.open(reportUrl, '_blank');
                        } else {
                            alert(`Robot report not found for run: ${cleanTimestamp}\n\nPlease check if the report file exists at:\n${reportUrl}`);
                        }
                    })
                    .catch(error => {
                        console.error('Error checking robot report:', error);
                        alert(`Error checking robot report for run: ${cleanTimestamp}\n\nPlease check if the report file exists at:\n${reportUrl}`);
                    });
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

            // Aggregate counts across features for latest run
            const aggTotal = latestRun.features.reduce((sum, f) => sum + (f.total || 0), 0);
            const aggPassed = latestRun.features.reduce((sum, f) => sum + (f.passed || 0), 0);
            const aggFailed = latestRun.features.reduce((sum, f) => sum + (f.failed || 0), 0);
            const aggFailedMajor = latestRun.features.reduce((sum, f) => sum + (f.failed_major || 0), 0);
            const aggFailedBlocker = latestRun.features.reduce((sum, f) => sum + (f.failed_blocker || 0), 0);

            currentData = {
                total: aggTotal,
                passed: aggPassed,
                failed: aggFailed,
                failed_major: aggFailedMajor,
                failed_blocker: aggFailedBlocker,
                timestamp: latestRun.timestamp,
                features: latestRun.features
            };

            // Calculate overall status and pass rate
            currentData.pass_rate = currentData.total > 0 ? parseFloat(((currentData.passed / currentData.total) * 100).toFixed(2)) : 0;
            if (currentData.total === 0) {
                currentData.status = 'not_run';
            } else if ((currentData.failed_blocker || 0) > 0) {
                currentData.status = 'failed_blocker';
            } else if ((currentData.failed_major || 0) > 0 || (currentData.failed || 0) > 0) {
                currentData.status = 'failed_major';
            } else {
                currentData.status = 'passed';
            }

            // Add calculated fields to each run for compatibility
            testData.forEach(run => {
                run.total = run.features.reduce((sum, f) => sum + (f.total || 0), 0);
                run.passed = run.features.reduce((sum, f) => sum + (f.passed || 0), 0);
                run.failed_major = run.features.reduce((sum, f) => sum + (f.failed_major || 0), 0);
                run.failed_blocker = run.features.reduce((sum, f) => sum + (f.failed_blocker || 0), 0);
                run.failed = run.features.reduce((sum, f) => sum + (f.failed || ((f.failed_major || 0) + (f.failed_blocker || 0))), 0);
                run.pass_rate = run.total > 0 ? parseFloat(((run.passed / run.total) * 100).toFixed(2)) : 0;
                if (run.total === 0) {
                    run.status = 'not_run';
                } else if ((run.failed_blocker || 0) > 0) {
                    run.status = 'failed_blocker';
                } else if ((run.failed_major || 0) > 0 || (run.failed || 0) > 0) {
                    run.status = 'failed_major';
                } else {
                    run.status = 'passed';
                }
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
            labels: ['Passed', 'FAIL (Major)', 'FAIL (Blocker)'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#28a745', '#ff5722', '#e51c23'],
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
    
    // Clear summary cards for all 5 cards
    document.getElementById('total-tests').textContent = '0';
    document.getElementById('passed-tests').textContent = '0';
    document.getElementById('failed-major-tests').textContent = '0';
    document.getElementById('failed-blocker-tests').textContent = '0';
    document.getElementById('pass-rate').textContent = '0%';
}

// Update summary cards
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

// Update pie chart
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
        // Determine status class and text based on failure types
        let statusClass, statusText;
        if (run.status === 'passed') {
            statusClass = 'status-passed';
            statusText = 'PASS';
        } else if (run.status === 'not_run') {
            statusClass = 'status-not-run';
            statusText = 'NOT RUN';
        } else if (run.status === 'failed_blocker') {
            statusClass = 'status-failed-blocker';
            statusText = 'FAIL (Blocker)';
        } else if (run.status === 'failed_major') {
            statusClass = 'status-failed-major';
            statusText = 'FAIL (Major)';
        } else {
            // Fallback for legacy 'failed' status
            const hasBlocker = run.features && run.features.some(f => f.failed_blocker > 0);
            if (hasBlocker) {
                statusClass = 'status-failed-blocker';
                statusText = 'FAIL (Blocker)';
            } else {
                statusClass = 'status-failed-major';
                statusText = 'FAIL (Major)';
            }
        }
        const passRate = run.pass_rate || run.passRate || 0;
        const cleanTimestamp = run.timestamp.trim(); // Remove any leading/trailing whitespace

        // Create the correct report filename, e.g., report-20250516-161132.html
        const reportFilename = `report-${cleanTimestamp.replace(/_/g, '-')}.html`;

        // Parent Row
        html += `
            <tr class="accordion-header" data-run-index="${runIndex}">
                <td style="text-align: left;"><span class="chevron">▶</span>${formatTimestamp(cleanTimestamp)}</td>
                <td style="text-align: center;"><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td style="text-align: center; font-weight: bold;">(<span style="color: #8B4513;">${run.total}</span>) <span style="color: #28a745;">${run.passed}</span>/<span style="color: #ff5722;">${run.failed_major || 0}</span>/<span style="color: #e51c23;">${run.failed_blocker || 0}</span></td>
                <td style="text-align: center; font-weight: bold;">${passRate.toFixed(2)}%</td>
                        <td style="text-align: center; white-space: nowrap;">
            <button class="btn btn-primary" onclick="event.stopPropagation(); downloadAllPDFsForRun('${cleanTimestamp}', ${runIndex})" style="margin-right: 8px; display: inline-block;">📄 Download PDF</button>
            <button class="btn btn-secondary" onclick="event.stopPropagation(); checkAndOpenRobotReport('${cleanTimestamp}')" style="display: inline-block;">🤖 Robot Report</button>
        </td>
            </tr>
        `;

        // Child Row (Sub-table)
        html += `<tr class="accordion-body"><td colspan="5">`;
        if (run.features && run.features.length > 0) {
            html += `<table class="sub-table"><thead><tr>
                        <th style="text-align: left;">Feature Name</th>
                        <th style="text-align: center;">Status</th>
                        <th style="text-align: center;">Summary (Total) Passed/Failed Major/Failed Blocker</th>
                        <th style="text-align: center;">Pass Rate</th>
                        <th style="text-align: center;">Actions</th>
                    </tr></thead><tbody>`;
            run.features.forEach((feature, featureIndex) => {
                // Determine feature status class and text based on failure types
                let featureStatusClass, featureStatusText;
                if (feature.status === 'passed') {
                    featureStatusClass = 'status-passed';
                    featureStatusText = 'PASS';
                } else if (feature.status === 'not_run') {
                    featureStatusClass = 'status-not-run';
                    featureStatusText = 'NOT RUN';
                } else if (feature.status === 'failed_blocker') {
                    featureStatusClass = 'status-failed-blocker';
                    featureStatusText = 'FAIL (Blocker)';
                } else if (feature.status === 'failed_major') {
                    featureStatusClass = 'status-failed-major';
                    featureStatusText = 'FAIL (Major)';
                } else {
                    // Fallback for legacy 'failed' status
                    if (feature.failed_blocker > 0) {
                        featureStatusClass = 'status-failed-blocker';
                        featureStatusText = 'FAIL (Blocker)';
                    } else {
                        featureStatusClass = 'status-failed-major';
                        featureStatusText = 'FAIL (Major)';
                    }
                }
                
                const featurePassRate = feature.total > 0 ? ((feature.passed / feature.total) * 100).toFixed(2) : 0;
                html += `
                    <tr>
                        <td style="text-align: left;">${feature.feature_name}</td>
                        <td style="text-align: center;"><span class="status-badge ${featureStatusClass}">${featureStatusText}</span></td>
                        <td style="text-align: center; font-weight: bold;">(<span style="color: #8B4513;">${feature.total}</span>) <span style="color: #28a745;">${feature.passed}</span>/<span style="color: #ff5722;">${feature.failed_major || 0}</span>/<span style="color: #e51c23;">${feature.failed_blocker || 0}</span></td>
                        <td style="text-align: center; font-weight: bold;">${featurePassRate}%</td>
                        <td style="text-align: center;">
                            <button class="btn btn-primary" onclick="event.stopPropagation(); viewFeatureDetailsInRunAsync(${runIndex}, ${featureIndex})">
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
        // Determine latest status class and text based on failure types
        let latestStatusClass, latestStatusText;
        if (latestRun.status === 'passed') {
            latestStatusClass = 'status-passed';
            latestStatusText = 'PASS';
        } else if (latestRun.status === 'not_run') {
            latestStatusClass = 'status-not-run';
            latestStatusText = 'NOT RUN';
        } else if (latestRun.status === 'failed_blocker') {
            latestStatusClass = 'status-failed-blocker';
            latestStatusText = 'FAIL (Blocker)';
        } else if (latestRun.status === 'failed_major') {
            latestStatusClass = 'status-failed-major';
            latestStatusText = 'FAIL (Major)';
        } else {
            // Fallback for legacy 'failed' status
            if (latestRun.failed_blocker > 0) {
                latestStatusClass = 'status-failed-blocker';
                latestStatusText = 'FAIL (Blocker)';
            } else {
                latestStatusClass = 'status-failed-major';
                latestStatusText = 'FAIL (Major)';
            }
        }
        
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
                        <th style="text-align: center;">Summary (Total) Passed/Failed Major/Failed Blocker</th>
                        <th style="text-align: center;">Pass Rate</th>
                        <th style="text-align: center;">Actions</th>
                    </tr></thead><tbody>`;
        
        feature.history.forEach(featureRun => {
            // Determine feature run status class and text based on failure types
            let featureStatusClass, featureStatusText;
            if (featureRun.status === 'passed') {
                featureStatusClass = 'status-passed';
                featureStatusText = 'PASS';
            } else if (featureRun.status === 'not_run') {
                featureStatusClass = 'status-not-run';
                featureStatusText = 'NOT RUN';
            } else if (featureRun.status === 'failed_blocker') {
                featureStatusClass = 'status-failed-blocker';
                featureStatusText = 'FAIL (Blocker)';
            } else if (featureRun.status === 'failed_major') {
                featureStatusClass = 'status-failed-major';
                featureStatusText = 'FAIL (Major)';
            } else {
                // Fallback for legacy 'failed' status
                if (featureRun.failed_blocker > 0) {
                    featureStatusClass = 'status-failed-blocker';
                    featureStatusText = 'FAIL (Blocker)';
                } else {
                    featureStatusClass = 'status-failed-major';
                    featureStatusText = 'FAIL (Major)';
                }
            }
            
            const featureRunPassRate = featureRun.total > 0 ? ((featureRun.passed / featureRun.total) * 100).toFixed(2) : 0;
            html += `
                <tr>
                    <td style="text-align: left;">${formatTimestamp(featureRun.timestamp)}</td>
                    <td style="text-align: center;"><span class="status-badge ${featureStatusClass}">${featureStatusText}</span></td>
                    <td style="text-align: center; font-weight: bold;">(<span style="color: #8B4513;">${featureRun.total}</span>) <span style="color: #28a745;">${featureRun.passed}</span>/<span style="color: #ff5722;">${featureRun.failed_major || 0}</span>/<span style="color: #e51c23;">${featureRun.failed_blocker || 0}</span></td>
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
    
    // Determine status class and text based on failure types
    let statusClass, statusText;
    if (feature.status === 'passed') {
        statusClass = 'status-passed';
        statusText = 'PASS';
    } else if (feature.status === 'not_run') {
        statusClass = 'status-not-run';
        statusText = 'NOT RUN';
    } else if (feature.status === 'failed_blocker') {
        statusClass = 'status-failed-blocker';
        statusText = 'FAIL (Blocker)';
    } else if (feature.status === 'failed_major') {
        statusClass = 'status-failed-major';
        statusText = 'FAIL (Major)';
    } else {
        // Fallback for legacy 'failed' status
        if (feature.failed_blocker > 0) {
            statusClass = 'status-failed-blocker';
            statusText = 'FAIL (Blocker)';
        } else {
            statusClass = 'status-failed-blocker';
            statusText = 'FAIL (Major)';
        }
    }
    
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
                <span class="stat-failed-major">⚠️ FAIL (Major): <strong>${feature.failed_major || 0}</strong></span>
                <span class="stat-failed-blocker">🚫 FAIL (Blocker): <strong>${feature.failed_blocker || 0}</strong></span>
                <span class="stat-rate">📈 Pass Rate: <strong>${passRate}%</strong></span>
            </div>
        </div>

        <div class="mb-20">
            <h3>📄 Excel Report</h3>
            ${excelSectionHtml}
        </div>
        
        <div class="mb-20">
            <div class="header-with-button">
                <h3>📸 TEST EVIDENCE SCREENSHOTS</h3>
                <button class="btn btn-primary download-all-pdfs-btn" 
                        onclick="downloadAllTestCasesPDF('${feature.feature_name}', '${feature.run_timestamp}', ${runIndex}, ${featureIndex})"
                        title="Download all test case PDFs as ZIP">
                    📦 Download All PDFs
                </button>
            </div>
            ${await generateTestCaseGallery(feature, testCaseDetails, galleryId)}
        </div>
    `;
    
    modal.style.display = 'block';

    // Initialize separate LightGallery instances for each test case
    console.log('[DEBUG] About to initialize LightGallery for gallery:', galleryId);
    setTimeout(() => {
        initializeTestCaseGalleries(galleryId);
    }, 100); // Small delay to ensure DOM is ready
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

// Function to format text with line breaks
function formatTextWithLineBreaks(text) {
    if (!text) return '';
    return text.toString()
        .replace(/\r\n/g, '\n') // แปลง \r\n เป็น \n
        .replace(/\r/g, '\n'); // แปลง \r เป็น \n
}

// Function to get description from Excel data
function getDescriptionFromExcelData(excelData, testCaseId) {
    if (!excelData) return null;
    
    // Find relevant columns
    const idColumns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo'];
    const descColumns = ['Test Case Description', 'TestCaseDescription', 'Description', 'Test Description', 'Name'];
    
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
        return formatTextWithLineBreaks(matchingRow[descCol].toString().trim());
    }
    
    return null;
}

// Function to get error message from Excel data
function getErrorFromExcelData(excelData, testCaseId) {
    if (!excelData) return null;
    
    // Find relevant columns
    const idColumns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo'];
    const errorColumns = ['Fail_Description', 'TestResult_Description', 'Error', 'Fail Description', 'Failure Reason', 'Error Message'];
    
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
        return errorMsg !== '' ? formatTextWithLineBreaks(errorMsg) : null;
    }
    
    return null;
}

// Function to get expected result from Excel data
function getExpectedResultFromExcelData(excelData, testCaseId) {
    if (!excelData) return null;
    
    // Find relevant columns
    const idColumns = ['Test Case ID', 'TestCaseID', 'Test Case', 'ID', 'TestCase', 'TestCaseNo'];
    const expectedResultColumns = ['ExpectedResult', 'Expected Result', 'Expected', 'Expected Outcome'];
    
    const idCol = excelData.headers.find(h => idColumns.includes(h));
    const expectedResultCol = excelData.headers.find(h => expectedResultColumns.includes(h));
    
    if (!idCol || !expectedResultCol) return null;
    
    // Find matching row
    const matchingRow = excelData.rows.find(row => {
        const rowId = row[idCol];
        return rowId && (rowId.toString() === testCaseId.toString() || 
                       testCaseId.startsWith(rowId.toString() + '_'));
    });
    
    if (matchingRow && matchingRow[expectedResultCol]) {
        const expectedResult = matchingRow[expectedResultCol].toString().trim();
        return expectedResult !== '' ? formatTextWithLineBreaks(expectedResult) : null;
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
            statusBadge = '<span class="status-badge test-case-badge status-passed">PASS</span>';
        } else if (status === 'fail (major)') {
            statusBadge = '<span class="status-badge test-case-badge status-failed-major">FAIL (Major)</span>';
        } else if (status === 'fail (blocker)') {
            statusBadge = '<span class="status-badge test-case-badge status-failed-blocker">FAIL (Blocker)</span>';
        } else if (status === 'fail') {
            // Default to major for legacy 'fail' status
            statusBadge = '<span class="status-badge test-case-badge status-failed-major">FAIL (Major)</span>';
        } else {
            statusBadge = '<span class="status-badge test-case-badge status-not-run">NOT RUN</span>';
        }
        
        // Get test case description, fail description (always read), and expected result from Excel data
        const testCaseDescription = getDescriptionFromExcelData(excelData, excelTestCaseId);
        const failDescription = getErrorFromExcelData(excelData, excelTestCaseId);
        const expectedResult = getExpectedResultFromExcelData(excelData, excelTestCaseId);
        
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
        
        // Create unique gallery ID for this specific test case
        const testCaseGalleryId = `${galleryId}-testcase-${testCaseIndex}`;
        
        // Prepare screenshot gallery HTML
        let screenshotGalleryHtml = '';
        if (matchingImages && matchingImages.length > 0) {
            // Filter out only invalid paths, show all valid images including PDFs
            const validImages = matchingImages.filter(imgPath => {
                // Check if imgPath is valid
                if (!imgPath || typeof imgPath !== 'string' || imgPath.trim() === '') {
                    console.warn('[DEBUG] Invalid imgPath in test evidence:', imgPath);
                    return false; // Remove invalid paths
                }
                return true; // Show all valid images including PDFs
            });
            
            if (validImages.length > 0) {
                const maxPreviewImages = 3; // แสดง 3 รูปแรก
                const previewImages = validImages.slice(0, maxPreviewImages);
            
                screenshotGalleryHtml += `<div class="features-grid test-case-gallery" data-gallery-id="${testCaseGalleryId}">`;
                
                // Show preview images (including HTML and Excel as thumbnails via API)
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
                    
                    const fileExt = fixedPath.toLowerCase();
                    const isHtml = fileExt.endsWith('.html') || fileExt.endsWith('.htm');
                    const isExcel = fileExt.endsWith('.xlsx') || fileExt.endsWith('.xls');
                    const relForApi = fixedPath.startsWith('/results/') ? fixedPath.slice(1) : fixedPath.replace(/^\//, '');
                    
                    // Use evidence_thumbnail API for all file types
                    const thumbSrc = `/api/evidence_thumbnail?path=${encodeURIComponent(relForApi)}`;
                    console.log(`[DEBUG] Thumbnail URL for ${imgFileName}: ${thumbSrc}`);

                    if (isHtml) {
                        // HTML files: use thumbnail for LightGallery display, keep original path for click action
                        screenshotGalleryHtml += `
                            <a href="${thumbSrc}" class="gallery-item gallery-item-html" data-type="html" data-sub-html="<h4>${imgFileName}</h4>" data-original-html="${fixedPath}" data-lg-size="800-600">
                                <img src="${thumbSrc}" alt="HTML Evidence for ${actualFolderName}: ${imgFileName}" loading="lazy" 
                                     onload="console.log('[DEBUG] Gallery HTML thumbnail loaded:', '${imgFileName}', this.naturalWidth, 'x', this.naturalHeight)"
                                     onerror="console.error('[DEBUG] Gallery HTML thumbnail failed to load:', '${imgFileName}', this.src)" />
                                <div class="gallery-item-info">
                                    <span>${imgFileName}</span>
                                    <br><small>Test Case: ${actualFolderName}</small>
                                </div>
                            </a>
                        `;
                    } else if (isExcel) {
                        // Excel files - show icon and allow download
                        screenshotGalleryHtml += `
                            <a href="${fixedPath}" download class="gallery-item gallery-item-excel" data-type="excel" data-sub-html="<h4>${imgFileName}</h4>">
                                <img src="${thumbSrc}" alt="Excel Evidence for ${actualFolderName}: ${imgFileName}" loading="lazy" />
                                <div class="gallery-item-info">
                                    <span>📊 ${imgFileName}</span>
                                    <br><small>Test Case: ${actualFolderName}</small>
                                    <br><small>Click to download</small>
                                </div>
                            </a>
                        `;
                    } else {
                        // Regular images
                        screenshotGalleryHtml += `
                            <a href="${fixedPath}" class="gallery-item gallery-item-image" data-type="image" data-sub-html="<h4>${imgFileName}</h4>" data-lg-size="1600-1200">
                                <img src="${thumbSrc}" alt="Test Evidence for ${actualFolderName}: ${imgFileName}" loading="lazy" />
                                <div class="gallery-item-info">
                                    <span>${imgFileName}</span>
                                    <br><small>Test Case: ${actualFolderName}</small>
                                </div>
                            </a>
                        `;
                    }
                });
                
                // Add "ดูรูปเพิ่มเติม" button if there are more than 4 images
                if (validImages.length > 4) {
                    // Ensure validImages are all valid before stringifying
                    const safeImages = validImages.filter(img => img && typeof img === 'string' && img.trim() !== '');
                    console.log('[DEBUG] Safe images for more button:', safeImages.length, 'out of', validImages.length);
                    
                    screenshotGalleryHtml += `
                        <button class="btn btn-secondary"
                            data-testcase-name="${excelTestCaseId}"
                            data-status="${status}"
                            data-images='${JSON.stringify(safeImages)}'
                            onclick="openAllImagesFromData(this)">
                            ดูรูปเพิ่มเติม
                        </button>
                    `;
                }
                
                screenshotGalleryHtml += '</div>';
            } else {
                screenshotGalleryHtml += '<div class="features-grid test-case-gallery" data-gallery-id="${testCaseGalleryId}">';
                screenshotGalleryHtml += '<div class="no-screenshot-placeholder">No screenshot found</div>';
                screenshotGalleryHtml += '</div>';
            }
        } else {
            // No matching screenshot folder found - show "No screenshot found"
            screenshotGalleryHtml += '<div class="features-grid test-case-gallery" data-gallery-id="${testCaseGalleryId}">';
            screenshotGalleryHtml += '<div class="no-screenshot-placeholder">No screenshot found</div>';
            screenshotGalleryHtml += '</div>';
        }
        
        // Add test case header with new layout (including screenshots and error message inside the same container)
        html += `
            <div class="test-case-header-new">
                <div class="test-case-title-row">
                    <span class="test-case-title-new">Test Case: ${actualFolderName}</span>
                    ${statusBadge}
                    <button class="btn btn-sm btn-outline-primary test-case-pdf-btn" 
                            onclick="exportTestCasePDF('${excelTestCaseId}', '${feature.feature_name}', '${feature.run_timestamp}')"
                            title="Export Test Case PDF">
                        📄 Download PDF
                    </button>
                </div>
                
                <div class="test-information-box">
                    ${testCaseDescription ? `<div class="info-row"><span class="info-label">Description:</span> <div class="info-content">${testCaseDescription}</div></div>` : ''}
                    ${expectedResult ? `<div class="info-row"><span class="info-label">Expected Result:</span> <div class="info-content">${expectedResult}</div></div>` : ''}
                </div>

                ${(() => { 
                    const content = (failDescription && failDescription.trim() !== '' ? failDescription : '-'); 
                    const errorTitle = status === 'fail (blocker)' ? '🚫 Blocker Failure:' : 
                                     status === 'fail (major)' ? '⚠️ Major Failure:' : 
                                     status === 'fail' ? '❌ Failure:' : '';
                    return errorTitle ? `<div class=\"test-case-error\"><div class=\"test-case-error-title\">${errorTitle}</div><div class=\"error-content\">${content}</div></div>` : '';
                })()}
                
                ${screenshotGalleryHtml}
            </div>
        `;
        
        // Add separator between test cases (except for the last one) - AFTER screenshots
        if (testCaseIndex < Object.keys(testCaseDetails).length - 1) {
            html += `<div class="test-case-separator"></div>`;
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
                // ใช้ formatTextWithLineBreaks เพื่อรักษาการขึ้นบรรทัดใหม่
                const formattedValue = formatTextWithLineBreaks(cellValue);
                // แปลง \n เป็น <br> เพื่อแสดงการขึ้นบรรทัดใหม่ใน HTML
                const htmlValue = formattedValue.replace(/\n/g, '<br>');
                tableHtml += `<td>${htmlValue}</td>`;
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

// Unified PDF export function
async function exportPDF(options, customFilename = null) {
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
            downloadPDF(blob, customFilename);
            return true;
        } else {
            const errorText = await response.text();
            console.error('PDF export failed:', response.status, errorText);
            alert(`Export failed: ${response.status} - ${errorText}`);
            return false;
        }
    } catch (error) {
        console.error('PDF export error:', error);
        alert(`Export error: ${error.message}`);
        return false;
    }
}

// Export PDF for specific run
async function exportRunPDF(timestamp) {
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
    
    // Use consistent filename format with server
    const formattedDate = formatTimestamp(timestamp).replace(/[\/\s:]/g, '_');
    const customFilename = `DRDB_TestReport_${formattedDate}`;
    
    await exportPDF(options, customFilename);
}

// Function to export individual test case PDF
async function exportTestCasePDF(testCaseId, featureName, runTimestamp) {
    try {
        console.log(`[DEBUG] Starting PDF export for test case: ${testCaseId} from ${featureName} (${runTimestamp})`);
        
        // แสดง loading overlay
        showPDFLoadingOverlay();
        
        const requestData = {
            test_case_id: testCaseId,
            feature_name: featureName,
            run_timestamp: runTimestamp
        };
        console.log('[DEBUG] Request payload:', requestData);
        
        const response = await fetch('/api/export_testcase_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        console.log(`[DEBUG] Response status: ${response.status}`);
        console.log(`[DEBUG] Response headers:`, Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
            console.error(`[ERROR] HTTP error ${response.status}`);
            try {
                const errorData = await response.json();
                console.error('[ERROR] Error response data:', errorData);
                
                // Special handling for large file errors
                if (response.status === 413) {
                    throw new Error(`PDF ขนาดใหญ่เกินไป: ${errorData.error}\n\nระบบจะสร้าง PDF แบบย่อให้อัตโนมัติ โปรดลองอีกครั้ง`);
                }
                
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            } catch (parseError) {
                console.error('[ERROR] Failed to parse error response:', parseError);
                const errorText = await response.text();
                console.error('[ERROR] Raw error response:', errorText);
                
                if (response.status === 413) {
                    throw new Error(`PDF ขนาดใหญ่เกินไป (${response.status}). โปรดติดต่อผู้ดูแลระบบ`);
                }
                
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
        }

        const blob = await response.blob();
        console.log(`[DEBUG] PDF blob received. Size: ${blob.size} bytes, Type: ${blob.type}`);
        
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `TestCase_${testCaseId}_${featureName}_${timestamp}.pdf`;
        console.log(`[DEBUG] Generated filename: ${filename}`);
        
        downloadPDF(blob, filename);
        console.log('[DEBUG] PDF download initiated successfully');
        
    } catch (error) {
        console.error('[ERROR] Error exporting test case PDF:', error);
        console.error('[ERROR] Error stack:', error.stack);
        alert(`Error exporting test case PDF: ${error.message}`);
    } finally {
        // ซ่อน loading overlay
        hidePDFLoadingOverlay();
    }
}

// เพิ่มฟังก์ชันใหม่สำหรับดาวน์โหลด PDF ทั้งหมด
async function downloadAllTestCasesPDF(featureName, runTimestamp, runIndex, featureIndex) {
    try {
        // แสดง loading overlay
        showPDFLoadingOverlay();
        
        // แสดง loading state
        const btn = document.querySelector('.download-all-pdfs-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Generating ZIP...';
        btn.disabled = true;

        // เรียก API สำหรับสร้าง ZIP file ที่มี PDF ของทุก feature
        const response = await fetch('/api/export_feature_pdfs_zip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                feature_name: featureName,
                run_timestamp: runTimestamp,
                run_index: runIndex,
                feature_index: featureIndex
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        // ดาวน์โหลดไฟล์ ZIP
        const blob = await response.blob();
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `${featureName}_AllTestCases_${timestamp}.zip`;
        
        // ใช้ฟังก์ชัน downloadPDF ที่แก้ไขแล้ว (จะไม่บังคับนามสกุล .pdf)
        downloadPDF(blob, filename);

    } catch (error) {
        console.error('Error downloading all PDFs:', error);
        alert('Error downloading PDFs: ' + error.message);
    } finally {
        // ซ่อน loading overlay
        hidePDFLoadingOverlay();
        
        // คืนค่าเดิมของปุ่ม
        const btn = document.querySelector('.download-all-pdfs-btn');
        btn.innerHTML = '📦 Download All PDFs';
        btn.disabled = false;
    }
}

// Export functions for global access
window.viewFeatureDetailsInRun = viewFeatureDetailsInRun;
window.closeModal = closeModal;
window.previewExcel = previewExcel;
window.exportRunPDF = exportRunPDF;
window.exportTestCasePDF = exportTestCasePDF;
window.downloadAllTestCasesPDF = downloadAllTestCasesPDF;

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
    // Map new statuses to text and classes
    let status = 'NOT RUN';
    let statusClass = 'status-not-run';
    if (currentData.status === 'passed') {
        status = 'PASS';
        statusClass = 'status-passed';
    } else if (currentData.status === 'not_run') {
        status = 'NOT RUN';
        statusClass = 'status-not-run';
    } else if (currentData.status === 'failed_blocker') {
        status = 'FAILED (Blocker)';
        statusClass = 'status-failed-blocker';
    } else if (currentData.status === 'failed_major' || currentData.status === 'failed') {
        status = 'FAILED (Major)';
        statusClass = 'status-failed-major';
    }
    
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
    if (!mainGallery) {
        console.log('[DEBUG] Main gallery not found:', galleryId);
        return;
    }
    
    // Find all test case galleries within this main gallery
    const testCaseGalleries = mainGallery.querySelectorAll('.test-case-gallery');
    console.log('[DEBUG] Found test case galleries:', testCaseGalleries.length);
    
    testCaseGalleries.forEach((galleryElement, index) => {
        if (galleryElement) {
            console.log(`[DEBUG] Initializing LightGallery for gallery ${index}`);
            
            // Check if LightGallery is available
            if (typeof lightGallery === 'undefined') {
                console.error('[DEBUG] LightGallery not available');
                return;
            }
            
            // Check if plugins are available
            const plugins = [];
            if (window.lgZoom) plugins.push(window.lgZoom);
            if (window.lgFullscreen) plugins.push(window.lgFullscreen);
            if (window.lgIframe) plugins.push(window.lgIframe);
            
            console.log('[DEBUG] Available plugins:', plugins.length);
            
            // Debug gallery items before initializing LightGallery
            const htmlItems = galleryElement.querySelectorAll('.gallery-item-html');
            const imageItems = galleryElement.querySelectorAll('.gallery-item-image');
            console.log(`[DEBUG] Gallery ${index} items:`, {
                html: htmlItems.length,
                image: imageItems.length,
                total: galleryElement.querySelectorAll('.gallery-item').length
            });
            
            // Debug HTML items attributes
            htmlItems.forEach((item, idx) => {
                console.log(`[DEBUG] HTML item ${idx}:`, {
                    href: item.getAttribute('href'),
                    iframe: item.getAttribute('data-iframe'),
                    subHtml: item.getAttribute('data-sub-html'),
                    size: item.getAttribute('data-lg-size'),
                    classes: item.className
                });
            });
            
            // Initialize separate LightGallery for each test case
            const lgInstance = lightGallery(galleryElement, {
                plugins: plugins,
                speed: 800,
                scale: 1.5,
                actualSize: true,
                download: true,
                counter: true,
                // Attach LG to both image and HTML items; Excel items are excluded
                selector: '.gallery-item-image, .gallery-item-html',
                appendSubHtmlTo: '.lg-item',
                backdropDuration: 500,
                swipeThreshold: 50,
                touchMove: true,
                enableSwipe: true,
                enableTouch: true,
                onBeforeOpen: () => {
                    console.log('[DEBUG] LightGallery opening');
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
                },
                onAfterOpen: () => {
                    console.log('[DEBUG] LightGallery opened successfully');
                    
                    // Debug current item info
                    const currentItem = document.querySelector('.lg-current');
                    if (currentItem) {
                        const iframe = currentItem.querySelector('iframe');
                        const img = currentItem.querySelector('img');
                        console.log('[DEBUG] Current item opened:', {
                            hasIframe: !!iframe,
                            hasImg: !!img,
                            iframeSrc: iframe ? iframe.src : null,
                            imgSrc: img ? img.src : null
                        });
                    }
                },
                onBeforeClose: () => {
                    console.log('[DEBUG] LightGallery closing');
                }
            });
            // Do not intercept click events; let LightGallery handle index mapping
        }
    });
}





function downloadPDF(blob, filename = null) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    // Use consistent filename format - don't force .pdf extension
    if (filename) {
        a.download = filename; // Use filename as-is, don't append .pdf
    } else {
        // Use same format as server: DRDB_TestReport_YYYYMMDD_HHMMSS.pdf
        const timestamp = new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14);
        const formattedTimestamp = timestamp.slice(0, 8) + '_' + timestamp.slice(8, 14);
        a.download = `DRDB_TestReport_${formattedTimestamp}.pdf`;
    }
    
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }, 100);
}

// Helper function to open all images modal from data attributes
async function openAllImagesFromData(element) {
    try {
        console.log('[DEBUG] openAllImagesFromData called');
        // Show blocking overlay while preparing thumbnails (HTML screenshots can take time)
        showBlockingOverlay('กำลังกำหนดค่ารูปภาพทั้งหมด', 'กรุณารอสักครู่ ระบบกำลังดำเนินการ');
        
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

        // NEW: Eagerly generate thumbnails to ensure .thumbnails exists and HTML screenshots are captured
        await prefetchEvidenceThumbnails(validImages);

        console.log('[DEBUG] Final valid images count:', validImages.length);
        console.log('[DEBUG] Sample valid paths:', validImages.slice(0, 3));
        
        showAllImagesModal(testCaseName, validImages, status, testCaseName);
    } catch (error) {
        console.error('[DEBUG] Unexpected error in openAllImagesFromData:', error);
        console.error('[DEBUG] Error stack:', error.stack);
        alert('เกิดข้อผิดพลาดไม่คาดคิด: ' + error.message);
    }
    finally {
        hideBlockingOverlay();
    }
}

// NEW: Helper function to eagerly generate thumbnails and ensure .thumbnails directory exists
async function prefetchEvidenceThumbnails(imagePaths) {
    try {
        console.log('[DEBUG] Prefetching thumbnails for', imagePaths.length, 'files to ensure .thumbnails directory exists');
        
        const requests = [];
        imagePaths.forEach((p, index) => {
            if (!p || typeof p !== 'string') return;
            
            const lower = p.toLowerCase();
            // We use the same endpoint for all file types; HTML files will trigger generation
            if (lower.endsWith('.html') || lower.endsWith('.htm') || lower.endsWith('.xlsx') || lower.endsWith('.xls') || /\.(png|jpe?g|gif|bmp)$/.test(lower)) {
                const relForApi = p.startsWith('/results/') ? p.slice(1) : p.replace(/^\//, '');
                const url = `/api/evidence_thumbnail?path=${encodeURIComponent(relForApi)}`;
                
                console.log(`[DEBUG] Prefetching thumbnail ${index + 1}: ${relForApi}`);
                requests.push(
                    fetch(url, { cache: 'reload' })
                        .then(response => {
                            if (response.ok) {
                                console.log(`[DEBUG] Successfully prefetched thumbnail for: ${relForApi}`);
                            } else {
                                console.warn(`[DEBUG] Failed to prefetch thumbnail for: ${relForApi} (${response.status})`);
                            }
                        })
                        .catch(error => {
                            console.warn(`[DEBUG] Error prefetching thumbnail for: ${relForApi}:`, error);
                        })
                );
            }
        });
        
        if (requests.length > 0) {
            console.log(`[DEBUG] Sending ${requests.length} thumbnail prefetch requests...`);
            await Promise.allSettled(requests);
            console.log('[DEBUG] Thumbnail prefetch completed');
        } else {
            console.log('[DEBUG] No thumbnail prefetch requests needed');
        }
    } catch (e) {
        console.log('[DEBUG] prefetchEvidenceThumbnails error (non-fatal):', e);
    }
}

// Function to show all images modal for specific test case
function showAllImagesModal(testCaseName, images, status, actualFolderName = null) {
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
    
    // Use actualFolderName if provided, otherwise fallback to testCaseName
    const displayName = actualFolderName || testCaseName;
    
    const statusBadge = status === 'pass' ? '<span class="status-badge status-passed">PASS</span>' :
                         status === 'fail' ? '<span class="status-badge status-failed">FAIL</span>' :
                         '<span class="status-badge status-not-run">NOT RUN</span>';
    
    // Create simple gallery HTML without complex attributes initially
    const galleryHTML = images.map((rawPath, index) => {
        if (!rawPath || typeof rawPath !== 'string') return '';
        let fixedPath = rawPath;
        if (!rawPath.startsWith('/results/')) {
            fixedPath = rawPath.startsWith('results/') ? ('/' + rawPath) : ('/results/' + rawPath.replace(/^\//, ''));
        }
        const imgFileName = fixedPath.split('/').pop();
        const fileExt = fixedPath.toLowerCase();
        const isHtml = fileExt.endsWith('.html') || fileExt.endsWith('.htm');
        const isExcel = fileExt.endsWith('.xlsx') || fileExt.endsWith('.xls');
        const relForApi = fixedPath.startsWith('/results/') ? fixedPath.slice(1) : fixedPath.replace(/^\//, '');
        
        // Use evidence_thumbnail API for all file types
        const thumbSrc = `/api/evidence_thumbnail?path=${encodeURIComponent(relForApi)}`;
        console.log(`[DEBUG] showAllImagesModal - Thumbnail URL for ${imgFileName}: ${thumbSrc}`);

        if (isHtml) {
            return `
                <div class="gallery-item simple-gallery-item" data-index="${index}" data-src="${thumbSrc}" data-type="html" data-original-html="${fixedPath}" onclick="event.preventDefault(); event.stopPropagation(); return false;">
                    <img src="${thumbSrc}" 
                         alt="HTML Evidence: ${imgFileName}" 
                         loading="lazy"
                         onload="console.log('[DEBUG] HTML thumbnail loaded:', '${imgFileName}', this.naturalWidth, 'x', this.naturalHeight)"
                         onerror="console.error('[DEBUG] HTML thumbnail failed to load:', '${imgFileName}', this.src); this.onerror=null; this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkhUTUwgUHJldmlldzwvdGV4dD48L3N2Zz4=';"
                         style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px; background: #fff; border: 1px solid #eee;" />
                    <div class="gallery-item-info">
                        <span>🌐 ${imgFileName}</span>
                        <br><small>Test Case: ${displayName}</small>
                        <br><small>HTML Thumbnail</small>
                    </div>
                </div>
            `;
        } else if (isExcel) {
            return `
                <div class="gallery-item simple-gallery-item" data-index="${index}" data-src="${fixedPath}" data-type="excel" onclick="event.preventDefault(); event.stopPropagation(); return false;">
                    <img src="${thumbSrc}" alt="Excel Evidence for ${testCaseName}: ${imgFileName}" loading="lazy" />
                    <div class="gallery-item-info">
                        <span>📊 ${imgFileName}</span>
                        <br><small>Test Case: ${displayName}</small>
                        <br><small>Click to download</small>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="gallery-item simple-gallery-item" data-index="${index}" data-src="${fixedPath}" data-type="image" onclick="event.preventDefault(); event.stopPropagation(); return false;">
                    <img src="${thumbSrc}" alt="Test Evidence for ${testCaseName}: ${imgFileName}" loading="lazy" />
                    <div class="gallery-item-info">
                        <span>${imgFileName}</span>
                        <br><small>Test Case: ${displayName}</small>
                    </div>
                </div>
            `;
        }
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
                <h2 style="margin: 0; color: #333;">📸 ไฟล์ Evidence ทั้งหมดของ Test Case: ${displayName} ${statusBadge}</h2>
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
                    จำนวนไฟล์ Evidence ทั้งหมด: ${images.length} ไฟล์ (คลิกที่รูปเพื่อดูขนาดใหญ่)
                    <br><small style="color: #888; font-style: italic; margin-top: 5px; display: block;">
                        💡 HTML files แสดงเป็น thumbnail • คลิกเพื่อดูใน LightGallery • ดับเบิลคลิกเพื่อเปิดไฟล์ต้นฉบับ
                    </small>
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
    
        // Add immediate click handlers for images
        const galleryItems = modal.querySelectorAll('.simple-gallery-item');
    console.log(`[DEBUG] Adding immediate click handlers to ${galleryItems.length} items`);
    
        galleryItems.forEach((item, index) => {
        const img = item.querySelector('img');
        const src = item.getAttribute('data-src'); // This should be thumbnail URL for HTML files
        const type = (item.getAttribute('data-type') || '').toLowerCase();

        // Only handle Excel downloads explicitly; let LightGallery handle all image display (including HTML thumbnails)
        item.addEventListener('click', function(e) {
            if (type === 'excel') {
                e.preventDefault();
                e.stopPropagation();
                // Excel: download directly
                const originalPath = item.getAttribute('data-original-html') || src;
                const link = document.createElement('a');
                link.href = originalPath;
                link.download = originalPath.split('/').pop();
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            // For HTML and images: let LightGallery handle click to show thumbnail/image
            // data-src already contains the correct thumbnail URL for HTML files
        });

        // Add double-click handler for HTML files to open original
        if (type === 'html') {
            item.addEventListener('dblclick', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const originalHtmlPath = item.getAttribute('data-original-html');
                if (originalHtmlPath) {
                    try {
                        const link = document.createElement('a');
                        link.href = originalHtmlPath;
                        link.target = '_blank';
                        link.rel = 'noopener noreferrer';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        console.log('[DEBUG] Opened original HTML file:', originalHtmlPath);
                    } catch (error) {
                        console.error('Error opening HTML file:', error);
                    }
                }
            });
        }
        
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
        
        // Add loading indicator and better error handling
        if (img) {
            img.addEventListener('load', function() {
                console.log(`[DEBUG] Image ${index + 1} loaded successfully`);
                this.style.opacity = '1';
                this.style.border = '1px solid #e0e0e0';
            });
            
            img.addEventListener('error', function() {
                console.error(`[DEBUG] Image ${index + 1} failed to load:`, this.src);
                
                // For HTML files, show a better error placeholder
                if (type === 'html') {
                    this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjVmN2ZhIi8+PHRleHQgeD0iNTAlIiB5PSI0MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzZiNzI4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSI+5LiN5a2Y5LqG5L2/55SoPC90ZXh0Pjx0ZXh0IHg9IjUwJSIgeT0iNjAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5Y2E5YWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkhUTUwg5LiA5Liq5paH5Lu2PC90ZXh0Pjwvc3ZnPg==';
                    this.alt = '❌ HTML Preview ไม่สามารถโหลดได้';
                } else {
                    this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4=';
                    this.alt = '❌ Image not found';
                }
                
                // Add error styling
                this.style.border = '2px solid #ff6b6b';
                this.style.background = '#fff5f5';
            });
            
            // Set initial opacity for loading effect
            img.style.opacity = '0.7';
            img.style.transition = 'opacity 0.3s ease';
        }
    });
    
    console.log('[DEBUG] Modal setup completed with immediate functionality');
    
    // Optional: Try to upgrade to LightGallery later (non-blocking)
    setTimeout(() => {
        console.log('[DEBUG] Attempting to upgrade modal to LightGallery');
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
    
    // Check if plugins are available
    const plugins = [];
    if (window.lgZoom) plugins.push(window.lgZoom);
    if (window.lgFullscreen) plugins.push(window.lgFullscreen);
    if (window.lgIframe) plugins.push(window.lgIframe);
    
    // Debug plugin availability
    console.log('[DEBUG] Plugin availability check:');
    console.log('[DEBUG] lgZoom:', !!window.lgZoom);
    console.log('[DEBUG] lgFullscreen:', !!window.lgFullscreen);
    console.log('[DEBUG] lgIframe:', !!window.lgIframe);
    
    console.log('[DEBUG] Available plugins for modal upgrade:', plugins.length);
    
    try {
        console.log('[DEBUG] Attempting LightGallery upgrade...');
        
        // Convert only image items to LightGallery format; HTML items open new tab
        const galleryItems = galleryElement.querySelectorAll('.simple-gallery-item');
        console.log('[DEBUG] Converting', galleryItems.length, 'items to LightGallery format');
        
        // Debug item types
        const typeCounts = {};
        galleryItems.forEach(item => {
            const type = (item.getAttribute('data-type') || '').toLowerCase();
            typeCounts[type] = (typeCounts[type] || 0) + 1;
        });
        console.log('[DEBUG] Item type distribution:', typeCounts);
        
        galleryItems.forEach((item, index) => {
            const imgSrc = item.getAttribute('data-src');
            const type = (item.getAttribute('data-type') || '').toLowerCase();

            // Build a clean display name for caption
            let displayName = `Item ${index + 1}`;
            if (type === 'html') {
                const originalHtml = item.getAttribute('data-original-html');
                if (originalHtml) {
                    displayName = originalHtml.split('/').pop();
                }
            } else if (imgSrc) {
                // If the src is an API URL like /api/evidence_thumbnail?path=... extract the file name from the path query
                try {
                    const url = new URL(imgSrc, window.location.origin);
                    const qPath = url.searchParams.get('path');
                    if (qPath) {
                        displayName = decodeURIComponent(qPath).split('/').pop();
                    } else {
                        displayName = imgSrc.split('/').pop();
                    }
                } catch (_) {
                    displayName = imgSrc.split('/').pop();
                }
            }

            if (type === 'html') {
                // HTML files: show thumbnail in LightGallery, not iframe
                item.setAttribute('href', imgSrc); // imgSrc should already be thumbnail URL
                item.setAttribute('data-sub-html', `<h4>${displayName}</h4>`);
                item.setAttribute('data-lg-size', '800-600');
                item.classList.add('lg-gallery-item');
                console.log(`[DEBUG] Converted HTML item ${index} for LG (thumbnail):`, {
                    href: imgSrc,
                    subHtml: item.getAttribute('data-sub-html'),
                    size: item.getAttribute('data-lg-size')
                });
            } else if (type === 'excel') {
                // Excel files: keep as simple download links (no LightGallery)
                console.log(`[DEBUG] Excel item ${index} kept as download link`);
            } else {
                // Image files: standard LightGallery format
                item.setAttribute('href', imgSrc);
                item.setAttribute('data-sub-html', `<h4>${displayName}</h4>`);
                item.setAttribute('data-lg-size', '1600-1200');
                item.classList.add('lg-gallery-item');
                console.log(`[DEBUG] Converted image item ${index} for LG`);
            }
        });
        
        // Initialize LightGallery
        console.log('[DEBUG] Initializing LightGallery with plugins:', plugins.length);
        
        // Debug selector items before initialization
        const selectorItems = galleryElement.querySelectorAll('.lg-gallery-item');
        console.log('[DEBUG] Items matching selector .lg-gallery-item:', selectorItems.length);
        selectorItems.forEach((item, idx) => {
            const type = item.getAttribute('data-type');
            const iframe = item.getAttribute('data-iframe');
            console.log(`[DEBUG] Selector item ${idx}:`, { type, iframe, href: item.getAttribute('href') });
        });
        
        const lgInstance = lightGallery(galleryElement, {
            plugins: plugins,
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
                    console.log('[DEBUG] LightGallery onBeforeOpen triggered');
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
                },
                onAfterOpen: () => {
                    console.log('[DEBUG] LightGallery onAfterOpen triggered');
                    
                    // Debug current item info for modal LightGallery
                    const currentItem = document.querySelector('.lg-current');
                    if (currentItem) {
                        const iframe = currentItem.querySelector('iframe');
                        const img = currentItem.querySelector('img');
                        console.log('[DEBUG] Modal LightGallery current item:', {
                            hasIframe: !!iframe,
                            hasImg: !!img,
                            iframeSrc: iframe ? iframe.src : null,
                            imgSrc: img ? img.src : null,
                            itemClasses: currentItem.className
                        });
                    }
                },
                onBeforeClose: () => {
                    console.log('[DEBUG] LightGallery onBeforeClose triggered');
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
        
        // Store instance for cleanup
        galleryElement.lgInstance = lgInstance;
        window.currentAllImagesLG = lgInstance;
        
        // Test click on first item to see if it works
        const firstItem = galleryElement.querySelector('.lg-gallery-item');
        if (firstItem) {
            console.log('[DEBUG] First gallery item found, testing click functionality');
            console.log('[DEBUG] First item href:', firstItem.getAttribute('href'));
            console.log('[DEBUG] First item data-iframe:', firstItem.getAttribute('data-iframe'));
            console.log('[DEBUG] First item data-lg-size:', firstItem.getAttribute('data-lg-size'));
        }
        
    } catch (error) {
        console.log('[DEBUG] LightGallery upgrade failed, keeping simple handlers:', error);
        console.error('[DEBUG] Error details:', error);
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

// 1. เพิ่มฟังก์ชัน downloadLatestPDF() และ downloadLatestRobotReport()
async function downloadLatestPDF() {
    if (!currentData || !currentData.timestamp || !currentData.features || currentData.features.length === 0) {
        alert('No test data available. Please run tests first.');
        return;
    }

    try {
        // แสดง loading overlay
        showPDFLoadingOverlay();
        
        // แสดง loading state
        const btn = document.getElementById('exportPdfBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Generating ZIP...';
        btn.disabled = true;

        // เรียก API สำหรับสร้าง ZIP file ที่มี PDF ของทุก feature
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout
        
        try {
            const response = await fetch('/api/export_latest_all_features_zip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    run_timestamp: currentData.timestamp,
                    features: currentData.features.map(f => ({
                        name: f.feature_name || f.name,
                        excel_path: f.excel_path
                    }))
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (jsonError) {
                // If response is not JSON (e.g., HTML error page), try to get text
                try {
                    const errorText = await response.text();
                    if (errorText.includes('<!doctype') || errorText.includes('<html')) {
                        errorMessage = 'Server error occurred. The request may have timed out or the server is overloaded.';
                    } else {
                        errorMessage = errorText.substring(0, 200) + (errorText.length > 200 ? '...' : '');
                    }
                } catch (textError) {
                    errorMessage = `HTTP error! status: ${response.status}`;
                }
            }
            throw new Error(errorMessage);
        }

        // ดาวน์โหลดไฟล์ ZIP
        const blob = await response.blob();
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `LatestRun_AllFeatures_${timestamp}.zip`;
        
        downloadPDF(blob, filename);
        
        } catch (fetchError) {
            clearTimeout(timeoutId);
            if (fetchError.name === 'AbortError') {
                throw new Error('Request timed out. The PDF generation is taking too long.');
            }
            throw fetchError;
        }

    } catch (error) {
        console.error('Error downloading latest PDFs:', error);
        alert('Error downloading PDFs: ' + error.message);
    } finally {
        // ซ่อน loading overlay
        hidePDFLoadingOverlay();
        
        // คืนค่าเดิมของปุ่ม
        const btn = document.getElementById('exportPdfBtn');
        btn.innerHTML = '📄 Download PDF';
        btn.disabled = false;
    }
}
window.downloadLatestPDF = downloadLatestPDF;

function downloadLatestRobotReport() {
    if (testData && testData.length > 0) {
        const latestRun = testData[0];
        const cleanTimestamp = latestRun.timestamp.trim();
        const reportFilename = `report-${cleanTimestamp.replace(/_/g, '-')}.html`;
        const reportUrl = `/results/${cleanTimestamp}/${reportFilename}`;
        
        // Check if the report file exists before opening
        fetch(reportUrl, { method: 'HEAD' })
            .then(response => {
                if (response.ok) {
                    window.open(reportUrl, '_blank');
                } else {
                    alert(`Robot report not found for run: ${cleanTimestamp}\n\nPlease check if the report file exists at:\n${reportUrl}`);
                }
            })
            .catch(error => {
                console.error('Error checking robot report:', error);
                alert(`Error checking robot report for run: ${cleanTimestamp}\n\nPlease check if the report file exists at:\n${reportUrl}`);
            });
    } else {
        alert('No robot report available. Please run tests first.');
    }
}
window.downloadLatestRobotReport = downloadLatestRobotReport;

// Function for Section 2 Robot Report buttons
function checkAndOpenRobotReport(timestamp) {
    const reportFilename = `report-${timestamp.replace(/_/g, '-')}.html`;
    const reportUrl = `/results/${timestamp}/${reportFilename}`;
    
    // Check if the report file exists before opening
    fetch(reportUrl, { method: 'HEAD' })
        .then(response => {
            if (response.ok) {
                window.open(reportUrl, '_blank');
            } else {
                alert(`Robot report not found for run: ${timestamp}\n\nPlease check if the report file exists at:\n${reportUrl}`);
            }
        })
        .catch(error => {
            console.error('Error checking robot report:', error);
            alert(`Error checking robot report for run: ${timestamp}\n\nPlease check if the report file exists at:\n${reportUrl}`);
        });
}
window.checkAndOpenRobotReport = checkAndOpenRobotReport;

// Function to refresh thumbnails in all currently open modals
function refreshAllModalThumbnails() {
    // Refresh thumbnails in the currently open modal
    const detailModal = document.getElementById('detailModal');
    const allImagesModal = document.getElementById('allImagesModal');
    
    if (detailModal && detailModal.style.display === 'block') {
        // Refresh thumbnails in detail modal
        refreshThumbnailsInModal(detailModal);
    }
    
    if (allImagesModal && allImagesModal.style.display === 'block') {
        // Refresh thumbnails in all images modal
        refreshThumbnailsInModal(allImagesModal);
    }
}

// Function to refresh thumbnails in modal when window regains focus
function refreshThumbnailsInModal(modal) {
    try {
        console.log('[DEBUG] Refreshing thumbnails in modal');
        
        // Find all img elements that might be loading or failed to load
        const thumbnailImages = modal.querySelectorAll('img[src*="evidence_thumbnail"]');
        let refreshCount = 0;
        
        thumbnailImages.forEach((img, index) => {
            // Check if image is loading, failed to load, or appears stuck
            const isLoading = !img.complete;
            const isFailedOrEmpty = img.complete && (img.naturalHeight === 0 || img.naturalWidth === 0);
            const isVisible = img.offsetParent !== null; // Only refresh visible images
            
            if ((isLoading || isFailedOrEmpty) && isVisible) {
                console.log(`[DEBUG] Refreshing thumbnail ${index}: ${img.src}`);
                refreshCount++;
                
                // Force reload by adding cache buster
                const originalSrc = img.src.split('?')[0]; // Remove any existing cache busters
                const cacheBuster = `?_refresh=${Date.now()}_${index}`;
                
                // Set loading state with smooth transition
                img.style.transition = 'opacity 0.3s ease, filter 0.3s ease';
                img.style.opacity = '0.6';
                img.style.filter = 'blur(1px)';
                
                // Reload image
                img.onload = function() {
                    console.log(`[DEBUG] Thumbnail ${index} reloaded successfully`);
                    this.style.opacity = '1';
                    this.style.filter = 'none';
                    this.onload = null;
                    this.onerror = null;
                    
                    // Remove transition after animation
                    setTimeout(() => {
                        this.style.transition = '';
                    }, 300);
                };
                
                img.onerror = function() {
                    console.warn(`[DEBUG] Thumbnail ${index} failed to reload`);
                    this.style.opacity = '1';
                    this.style.filter = 'none';
                    this.onload = null;
                    this.onerror = null;
                    
                    // Remove transition after animation
                    setTimeout(() => {
                        this.style.transition = '';
                    }, 300);
                };
                
                img.src = originalSrc + cacheBuster;
            }
        });
        
        if (refreshCount > 0) {
            console.log(`[DEBUG] Refreshed ${refreshCount} thumbnails`);
        } else {
            console.log('[DEBUG] No thumbnails needed refreshing');
        }
        
    } catch (error) {
        console.error('[DEBUG] Error refreshing thumbnails:', error);
    }
}
window.downloadAllPDFsForRun = downloadAllPDFsForRun;

// Function to download all PDFs for a specific run as ZIP (for History tab)
async function downloadAllPDFsForRun(timestamp, runIndex) {
    try {
        const run = testData[runIndex];
        if (!run || !run.features || run.features.length === 0) {
            alert('No features found in this run.');
            return;
        }

        // แสดง loading overlay
        showPDFLoadingOverlay();

        // แสดง loading state
        const btn = document.querySelector(`[onclick*="downloadAllPDFsForRun('${timestamp}', ${runIndex})"]`);
        if (btn) {
            const originalText = btn.innerHTML;
            btn.innerHTML = '⏳ Generating ZIP...';
            btn.disabled = true;
        }

        // เรียก API สำหรับสร้าง ZIP file ที่มี PDF ของทุก feature
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout
        
        try {
            const response = await fetch('/api/export_latest_all_features_zip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    run_timestamp: timestamp,
                    features: run.features.map(f => ({
                        name: f.feature_name || f.name,
                        excel_path: f.excel_path
                    }))
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (jsonError) {
                // If response is not JSON (e.g., HTML error page), try to get text
                try {
                    const errorText = await response.text();
                    if (errorText.includes('<!doctype') || errorText.includes('<html')) {
                        errorMessage = 'Server error occurred. The request may have timed out or the server is overloaded.';
                    } else {
                        errorMessage = errorText.substring(0, 200) + (errorText.length > 200 ? '...' : '');
                    }
                } catch (textError) {
                    errorMessage = `HTTP error! status: ${response.status}`;
                }
            }
            throw new Error(errorMessage);
        }

        // ดาวน์โหลดไฟล์ ZIP
        const blob = await response.blob();
        const timestampStr = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `Run_${timestamp.replace(/[\/\s:]/g, '_')}_AllFeatures_${timestampStr}.zip`;
        
        downloadPDF(blob, filename);
        
        } catch (fetchError) {
            clearTimeout(timeoutId);
            if (fetchError.name === 'AbortError') {
                throw new Error('Request timed out. The PDF generation is taking too long.');
            }
            throw fetchError;
        }

    } catch (error) {
        console.error('Error downloading run PDFs:', error);
        alert('Error downloading PDFs: ' + error.message);
    } finally {
        // ซ่อน loading overlay
        hidePDFLoadingOverlay();
        
        // คืนค่าเดิมของปุ่ม
        const btn = document.querySelector(`[onclick*="downloadAllPDFsForRun('${timestamp}', ${runIndex})"]`);
        if (btn) {
            btn.innerHTML = '📄 Download PDF';
            btn.disabled = false;
        }
    }
}