# PythonProject – Robot Framework และการอ่าน Config จาก YAML

โปรเจกต์นี้เป็นชุดเทสต์ Robot Framework ที่อ่านค่าตั้งค่าจาก `Environment/DRDB_Config.yaml` ผ่าน Python libraries (ConfigReader, DataReader) และ BaseLibrary

---

## ความต้องการของระบบ

- **Python**: 3.8 ขึ้นไป
- **Robot Framework**: ติดตั้งผ่าน pip (`pip install robotframework`)
- **Libraries ที่ใช้ใน test**:
  - SeleniumLibrary
  - RequestsLibrary
  - Collections, OperatingSystem, Screenshot, String, DateTime (มาตรฐานของ Robot)
- **PyYAML**: สำหรับ BaseLibrary โหลดไฟล์ YAML (`pip install pyyaml`)

ติดตั้งครบด้วยคำสั่ง:

```text
pip install robotframework robotframework-seleniumlibrary robotframework-requests pyyaml
```

---

## โครงสร้างโฟลเดอร์

| โฟลเดอร์/ไฟล์ | คำอธิบาย |
|----------------|----------|
| `test.robot` | ไฟล์เทสต์หลัก มี Test Cases และ Keywords ตัวอย่างการดึงค่าจาก YAML |
| `Environment/` | เก็บไฟล์ config ของ suite |
| `Environment/DRDB_Config.yaml` | ไฟล์ตั้งค่าหลัก (Input_Test_Data, LDP_environment, DRDB_environment, SMSSmart_environment) |
| `Resources/pythonLib/` | Python libraries ที่ใช้ในเทสต์ |
| `Resources/pythonLib/base_library.py` | Base class โหลด YAML, cache, และ resolve path จาก project root |
| `Resources/pythonLib/config_reader.py` | อ่านค่าต่างๆ จาก config (browser, LDP URL, DRDB URL, SMSSmart, test data file) |
| `Resources/pythonLib/data_reader.py` | ดึงค่าด้วย dotted path และโหลดทั้ง section เป็นตัวแปร Robot |

Project root สำหรับ path ใน config คือโฟลเดอร์ที่เก็บ `test.robot` (PythonProject) ดังนั้น `Environment/DRDB_Config.yaml` จะถูก resolve จากโฟลเดอร์นั้น

---

## การตั้งค่า Config

แก้ไข `Environment/DRDB_Config.yaml` ตาม environment จริง

- **Input_Test_Data**: ชื่อไฟล์ input (เช่น GDR_InputFileName, ert_InputFileName)
- **LDP_environment**: `ldp_base_url`, `timeout`, `implicit_wait`
- **DRDB_environment**: `drdb_base_url`, `sheet_name`, `output_dir` เป็นต้น
- **SMSSmart_environment**: `username`, `password`, `sms_url`

 path ที่ใส่ใน YAML ถ้าเป็น relative จะถูก resolve จาก project root เมื่อใช้ผ่าน BaseLibrary/DataReader (เช่น ใน `build_section_paths_from_settings`)

---

## วิธีรันเทสต์

จากโฟลเดอร์ PythonProject (โฟลเดอร์ที่มี `test.robot`):

```text
robot test.robot
```

รันเฉพาะเทสต์บางตัว:

```text
robot --test "Example 01*" test.robot
```

ผลลัพธ์: `report.html`, `log.html`, `output.xml` จะถูกสร้างในโฟลเดอร์เดียวกัน (หรือตาม output dir ที่ตั้งใน config)

---

## Keyword หลักที่ใช้บ่อย

### Get From Settings

ดึงค่าจาก YAML ด้วย dotted path (เช่น `Input_Test_Data.GDR_InputFileName`)

- **Arguments**: `dotted_path`, `default` (optional), `settings_path` (optional)
- **ตัวอย่าง**:  
  `${filename}=    Get From Settings    Input_Test_Data.GDR_InputFileName`  
  `${timeout}=     Get From Settings    LDP_environment.timeout    default=30`

### Load Section From Settings

โหลดทั้ง section จาก YAML แล้วตั้งเป็น suite variables ชื่อรูปแบบ `SECTION_KEY` (เช่น `INPUT_TEST_DATA_GDR_INPUTFILENAME`)

- **Arguments**: `section`, `prefix` (optional), `settings_path` (optional)
- **ตัวอย่าง**:  
  `Load Section From Settings    Input_Test_Data`  
  จากนั้นใช้ตัวแปรเช่น `${INPUT_TEST_DATA_GDR_INPUTFILENAME}`

### ConfigReader

ใช้เมื่อต้องการดึงค่าที่มี helper เตรียมไว้แล้ว:

- `ConfigReader.Get Ldp Base Url`
- `ConfigReader.Get Drdb Base Url`
- `ConfigReader.Get Test Data File`
- `ConfigReader.Get Timeout`, `ConfigReader.Get Implicit Wait`
- `ConfigReader.Get Sms Smart Username`, `ConfigReader.Get Sms Smart Password`, `ConfigReader.Get Sms Smart Url`

---

## ตัวอย่างค่าใน YAML และการเรียกใช้ใน Test Case

**ใน `DRDB_Config.yaml` (ตัวอย่าง):**

```yaml
Input_Test_Data:
  GDR_InputFileName: GDR_InputFileName.xlsx
  ert_InputFileName: ert_InputFileName.xlsx

LDP_environment:
  ldp_base_url: https://example.com/ldp
  timeout: 30
  implicit_wait: 10

DRDB_environment:
  drdb_base_url: https://example.com/drdb
  sheet_name: Sheet1
```

**ใน test.robot (อ้างอิงจาก Example 01–05):**

- **Example 01**: ดึงค่าด้วย dotted path  
  `${filename}=    Get From Settings    Input_Test_Data.GDR_InputFileName`

- **Example 02**: ดึงหลายค่าจาก section เดียว  
  `${url}=    Get From Settings    LDP_environment.ldp_base_url`  
  `${timeout}=    Get From Settings    LDP_environment.timeout    default=30`

- **Example 03**: โหลดทั้ง section แล้วใช้ตัวแปร  
  `Load Section From Settings    Input_Test_Data`  
  ใช้ `${INPUT_TEST_DATA_GDR_INPUTFILENAME}`, `${INPUT_TEST_DATA_ERT_INPUTFILENAME}`

- **Example 04**: ดึงค่าผสมจากหลาย section  
  `Get From Settings    DRDB_environment.drdb_base_url`, `SMSSmart_environment.username`, `DRDB_environment.sheet_name`

- **Example 05**: ใช้ ConfigReader  
  `ConfigReader.Get Ldp Base Url`, `ConfigReader.Get Drdb Base Url`, `ConfigReader.Get Test Data File`
