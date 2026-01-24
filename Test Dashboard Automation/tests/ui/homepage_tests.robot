*** Settings ***
Documentation    Homepage UI Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/variables/selectors.robot
Resource    ../../resources/keywords/common_keywords.robot
Resource    ../../resources/keywords/homepage_keywords.robot
Resource    ../../resources/page_objects/homepage_page.robot
Library    SeleniumLibrary
Library    Collections

Suite Setup    Start Dashboard Server And Open Homepage
Suite Teardown    Stop Dashboard Server And Close Browser
Test Teardown    Take Screenshot On Failure

*** Keywords ***
Start Dashboard Server And Open Homepage
    Start Dashboard Server
    Open Dashboard Homepage

Stop Dashboard Server And Close Browser
    Close Dashboard Browser
    Stop Dashboard Server

*** Test Cases ***
TC_HP_001: Verify Homepage Loads Successfully
    [Documentation]    Verify homepage loads successfully
    [Tags]    smoke    homepage
    Verify Homepage Loaded
    Location Should Be    ${DASHBOARD_URL}/

TC_HP_002: Verify Project Cards Are Displayed
    [Documentation]    Verify project cards are displayed
    [Tags]    homepage
    Wait Until Element Is Visible    ${HP_PROJECTS_GRID}    timeout=10s
    ${count}=    Get Project Count
    Should Be True    ${count} >= ${EXPECTED_MIN_PROJECTS}    At least ${EXPECTED_MIN_PROJECTS} project should be displayed

TC_HP_003: Verify Project Statistics
    [Documentation]    Verify project statistics (pass rate, total tests, last run)
    [Tags]    homepage
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    Dictionary Should Contain Key    ${stats}    name
    Dictionary Should Contain Key    ${stats}    pass_rate
    Dictionary Should Contain Key    ${stats}    total_tests
    Dictionary Should Contain Key    ${stats}    last_run
    Should Not Be Empty    ${stats}[name]
    Should Not Be Empty    ${stats}[pass_rate]

TC_HP_004: Verify Project Card Colors
    [Documentation]    Verify project card colors based on pass rate
    [Tags]    homepage
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${pass_rate_str}=    Get From Dictionary    ${stats}    pass_rate
    ${pass_rate_num}=    Evaluate    int('${pass_rate_str}'.replace('%', ''))
    Run Keyword If    ${pass_rate_num} >= 80    Verify Project Card Color    ${COLOR_PASS}    0
    ...    ELSE IF    ${pass_rate_num} >= 50    Verify Project Card Color    ${COLOR_FAIL_MAJOR}    0
    ...    ELSE    Verify Project Card Color    ${COLOR_FAIL_BLOCK}    0

TC_HP_005: Verify Loading State Display
    [Documentation]    Verify loading state display
    [Tags]    homepage
    # Note: Loading state may appear briefly, test may need adjustment
    # This test verifies the loading element exists in DOM
    Page Should Contain Element    ${HP_LOADING}

TC_HP_006: Verify Error State Display
    [Documentation]    Verify error state display (when API fails)
    [Tags]    homepage    negative
    # Error state is hidden by default, only shows on API failure
    # This test verifies error element exists in DOM
    Page Should Contain Element    ${HP_ERROR}

TC_HP_007: Verify Empty State Display
    [Documentation]    Verify empty state display (when no projects)
    [Tags]    homepage    negative
    # Empty state is hidden by default, only shows when no projects
    # This test verifies empty state element exists in DOM
    Page Should Contain Element    ${HP_NO_PROJECTS}

TC_HP_008: Verify Project Card Click Navigation
    [Documentation]    Verify project card click navigation
    [Tags]    smoke    homepage    navigation
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Click Project Card    ${project_name}
    Location Should Contain    /dashboard
    Location Should Contain    project=${project_name}
