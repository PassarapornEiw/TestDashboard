# Dashboard Report Specification
## Test Automation Dashboard - Technical Specification Document

### 1. ภาพรวมระบบ (System Overview)
Dashboard Report เป็นระบบแสดงผลและจัดการข้อมูลผลการทดสอบอัตโนมัติที่สร้างขึ้นจาก Robot Framework โดยมีฟีเจอร์หลักดังนี้:
- **Homepage**: หน้าเลือก Project ก่อนเข้าสู่ Dashboard
- แสดงผลสรุปการทดสอบแบบ Real-time
- จัดการข้อมูลตาม Timestamp และ Feature
- สร้าง PDF Report
- แสดงผล Evidence และ Screenshot
- จัดการ Excel Data Preview

**Navigation Flow**:
1. ผู้ใช้เข้าสู่ระบบผ่านหน้า Homepage (`/`)
2. เลือก Project ที่ต้องการดูผลการทดสอบ
3. ระบบนำไปยังหน้า Dashboard ของ Project ที่เลือก (`/dashboard?project=<project_name>`)
4. สามารถกลับไปหน้า Homepage ได้ตลอดเวลา

---

## 2. ส่วนประกอบหลัก (Main Components)

### 2.0 Homepage (Project Selection Page)
**ตำแหน่ง**: หน้าแรกของระบบ (`/`)
**วัตถุประสงค์**: แสดงรายการ Projects ทั้งหมดที่มีผลการทดสอบและให้ผู้ใช้เลือก Project ที่ต้องการดู

#### 2.0.1 Project Discovery
- ระบบจะค้นหา Projects จาก `Automation_Project` folder (configurable ผ่าน Environment Variable `AUTOMATION_PROJECT_DIR`)
- แสดงเฉพาะ Projects ที่มี `results` folder และมีข้อมูล timestamp folders ที่ถูกต้อง
- Path structure: `Automation_Project/<project_name>/results`

#### 2.0.2 Project Cards Display
แต่ละ Project Card แสดงข้อมูล:
- **Project Icon**: Icon แบบ rotating จากชุด icons ที่กำหนด
- **Project Name**: ชื่อ Project (ชื่อ folder)
- **Pass Rate**: อัตราการผ่านเป็นเปอร์เซ็นต์ (คำนวณจาก run ล่าสุด)
  - สีเขียว: ≥ 80%
  - สีน้ำเงิน: 50-79%
  - สีแดง: < 50%
- **Total Tests**: จำนวน Test Cases ทั้งหมดใน run ล่าสุด
- **Last Run**: วันที่และเวลาของการรันล่าสุด (format: DD/MM/YYYY HH:MM:SS)

#### 2.0.3 UI States
- **Loading State**: แสดงข้อความ "กำลังโหลดข้อมูล..." พร้อม animation
- **Error State**: แสดงข้อความ error เมื่อไม่สามารถโหลดข้อมูลได้
- **Empty State**: แสดงข้อความ "ไม่พบ Project ที่มีผลการทดสอบ" เมื่อไม่มี projects

#### 2.0.4 Navigation
- คลิกที่ Project Card → นำไปยังหน้า Dashboard ของ Project นั้น (`/dashboard?project=<project_name>`)
- Dashboard มีปุ่ม "← กลับหน้าแรก" เพื่อกลับไป Homepage

#### 2.0.5 Statistics Calculation
- Stats ถูกคำนวณจาก Excel files ใน run ล่าสุด (timestamp ล่าสุด)
- Aggregates ข้อมูลจากทุก Features ใน run นั้น
- Pass Rate = (Passed / Total) × 100

### 2.1 Dashboard Page
**ตำแหน่ง**: หน้า Dashboard (`/dashboard`)
**วัตถุประสงค์**: แสดงผลการทดสอบของ Project ที่เลือก

