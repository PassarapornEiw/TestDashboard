# test.robot
# ตัวอย่างการเรียกตัวแปรจาก Environment/DRDB_Config.yaml มาใช้ใน test
*** Settings ***

Library    SeleniumLibrary
Library    RequestsLibrary
Library    Collections
Library    OperatingSystem
Library    Screenshot
Library    String
Library    DateTime
# Library    Mainframe3270

# library    xReader    AS    DRDB_Input
# Library    xReader    AS    Master

Library    ${CURDIR}/Resources/pythonLib/config_reader.py    WITH NAME    ConfigReader
Library    ${CURDIR}/Resources/pythonLib/data_reader.py    WITH NAME    DataReader

*** Test Cases ***
Verify Get From Settings
    Log GDR Input File Name

# ตัวอย่างที่ 1: ดึงค่าด้วย dotted path (เช่น Input_Test_Data.GDR_InputFileName)
Example 01 Get Single Value From YAML
    ${filename}=    Get From Settings    Input_Test_Data.GDR_InputFileName
    Log    ใช้ค่าจาก YAML: ${filename}
    Should Be Equal As Strings    ${filename}    GDR_InputFileName.xlsx

# ตัวอย่างที่ 2: ดึงค่าหลายค่าจาก section เดียว (LDP_environment)
Example 02 Use LDP Environment Variables
    ${url}=    Get From Settings    LDP_environment.ldp_base_url
    ${timeout}=    Get From Settings    LDP_environment.timeout    default=30
    Log    LDP URL: ${url}, Timeout: ${timeout}

# ตัวอย่างที่ 3: โหลดทั้ง section เป็นตัวแปร Robot แล้วใช้
Example 03 Load Section And Use Variables
    Load Section From Settings    Input_Test_Data
    Log    ใช้ตัวแปรที่โหลดจาก YAML:
    Log To Console   - GDR file: ${INPUT_TEST_DATA_GDR_INPUTFILENAME}
    Log To Console   - ERT file: ${INPUT_TEST_DATA_ERT_INPUTFILENAME}

# ตัวอย่างที่ 4: โหลดหลาย section แล้วใช้ค่าผสม
Example 04 Use Multiple Sections From YAML
    ${drdb_url}=    Get From Settings    DRDB_environment.drdb_base_url
    ${sms_user}=    Get From Settings    SMSSmart_environment.username
    ${sheet}=       Get From Settings    DRDB_environment.sheet_name    default=Sheet1
    Log    DRDB URL=${drdb_url}, SMS user=${sms_user}, Sheet=${sheet}

# ตัวอย่างที่ 5: ใช้ ConfigReader ดึง URL และ test data file
Example 05 Use ConfigReader For URLs And Test Data
    ${ldp_url}=     ConfigReader.Get Ldp Base Url
    ${drdb_url}=    ConfigReader.Get Drdb Base Url
    ${test_file}=   ConfigReader.Get Test Data File
    Log    LDP URL: ${ldp_url}, DRDB URL: ${drdb_url}, Test data file: ${test_file}

*** Keywords ***
Log GDR Input File Name
    ${value}=    Get From Settings    Input_Test_Data.GDR_InputFileName
    Log    ${value}

# ดึงค่าด้วย dotted path จาก DRDB_Config.yaml (เช่น Input_Test_Data.GDR_InputFileName)
Get From Settings
    [Arguments]    ${dotted_path}=Input_Test_Data.GDR_InputFileName    ${default}=${None}    ${settings_path}=${None}
    ${instance}=    Get Library Instance    DataReader
    ${value}=    Call Method    ${instance}    get_from_settings    ${dotted_path}    ${default}    ${settings_path}
    RETURN    ${value}

# โหลดทั้ง section จาก YAML แล้วตั้งเป็นตัวแปร Robot ใน scope ปัจจุบัน (ชื่อแบบ SECTION_KEY)
Load Section From Settings
    [Arguments]    ${section}=Input_Test_Data    ${prefix}=${None}    ${settings_path}=${None}
    ${instance}=    Get Library Instance    DataReader
    ${section_dict}=    Call Method    ${instance}    load_section_from_settings    ${section}    ${prefix}    suite    ${settings_path}
    RETURN    ${section_dict}