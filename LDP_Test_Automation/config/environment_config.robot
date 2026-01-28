*** Settings ***
Documentation    Environment Configuration
Library          ../resources/libraries/config_reader.py

*** Variables ***
${CONFIG_READER}    ConfigReader

*** Keywords ***
Load Environment Configuration
    [Documentation]    Load environment configuration from settings.json
    ${config_reader}=    Get Library Instance    ConfigReader
    ${base_url}=    Call Method    ${config_reader}    get_base_url
    ${timeout}=    Call Method    ${config_reader}    get_timeout
    ${implicit_wait}=    Call Method    ${config_reader}    get_implicit_wait
    [Return]    ${base_url}    ${timeout}    ${implicit_wait}