#### 2.1.1 Navigation Header
- แสดงชื่อ "🧪 Test Automation Dashboard"
- ปุ่ม "← กลับหน้าแรก" สำหรับกลับไป Homepage
- Style: Gradient background สีทอง (#f5d547 ถึง #f0c419)

### 2.2 Latest Test Result (Section 1)
**ตำแหน่ง**: ส่วนบนของหน้า Dashboard
**วัตถุประสงค์**: แสดงผลการทดสอบล่าสุดและสถิติสรุป

#### 2.1.1 Summary Cards (5 Cards)
- **Total Executed**: จำนวน Test Case ทั้งหมดที่รัน
- **Passed**: จำนวน Test Case ที่ผ่าน (PASS)
- **FAIL (Major)**: จำนวน Test Case ที่ล้มเหลวระดับ Major
- **FAIL (Block)**: จำนวน Test Case ที่ล้มเหลวระดับ Block
- **Pass Rate**: อัตราการผ่านเป็นเปอร์เซ็นต์

**รองรับ 4 statuses หลัก**:
- **PASS**: ทดสอบผ่าน (สีเขียว #28a745)
- **FAIL (Major)**: ล้มเหลวระดับ Major (สีส้ม #ff5722)
- **FAIL (Block)**: ล้มเหลวระดับ Block (สีแดง #e51c23)
- **UNKNOWN**: ไม่ทราบสถานะ (สีเทา #6c757d)

#### 2.1.2 Pie Chart
- แสดงกราฟวงกลมของผลการทดสอบ
- ใช้ Chart.js library
- แสดงสัดส่วน 3 statuses: Pass (สีเขียว) / FAIL Major (สีส้ม) / FAIL Block (สีแดง)

#### 2.1.3 Latest Run Information
- แสดงข้อมูลการรันล่าสุด
- Timestamp ของการรัน
- จำนวน Feature ที่รัน
- สถานะการรันล่าสุด

#### 2.1.4 Action Buttons
- **Download PDF**: ดาวน์โหลด PDF ของการรันล่าสุด
- **Robot Report**: เปิด Robot Report HTML

### 2.3 History Section (Section 2)
**ตำแหน่ง**: ส่วนกลางของหน้า Dashboard
**วัตถุประสงค์**: แสดงประวัติการรันทั้งหมดและข้อมูลรายละเอียด

#### 2.2.1 Tab Navigation
- **By Timestamp**: จัดกลุ่มตามเวลาการรัน
- **By Feature**: จัดกลุ่มตาม Feature

#### 2.2.2 Search Functionality
- ค้นหาข้อมูลในตาราง
- รองรับการค้นหาทั้ง Timestamp และ Feature

#### 2.2.3 Data Table
- แสดงข้อมูลการรันทั้งหมด
- แสดงสถิติของแต่ละ Feature
- รองรับการ Expand/Collapse
- **Column Header**: "Summary (Total) Passed/Failed Major/Failed Block"

---

## 3. ฟีเจอร์การทำงาน (Functional Features)

### 3.1 View Details
**วัตถุประสงค์**: แสดงรายละเอียดของ Test Case และ Feature ยึดจากไฟล์ excel ที่เกี่ยวข้อง

#### 3.1.1 Modal Display
- แสดงข้อมูลในรูปแบบ Modal
- แสดงข้อมูล Test Case ทั้งหมดใน Feature
- แสดงสถานะและผลลัพธ์

#### 3.1.2 Test Case Information
- Test Case ID และ Description
- Expected Result
- Actual Result (ถ้ามี Error)
- Status Badge (Pass/FAIL Major/FAIL Block/Not Run) 
- Error Title แสดงระดับความรุนแรงของ Failure

#### 3.1.3 Evidence Display
- แสดง Screenshot และ Evidence ซึ่งจะเอาจาก path ที่ระบุใน excel คอลัมภ์ "ResultFolder"
- รองรับการดูภาพแบบ Gallery
- **Centralized Sorting Logic**: ใช้ EvidenceProcessor สำหรับการเรียงลำดับไฟล์
  - Media files (images) เรียงตามเลขนำหน้าในชื่อไฟล์
  - Excel files แสดงท้ายสุดเสมอ (เรียงตามชื่อไฟล์)
- แสดงข้อมูล Excel ที่เกี่ยวข้อง (แสดงใน Gallery และ PDF)
- **Note**: HTML files ไม่ถูกแสดงเป็น evidence เนื่องจากมี screenshot PNG จาก automation อยู่แล้ว

### 3.2 Excel Preview
**วัตถุประสงค์**: แสดงข้อมูล Excel ในรูปแบบตาราง

#### 3.2.1 Data Parsing
- อ่านข้อมูลจาก Excel file
- แปลงข้อมูลเป็นรูปแบบตาราง
- แสดงข้อมูลใน Modal

#### 3.2.2 Table Display
- แสดงข้อมูลในรูปแบบตาราง
- รองรับการ Format ข้อมูล
- แสดงข้อมูลที่เกี่ยวข้องกับ Test Case

### 3.3 PDF Download

#### 3.3.1 PDF Download in View Details
- ดาวน์โหลด PDF ของ Test Case เดี่ยว
- แสดงข้อมูล Test Case และ Evidence ซึ่งจะเอาจาก path ที่ระบุใน excel คอลัมภ์ "ResultFolder"
- รองรับการแสดงผลภาษาไทย

#### 3.3.2 PDF Download in Main (Section 1 & 2)
- **Section 1**: ดาวน์โหลด PDF ของการรันล่าสุด
- **Section 2**: ดาวน์โหลด PDF ของการรันทั้งหมดใน Feature

#### 3.3.3 PDF Generation Features
- ใช้ ReportLab library
- รองรับฟอนต์ภาษาไทย
- แสดงข้อมูล Test Case และ Evidence
- **Centralized Sorting**: ใช้ EvidenceProcessor สำหรับการเรียงลำดับไฟล์
  - Media files (images) เรียงตามเลขนำหน้าในชื่อไฟล์
  - Excel files แสดงท้ายสุดเสมอ (แสดงเป็น placeholder image)
- **Excel Files Support**: แสดง Excel files ใน PDF เป็น placeholder image พร้อมชื่อไฟล์
- **Note**: HTML files ไม่ถูกแสดงใน PDF เนื่องจากมี screenshot PNG จาก automation อยู่แล้ว
- **Project-Specific Results**: PDF exports ใช้ project-specific results directory ตาม project parameter ที่ระบุ
- รองรับการแสดงผลแบบ Full Page

---

## 4. Gallery และ Image Management

### 4.1 Gallery Modal
**วัตถุประสงค์**: แสดงภาพ Evidence และ Screenshot ซึ่งจะเอาจาก path ที่ระบุใน excel คอลัมภ์ "ResultFolder"

#### 4.1.1 Modal Structure
- แสดงภาพในรูปแบบ Grid
- **Centralized Sorting**: ใช้ EvidenceProcessor สำหรับการเรียงลำดับไฟล์
  - Media files (images) เรียงตามเลขนำหน้าในชื่อไฟล์
  - Excel files แสดงท้ายสุดเสมอ
- รองรับการคลิกเพื่อดูภาพขนาดใหญ่
- แสดงข้อมูลของแต่ละภาพ
- **Excel Files**: แสดงเป็น thumbnail icon พร้อมชื่อไฟล์ (คลิกเพื่อดาวน์โหลด)

#### 4.1.2 Image Display
- แสดงภาพแบบ Thumbnail
- รองรับการแสดงผลแบบ Responsive
- แสดงข้อมูลของแต่ละภาพ
- **Note**: HTML files ไม่ถูกแสดงใน Gallery เนื่องจากมี screenshot PNG จาก automation อยู่แล้ว

### 4.2 LightGallery Integration
**วัตถุประสงค์**: จัดการการแสดงภาพแบบ Advanced

#### 4.2.1 LightGallery Features
- Zoom และ Fullscreen
- Navigation ระหว่างภาพ
- Keyboard shortcuts
- Touch gestures

#### 4.2.2 Integration
- ใช้ CDN ของ LightGallery
- รองรับการแสดงผลแบบ Responsive
- รองรับการแสดงผลแบบ Mobile

---

## 5. Backend API Endpoints

### 5.1 Page Routes
- `/`: Render Homepage (Project Selection Page)
- `/dashboard`: Render Dashboard Page (รองรับ query parameter `project`)

### 5.2 Data Endpoints
- `/api/projects`: ดึงรายการ Projects ทั้งหมดพร้อม Statistics
  - Response: `{ projects: [...], total_projects: number, automation_project_dir: string }`
  - Project object: `{ name: string, path: string, stats: { pass_rate, total_tests, passed, failed, last_run } }`
- `/api/data`: ดึงข้อมูล Dashboard
  - Query Parameters: `project` (optional) - ชื่อ Project ที่ต้องการดู
  - Backward Compatibility: หากไม่ระบุ `project` จะใช้ auto-discovered results directory
- `/api/excel_preview`: แสดงผล Excel Preview
- `/api/export_pdf`: สร้าง PDF
- `/api/export_testcase_pdf`: สร้าง PDF ของ Test Case
  - Method: POST
  - Request Body: `{ test_case_id, feature_name, run_timestamp, project (optional) }`
  - **Project Support**: รับ `project` parameter ใน request body หรือ query parameter
  - ใช้ project-specific results directory หากระบุ project
  - Backward Compatibility: หากไม่ระบุ `project` จะใช้ auto-discovered results directory
- `/api/export_feature_pdfs_zip`: สร้าง ZIP ของ PDF ทั้งหมดใน Feature
  - Method: POST
  - Request Body: `{ feature_name, run_timestamp, run_index, feature_index, project (optional) }`
  - **Project Support**: รับ `project` parameter ใน request body หรือ query parameter
  - ใช้ project-specific results directory หากระบุ project
  - Backward Compatibility: หากไม่ระบุ `project` จะใช้ auto-discovered results directory

### 5.3 Thumbnail Endpoints
- `/api/evidence_thumbnail`: สร้างและส่งคืน Thumbnail ของ Evidence files (Excel, Images)
  - Query Parameter: `path` - path ของไฟล์ relative to PROJECT_ROOT
  - รองรับไฟล์: `.xlsx`, `.xls`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`
  - สำหรับ Excel: ส่งคืน SVG placeholder
  - สำหรับ Images: ส่งคืนไฟล์รูปภาพโดยตรง
  - **Note**: HTML files ไม่ถูกใช้เป็น evidence (มี screenshot PNG อยู่แล้ว)
- `/api/html_thumbnail`: Legacy endpoint - redirect ไปยัง `/api/evidence_thumbnail`
- `/api/thumbnail_info`: ข้อมูล Thumbnail cache
  - Response: `{ total_thumbnails, cache_size_mb, folders, structure }`
- `/api/thumbnail_status`: สถานะ Thumbnail และข้อมูล cleanup
  - Response: `{ cache_info, old_structure, recommendations }`
- `/api/cleanup_old_thumbnails`: ลบ `.thumbnails` folders เก่า (POST method)
  - Response: `{ success, removed_directories, removed_files, removed_directories_list, errors }`

---

## 6. การจัดการข้อมูล (Data Management)

### 6.1 Project Management
- **Project Discovery**: ค้นหา Projects จาก `Automation_Project` folder
- **Results Validation**: ตรวจสอบว่า Project มี `results` folder และมี timestamp folders ที่ถูกต้อง
- **Path Configuration**: 
  - Default: `PROJECT_ROOT/Automation_Project`
  - Configurable via Environment Variable: `AUTOMATION_PROJECT_DIR`
- **Statistics Calculation**: คำนวณ stats จาก Excel files ใน run ล่าสุดของแต่ละ Project

### 6.2 Excel Data Processing
- อ่านข้อมูลจาก Excel files
- แปลงข้อมูลเป็น DataFrame
- จัดการข้อมูลตาม Feature และ Test Case
- **Evidence Collection**: ใช้ ResultFolder column เพื่อ collect evidence files
- **Evidence Sorting**: ใช้ EvidenceProcessor.collect_and_sort_evidence() เพื่อเรียงลำดับไฟล์

### 6.3 Evidence Processing และ Thumbnail Generation

#### 6.3.1 EvidenceProcessor Class
- **Centralized Evidence Processing**: ใช้ EvidenceProcessor class สำหรับจัดการ evidence files
- **Methods**:
  - `collect_and_sort_evidence()`: เรียงลำดับไฟล์ (media files ตามเลขนำหน้า, Excel files ท้ายสุด)
  - `extract_sort_key()`: สร้าง sort key สำหรับการเรียงลำดับ
  - `ensure_thumbnail_exists()`: ตรวจสอบและสร้าง thumbnail สำหรับ HTML files (legacy support)
  - `prepare_evidence_for_pdf()`: เตรียม evidence พร้อม thumbnails สำหรับ PDF generation
- **Evidence Collection**: HTML files ไม่ถูก collect เป็น evidence เนื่องจากมี screenshot PNG จาก automation อยู่แล้ว

#### 6.3.2 Evidence File Types
- **Supported Evidence Types**:
  - Image files: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp` (screenshots จาก automation)
  - Excel files: `.xlsx`, `.xls` (แสดงเป็น placeholder thumbnail)
- **Excluded Types**:
  - HTML files: ไม่ถูก collect เป็น evidence เนื่องจากมี screenshot PNG อยู่แล้ว
- **Note**: HTML thumbnail generation code ยังคงอยู่ในระบบเพื่อรองรับ legacy แต่จะไม่ถูกเรียกใช้

#### 6.3.3 Evidence Sorting Logic
- **Sorting Order**:
  1. Media files (images) เรียงตามเลขนำหน้าในชื่อไฟล์ (numeric sort)
  2. Excel files แสดงท้ายสุดเสมอ (alphabetical sort)
- **Consistent Behavior**: ใช้ sorting logic เดียวกันใน Gallery, PDF, และ ZIP exports
- **Performance**: Sort ครั้งเดียวตอน collect evidence, ไม่ต้อง sort ซ้ำในแต่ละ feature

### 6.4 Font Management
- รองรับฟอนต์ภาษาไทย
- ใช้ Unicode CID fonts
- Fallback ไปยัง TTF fonts

---

## 7. การแสดงผล (UI/UX)

### 7.1 Responsive Design
- รองรับการแสดงผลบน Mobile
- ใช้ CSS Grid และ Flexbox
- รองรับการแสดงผลแบบ Adaptive

### 7.2 Loading States
- แสดง Loading indicator
- Blocking overlay สำหรับ PDF generation
- Progress indication

### 7.3 Error Handling
- แสดงข้อความ Error ที่เหมาะสม
- Fallback mechanisms

---

## 8. Status Priority System

### 8.1 Status Priority Order
ระบบมีการให้ priority ตามลำดับความรุนแรง:

1. **FAIL (Block)** - Priority สูงสุด (สีแดง #e51c23)
2. **FAIL (Major)** - Priority ที่สอง (สีส้ม #ff5722)
3. **PASS** - Priority ที่สาม (สีเขียว #28a745)
4. **UNKNOWN** - Priority ต่ำสุด (สีเทา #6c757d)

### 8.2 Status Logic
- **Feature Level**: ถ้ามี test case เป็น block จะ stamp เป็น FAIL (Block)
- **Run Level**: ถ้ามี feature ใดๆ เป็น block จะ stamp เป็น FAIL (Block)
- **Fallback Logic**: รองรับ legacy status และมีการตรวจสอบ priority ที่ถูกต้อง

### 8.3 Status Badge Display
- **PASS**: แสดงเป็น "PASS"
- **FAIL (Major)**: แสดงเป็น "FAIL (Major)"
- **FAIL (Block)**: แสดงเป็น "FAIL (Block)"
- **UNKNOWN**: แสดงเป็น "UNKNOWN"

---

## 9. การทดสอบและ Validation

### 9.1 Status Validation
- ตรวจสอบ priority ของ status ที่ถูกต้อง
- ตรวจสอบการแสดงผลสีที่ถูกต้อง
- ตรวจสอบการแสดงข้อความที่ถูกต้อง

### 9.2 UI Validation
- ตรวจสอบการแสดงผล 5 cards ใน Section 1
- ตรวจสอบการแสดงผลสีในตาราง Summary
- ตรวจสอบการแสดงผลสีใน Pie Chart

---

## 10. Configuration และ Environment Variables

### 10.1 Automation Project Directory
- **Environment Variable**: `AUTOMATION_PROJECT_DIR`
- **Default Path**: `PROJECT_ROOT/Automation_Project`
- **Purpose**: กำหนด path ของ folder ที่เก็บ Automation Projects
- **Example**: `set AUTOMATION_PROJECT_DIR=C:\Projects\Automation_Project`

### 10.2 Results Directory (Legacy)
- **Environment Variable**: `RESULTS_DIR`
- **Purpose**: Override auto-discovery สำหรับ backward compatibility
- **Note**: ยังคงรองรับสำหรับระบบเดิม

---

## 11. การบำรุงรักษาและ Update

### 11.1 Color Scheme Management
- สีหลักของระบบสามารถปรับเปลี่ยนได้ง่าย
- ใช้ CSS variables สำหรับสีหลัก
- รองรับการปรับเปลี่ยนสีแบบ centralized

### 11.2 Status Management
- รองรับการเพิ่ม status ใหม่
- รองรับการปรับเปลี่ยน priority
- รองรับการปรับเปลี่ยนข้อความแสดงผล

### 11.3 Backward Compatibility
- ระบบยังคงรองรับการเข้าถึง Dashboard โดยตรง (`/dashboard`) โดยไม่มี project parameter
- ในกรณีนี้ระบบจะใช้ auto-discovery mechanism เดิม
- API `/api/data` ยังคงทำงานได้ทั้งแบบมีและไม่มี project parameter
- **PDF Export APIs** (`/api/export_testcase_pdf`, `/api/export_feature_pdfs_zip`):
  - รองรับ `project` parameter ใน request body หรือ query parameter
  - หากไม่ระบุ `project` จะใช้ auto-discovered results directory (backward compatible)
  - Frontend ส่ง `project` parameter อัตโนมัติจาก URL query parameter

### 11.4 Evidence Processing Optimization (Latest Update)
- **EvidenceProcessor Class**: Centralized class สำหรับจัดการ evidence files
  - `collect_and_sort_evidence()`: เรียงลำดับไฟล์ (media files ตามเลขนำหน้า, Excel files ท้ายสุด)
  - `ensure_thumbnail_exists()`: จัดการ HTML thumbnails (legacy support, ไม่ถูกเรียกใช้)
  - `prepare_evidence_for_pdf()`: เตรียม evidence สำหรับ PDF generation
- **Consistent Sorting**: ใช้ sorting logic เดียวกันใน Gallery, PDF, และ ZIP exports
- **Excel Files Support**: แสดง Excel files ใน Gallery และ PDF (แสดงท้ายสุดเสมอ)
- **HTML Files Exclusion**: HTML files ไม่ถูก collect เป็น evidence เนื่องจากมี screenshot PNG จาก automation อยู่แล้ว
- **Performance Improvements**: 
  - Sort ครั้งเดียวตอน collect evidence
  - Reuse thumbnails ระหว่าง Gallery, PDF, และ ZIP exports
  - ลด duplicate logic และ I/O operations
