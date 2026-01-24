*** Variables ***
# Homepage Selectors
${HP_PROJECTS_GRID}              id:projects-grid
${HP_PROJECT_CARD}                css:.project-card
${HP_PROJECT_NAME}                css:.project-name
${HP_PROJECT_PASS_RATE}           css:.stat-value
${HP_PROJECT_TOTAL_TESTS}         css:.stat-item .stat-value
${HP_PROJECT_LAST_RUN}            css:.last-run
${HP_LOADING}                     id:loading
${HP_ERROR}                       id:error
${HP_NO_PROJECTS}                 id:no-projects
${HP_HEADER_TITLE}                css:.header h1

# Dashboard Selectors
${DB_HEADER}                      css:.header
${DB_HEADER_TITLE}                css:.header h1
${DB_BACK_BUTTON}                 css:a[href="/"]
${DB_SUMMARY_GRID}                css:.summary-grid
${DB_CARD_TOTAL}                 id:total-tests
${DB_CARD_PASSED}                id:passed-tests
${DB_CARD_FAILED_MAJOR}          id:failed-major-tests
${DB_CARD_FAILED_BLOCK}          id:failed-blocker-tests
${DB_CARD_PASS_RATE}             id:pass-rate
${DB_PIE_CHART}                  id:pieChart
${DB_LATEST_RUN_INFO}             id:latest-run-info
${DB_EXPORT_PDF_BTN}              id:exportPdfBtn
${DB_ROBOT_REPORT_BTN}            id:robotReportBtn
${DB_TAB_TIMESTAMP}              css:.tab-button[data-tab="timestamp"]
${DB_TAB_FEATURE}                 css:.tab-button[data-tab="feature"]
${DB_SEARCH_INPUT}                css:input[type="search"]
${DB_DATA_TABLE}                  css:.data-table
${DB_FEATURE_ROW}                 css:.feature-row
${DB_EXPAND_BUTTON}               css:.expand-button
${DB_VIEW_DETAILS_BTN}            css:.view-details-btn

# Modal Selectors
${MODAL}                          css:.modal
${MODAL_CLOSE}                    css:.modal-close
${MODAL_TITLE}                    css:.modal-title
${MODAL_TEST_CASE_LIST}           css:.test-case-list
${MODAL_TEST_CASE_ITEM}           css:.test-case-item
${MODAL_EVIDENCE_GALLERY}         css:.evidence-gallery
${MODAL_EVIDENCE_IMAGE}           css:.evidence-image
${MODAL_EXCEL_PREVIEW}            css:.excel-preview
${MODAL_PDF_DOWNLOAD_BTN}         css:.download-pdf-btn

# Status Badge Selectors
${BADGE_PASS}                     css:.status-badge.status-passed
${BADGE_FAIL_MAJOR}               css:.status-badge.status-failed-major
${BADGE_FAIL_BLOCK}                css:.status-badge.status-failed-blocker
${BADGE_UNKNOWN}                   css:.status-badge.status-not-run
