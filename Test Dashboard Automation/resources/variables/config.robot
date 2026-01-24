*** Variables ***
# Dashboard Configuration
${DASHBOARD_URL}          http://127.0.0.1:5000
${DASHBOARD_TIMEOUT}       30s
${BROWSER}                 chrome
${HEADLESS}                ${False}
${IMPLICIT_WAIT}           10s
${PAGE_LOAD_TIMEOUT}       30s

# Paths
${AUTOMATION_PROJECT_DIR}  ${CURDIR}/../../../../Automation_Project
${PROJECT_ROOT}            ${CURDIR}/../../..

# Test Data
${TEST_PROJECT}            DRDB
${EXPECTED_MIN_PROJECTS}   1

# API Endpoints
${API_PROJECTS}            /api/projects
${API_DATA}                /api/data
${API_EXCEL_PREVIEW}       /api/excel_preview
${API_EXPORT_PDF}          /api/export_pdf
${API_EXPORT_TESTCASE_PDF}    /api/export_testcase_pdf
${API_EXPORT_FEATURE_ZIP}  /api/export_feature_pdfs_zip
${API_EVIDENCE_THUMBNAIL}  /api/evidence_thumbnail
${API_THUMBNAIL_INFO}      /api/thumbnail_info

# Status Colors (from specification)
${COLOR_PASS}              #28a745
${COLOR_FAIL_MAJOR}        #ff5722
${COLOR_FAIL_BLOCK}        #e51c23
${COLOR_UNKNOWN}           #6c757d

# Status Values
${STATUS_PASS}             PASS
${STATUS_FAIL_MAJOR}       FAIL (Major)
${STATUS_FAIL_BLOCK}       FAIL (Block)
${STATUS_UNKNOWN}          UNKNOWN
