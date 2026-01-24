*** Settings ***
Resource    ../variables/config.robot
Resource    ../variables/selectors.robot
Resource    common_keywords.robot
Library    SeleniumLibrary
Library    Collections
Library    String

*** Keywords ***
Get Project Cards
    [Documentation]    Get all project card elements
    Wait Until Element Is Visible    ${HP_PROJECTS_GRID}
    ${cards}=    Get WebElements    ${HP_PROJECT_CARD}
    RETURN    ${cards}

Get Project Count
    [Documentation]    Get number of project cards
    ${cards}=    Get Project Cards
    ${count}=    Get Length    ${cards}
    RETURN    ${count}

Get Project Stats
    [Documentation]    Extract project statistics from card
    [Arguments]    ${card_index}=0
    ${cards}=    Get Project Cards
    ${card}=    Get From List    ${cards}    ${card_index}
    ${name_elem}=    Find Child Element    ${card}    ${HP_PROJECT_NAME}
    ${name}=    Get Text    ${name_elem}
    ${pass_rate_elem}=    Find Child Element    ${card}    ${HP_PROJECT_PASS_RATE}
    ${pass_rate}=    Get Text    ${pass_rate_elem}
    ${total_tests_elem}=    Find Child Element    ${card}    ${HP_PROJECT_TOTAL_TESTS}
    ${total_tests}=    Get Text    ${total_tests_elem}
    ${last_run_elem}=    Find Child Element    ${card}    ${HP_PROJECT_LAST_RUN}
    ${last_run}=    Get Text    ${last_run_elem}
    ${stats}=    Create Dictionary    name=${name}    pass_rate=${pass_rate}    total_tests=${total_tests}    last_run=${last_run}
    RETURN    ${stats}

Click Project Card
    [Documentation]    Click on project card
    [Arguments]    ${project_name}
    ${cards}=    Get Project Cards
    FOR    ${card}    IN    @{cards}
        ${name_elem}=    Find Child Element    ${card}    ${HP_PROJECT_NAME}
        ${name}=    Get Text    ${name_elem}
        Exit For Loop If    '${name}' == '${project_name}'
    END
    Click Element    ${card}
    Wait For Page Load

Verify Project Card Display
    [Documentation]    Verify card displays correctly
    [Arguments]    ${card_index}=0
    ${cards}=    Get Project Cards
    ${card}=    Get From List    ${cards}    ${card_index}
    ${name_elem}=    Find Child Element    ${card}    ${HP_PROJECT_NAME}
    ${pass_rate_elem}=    Find Child Element    ${card}    ${HP_PROJECT_PASS_RATE}
    ${total_tests_elem}=    Find Child Element    ${card}    ${HP_PROJECT_TOTAL_TESTS}
    ${last_run_elem}=    Find Child Element    ${card}    ${HP_PROJECT_LAST_RUN}
    Element Should Be Visible    ${name_elem}
    Element Should Be Visible    ${pass_rate_elem}
    Element Should Be Visible    ${total_tests_elem}
    Element Should Be Visible    ${last_run_elem}

Verify Loading State
    [Documentation]    Verify loading state is displayed
    Wait Until Element Is Visible    ${HP_LOADING}    timeout=5s
    Element Should Contain    ${HP_LOADING}    กำลังโหลด

Verify Error State
    [Documentation]    Verify error state is displayed
    Wait Until Element Is Visible    ${HP_ERROR}    timeout=5s
    Element Should Be Visible    ${HP_ERROR}

Verify Empty State
    [Documentation]    Verify empty state is displayed
    Wait Until Element Is Visible    ${HP_NO_PROJECTS}    timeout=5s
    Element Should Be Visible    ${HP_NO_PROJECTS}

Verify Project Card Color
    [Documentation]    Verify project card color based on pass rate
    [Arguments]    ${expected_color}    ${card_index}=0
    ${cards}=    Get Project Cards
    ${card}=    Get From List    ${cards}    ${card_index}
    ${pass_rate_elem}=    Find Child Element    ${card}    ${HP_PROJECT_PASS_RATE}
    ${color}=    Call Method    ${pass_rate_elem}    value_of_css_property    color
    Should Contain    ${color}    ${expected_color}

Find Child Element
    [Documentation]    Find child element within parent WebElement using Execute Javascript
    [Arguments]    ${parent_element}    ${child_locator}
    # Extract selector value (remove prefix like "css:", "id:", etc.)
    ${selector_value}=    Remove String    ${child_locator}    css:    id:
    # Use Execute Javascript to find child element within parent
    ${child_elem}=    Execute Javascript    return arguments[0].querySelector('${selector_value}');    ARGUMENTS    ${parent_element}
    RETURN    ${child_elem}
