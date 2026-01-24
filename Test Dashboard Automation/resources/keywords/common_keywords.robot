*** Settings ***
Resource    ../variables/config.robot
Library    SeleniumLibrary
Library    Process
Library    OperatingSystem
Library    Collections
Library    RequestsLibrary
Library    String

*** Keywords ***
Start Dashboard Server
    [Documentation]    Start Flask dashboard server
    [Arguments]    ${server_path}=${EMPTY}
    # Default path: from resources/keywords to Dashboard_Report
    ${default_path}=    Set Variable    ${CURDIR}/../../../Dashboard_Report/dashboard_server.py
    ${final_path}=    Set Variable If    '${server_path}' == '${EMPTY}'    ${default_path}    ${server_path}
    ${final_path_normalized}=    Normalize Path    ${final_path}
    # Split Path returns [directory, filename], get directory (index 0)
    ${path_parts}=    Split Path    ${final_path_normalized}
    ${server_dir}=    Get From List    ${path_parts}    0
    ${server_dir_normalized}=    Normalize Path    ${server_dir}
    Log    Starting dashboard server from: ${final_path_normalized}
    Log    Server directory: ${server_dir_normalized}
    # Verify file exists
    File Should Exist    ${final_path_normalized}
    # Check if server is already running by making an actual request
    ${is_running}=    Check Server Running
    Run Keyword If    ${is_running}    Log    Dashboard server is already running
    ...    ELSE    Start New Server    ${final_path_normalized}    ${server_dir_normalized}
    # Final verification that server is accessible
    ${final_check}=    Check Server Running
    Run Keyword If    not ${final_check}    Fail    Dashboard server is not accessible after startup

Start New Server
    [Documentation]    Start a new dashboard server instance
    [Arguments]    ${server_path}    ${server_dir}
    Log    Starting process: python ${server_path} in directory ${server_dir}
    # Get Python executable path
    ${python_exe}=    Evaluate    __import__('sys').executable
    Log    Using Python: ${python_exe}
    # Normalize paths for Windows
    ${server_path_normalized}=    Normalize Path    ${server_path}
    ${server_dir_normalized}=    Normalize Path    ${server_dir}
    # Get current environment and add PYTHONIOENCODING for Unicode support on Windows
    ${env}=    Get Environment Variables
    Set To Dictionary    ${env}    PYTHONIOENCODING    utf-8
    # Start process using Process library with environment variables
    ${stdout_file}=    Join Path    ${TEMPDIR}    server_stdout.txt
    ${stderr_file}=    Join Path    ${TEMPDIR}    server_stderr.txt
    Start Process    python    ${server_path_normalized}    cwd=${server_dir_normalized}    alias=dashboard_server    shell=False    env=${env}    stdout=${stdout_file}    stderr=${stderr_file}
    Log    Started server process with PYTHONIOENCODING=utf-8
    # #region agent log
    ${is_running}=    Run Keyword And Return Status    Process Should Be Running    dashboard_server
    Log    Process started - Is running: ${is_running}
    # #endregion
    Sleep    5s    # Initial wait for server to start (Flask may take time to initialize)
    # Check if process is still running after initial wait
    ${is_running_after}=    Run Keyword And Return Status    Process Should Be Running    dashboard_server
    Log    After 5s wait - Process is running: ${is_running_after}
    # Verify server is running by making actual requests
    ${status}=    Set Variable    ${False}
    FOR    ${i}    IN RANGE    30
        ${process_running}=    Run Keyword And Return Status    Process Should Be Running    dashboard_server
        Log    Attempt ${i+1}/30: Process running=${process_running}
        ${status}=    Check Server Running
        Log    Attempt ${i+1}/30: Server check result=${status}
        Run Keyword If    ${status}    Exit For Loop
        Log    Attempt ${i+1}/30: Server not ready yet, waiting...
        Sleep    1s
    END
    Run Keyword If    not ${status}    Fail    Dashboard server failed to start after 30 attempts (35 seconds total). Check if port 5000 is available, Python/Flask are installed, and server path is correct: ${server_path}
    Log    Dashboard server started successfully and is accessible

Check Server Running
    [Documentation]    Check if dashboard server is running by making an actual HTTP request
    # Clean up any existing sessions first to avoid conflicts
    Run Keyword And Ignore Error    Delete All Sessions
    # Try to create session and make request - use longer timeout for slow startup
    ${session_status}=    Run Keyword And Return Status    Create Session    server_check    ${DASHBOARD_URL}    timeout=10
    IF    not ${session_status}
        RETURN    ${False}
    END
    # Make actual request to verify server is responding
    ${request_status}=    Run Keyword And Return Status    GET On Session    server_check    /    timeout=10
    # Clean up session
    Run Keyword And Ignore Error    Delete All Sessions
    RETURN    ${request_status}

Stop Dashboard Server
    [Documentation]    Stop Flask dashboard server
    ${status}=    Run Keyword And Return Status    Terminate Process    dashboard_server
    Run Keyword If    ${status}    Log    Dashboard server stopped successfully
    ...    ELSE    Log    Dashboard server was not running or already stopped

Wait For Page Load
    [Documentation]    Wait for page to fully load
    [Arguments]    ${timeout}=${PAGE_LOAD_TIMEOUT}
    # Wait for body element with longer timeout
    Wait Until Page Contains Element    body    timeout=${timeout}    error=Page did not load within ${timeout}
    # Wait for document ready state
    Wait Until Keyword Succeeds    5x    2s    Execute JavaScript    return document.readyState === 'complete'
    Sleep    2s    # Additional wait for dynamic content to render

Open Dashboard Homepage
    [Documentation]    Open dashboard homepage
    [Arguments]    ${url}=${DASHBOARD_URL}
    Log    Opening browser to ${url}
    # Verify server is accessible before opening browser
    ${server_ready}=    Check Server Running
    Run Keyword If    not ${server_ready}    Fail    Server is not ready before opening browser
    Open Browser    ${url}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Implicit Wait    ${IMPLICIT_WAIT}
    # Wait for page to load - use longer timeout for initial load
    Wait Until Page Contains Element    body    timeout=60s    error=Homepage did not load within 60 seconds
    Sleep    3s    # Additional wait for dynamic content to render

Close Dashboard Browser
    [Documentation]    Close browser
    Close All Browsers

Take Screenshot On Failure
    [Documentation]    Take screenshot on test failure
    Run Keyword If Test Failed    Capture Page Screenshot    ${OUTPUT_DIR}/failure-{index}.png

Verify Element Is Visible
    [Documentation]    Verify element is visible
    [Arguments]    ${locator}    ${timeout}=${IMPLICIT_WAIT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Element Should Be Visible    ${locator}

Verify Element Contains Text
    [Documentation]    Verify element contains expected text
    [Arguments]    ${locator}    ${expected_text}
    Wait Until Element Is Visible    ${locator}
    Element Should Contain    ${locator}    ${expected_text}

Get Element Text
    [Documentation]    Get text from element
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}
    ${text}=    Get Text    ${locator}
    RETURN    ${text}

Click Element Safely
    [Documentation]    Click element with wait
    [Arguments]    ${locator}    ${timeout}=${IMPLICIT_WAIT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Wait Until Element Is Enabled    ${locator}    timeout=${timeout}
    Click Element    ${locator}
