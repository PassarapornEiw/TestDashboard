*** Settings ***
Documentation    Browser Configuration
Library          ../resources/libraries/config_reader.py

*** Variables ***
${CONFIG_READER}    ConfigReader

*** Keywords ***
Load Browser Configuration
    [Documentation]    Load browser configuration from LDP_UI.yaml
    ${config_reader}=    Get Library Instance    ConfigReader
    ${browser_name}=    Call Method    ${config_reader}    get_browser_name
    ${browser_options}=    Call Method    ${config_reader}    get_browser_options
    [Return]    ${browser_name}    ${browser_options}

Get Enabled Browsers
    [Documentation]    Get list of enabled browsers
    ${config_reader}=    Get Library Instance    ConfigReader
    ${browsers}=    Call Method    ${config_reader}    get_enabled_browsers
    [Return]    ${browsers}






