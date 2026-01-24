*** Settings ***
Documentation    Navigation Flow Tests
Resource    ../../resources/variables/config.robot
Resource    ../../resources/variables/selectors.robot
Resource    ../../resources/keywords/common_keywords.robot
Resource    ../../resources/keywords/homepage_keywords.robot
Resource    ../../resources/keywords/dashboard_keywords.robot
Library    SeleniumLibrary

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
TC_NAV_001: Verify Homepage To Dashboard Navigation Flow
    [Documentation]    Verify Homepage → Dashboard navigation flow
    [Tags]    smoke    navigation
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Click Project Card    ${project_name}
    Verify Dashboard Loaded
    Verify Dashboard URL    ${project_name}

TC_NAV_002: Verify Dashboard To Homepage Navigation Flow
    [Documentation]    Verify Dashboard → Homepage navigation flow
    [Tags]    smoke    navigation
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Click Project Card    ${project_name}
    Wait For Page Load
    Click Back To Homepage
    Location Should Be    ${DASHBOARD_URL}/
    Wait Until Element Is Visible    ${HP_PROJECTS_GRID}

TC_NAV_003: Verify Project Selection From Homepage
    [Documentation]    Verify project selection from Homepage
    [Tags]    navigation
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Click Project Card    ${project_name}
    ${current_url}=    Get Location
    Should Contain    ${current_url}    project=${project_name}

TC_NAV_004: Verify URL Parameters Handling
    [Documentation]    Verify URL parameters handling
    [Tags]    navigation
    ${count}=    Get Project Count
    Skip If    ${count} == 0    No projects available
    ${stats}=    Get Project Stats    0
    ${project_name}=    Get From Dictionary    ${stats}    name
    Go To    ${DASHBOARD_URL}/dashboard?project=${project_name}
    Wait For Page Load
    Verify Dashboard URL    ${project_name}
