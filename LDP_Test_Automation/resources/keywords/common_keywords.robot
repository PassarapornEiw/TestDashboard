*** Settings ***
Documentation    Common Keywords for all test cases
Library          SeleniumLibrary
Library          Collections
Library          DateTime
Library          String
Library          ../libraries/config_reader.py    WITH NAME    ConfigReader
Library          ../libraries/data_reader.py    WITH NAME    DataReader
Resource         ../variables/common_variables.robot
Resource         ../variables/locators.robot

*** Keywords ***
Initialize Browser
    [Documentation]    Initialize browser based on settings.json
    ${browser_name}=    ConfigReader.Get Browser Name
    ${base_url}=    ConfigReader.Get Base Url
    Set Suite Variable    ${BASE_URL}    ${base_url}    # Set BASE_URL for all page objects
    ${timeout}=    ConfigReader.Get Timeout
    Open Browser    ${base_url}${AUTH_PAGE}    ${browser_name}
    Set Window Size    1920    1080
    Set Selenium Timeout    ${timeout}s
    Set Selenium Implicit Wait    10s

Get Base Url
    [Documentation]    Get base URL from settings.json
    ${base_url}=    ConfigReader.Get Base Url
    RETURN    ${base_url}

Close All Browsers
    [Documentation]    Close all browser instances
    SeleniumLibrary.Close All Browsers

Take Screenshot On Failure
    [Documentation]    Take screenshot on test failure
    [Arguments]    ${test_name}
    ${timestamp}=    Get Current Date    result_format=%Y%m%d-%H%M%S
    ${safe_name}=    Replace String Using Regexp    ${test_name}    [:\\/\\*\\?"<>|]    -
    Capture Page Screenshot    results/screenshots/${safe_name}_${timestamp}.png

Wait For Page Load
    [Documentation]    Wait for page to load completely
    Wait Until Page Contains Element    ${HEADER_TITLE}    timeout=15s
    # Wait for page to stabilize after JavaScript execution
    Sleep    0.5s

Verify Page Title
    [Documentation]    Verify page title
    [Arguments]    ${expected_title}
    Element Should Contain    ${HEADER_TITLE}    ${expected_title}

Navigate To Page
    [Documentation]    Navigate to specific page
    [Arguments]    ${page_name}    ${params}=${EMPTY}
    ${base_url}=    Get Base Url
    ${url}=    Set Variable    ${base_url}${page_name}
    ${url}=    Set Variable If    '${params}' != '${EMPTY}'    ${url}?${params}    ${url}
    Go To    ${url}
    Wait For Page Load

Click Common Back Button
    [Documentation]    Click back button and wait for page load
    page_base.Click Back Button
    Wait For Page Load

Click Close Button
    [Documentation]    Click close button (with confirmation)
    Handle Alert    action=ACCEPT    timeout=5s
    Click Element    ${CLOSE_BUTTON}

Verify Button Disabled
    [Documentation]    Verify button is disabled
    [Arguments]    ${button_locator}
    Element Should Be Disabled    ${button_locator}

Verify Button Enabled
    [Documentation]    Verify button is enabled
    [Arguments]    ${button_locator}
    Element Should Be Enabled    ${button_locator}

Wait For Element And Click
    [Documentation]    Wait for element and click
    [Arguments]    ${locator}    ${timeout}=10s
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Click Element    ${locator}

Verify Element Contains Text
    [Documentation]    Verify element contains expected text
    [Arguments]    ${locator}    ${expected_text}
    Wait Until Element Is Visible    ${locator}
    Element Should Contain    ${locator}    ${expected_text}

Verify Element Not Visible
    [Documentation]    Verify element is not visible
    [Arguments]    ${locator}
    Element Should Not Be Visible    ${locator}

Verify Element Visible
    [Documentation]    Verify element is visible
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}
    Element Should Be Visible    ${locator}

Get Current URL
    [Documentation]    Get current page URL
    ${url}=    Get Location
    RETURN    ${url}

Verify URL Contains
    [Documentation]    Verify URL contains expected text
    [Arguments]    ${expected_text}
    ${current_url}=    Get Current URL
    Should Contain    ${current_url}    ${expected_text}

Clear Local Storage
    [Documentation]    Clear browser local storage
    Execute JavaScript    localStorage.clear();

Set Local Storage Item
    [Documentation]    Set item in local storage
    [Arguments]    ${key}    ${value}
    Execute JavaScript    localStorage.setItem('${key}', '${value}');

Get Local Storage Item
    [Documentation]    Get item from local storage
    [Arguments]    ${key}
    ${value}=    Execute JavaScript    return localStorage.getItem('${key}');
    RETURN    ${value}

Get Test Case Data By ID
    [Documentation]    Get test case data by TestCaseNo
    [Arguments]    ${test_case_no}
    ${test_data}=    DataReader.Get Test Case By Id    ${test_case_no}
    RETURN    ${test_data}

Update Test Result
    [Documentation]    Update test result in Excel
    [Arguments]    ${test_case_no}    ${test_result}    ${fail_description}=${EMPTY}
    DataReader.Update Test Result    ${test_case_no}    ${test_result}    ${fail_description}

Get All Executable Test Cases
    [Documentation]    Get all executable test cases from Excel
    ${test_cases}=    DataReader.Get All Executable Test Cases
    RETURN    ${test_cases}
