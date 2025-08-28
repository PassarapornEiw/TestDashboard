# Dashboard Report Specification
## Test Automation Dashboard - Technical Specification Document

### 1. ภาพรวมระบบ (System Overview)
Dashboard Report เป็นระบบแสดงผลและจัดการข้อมูลผลการทดสอบอัตโนมัติที่สร้างขึ้นจาก Robot Framework โดยมีฟีเจอร์หลักดังนี้:
- แสดงผลสรุปการทดสอบแบบ Real-time
- จัดการข้อมูลตาม Timestamp และ Feature
- สร้าง PDF Report
- แสดงผล Evidence และ Screenshot
- จัดการ Excel Data Preview

---

## 2. ส่วนประกอบหลัก (Main Components)

### 2.1 Latest Test Result (Section 1)
**ตำแหน่ง**: ส่วนบนของหน้า Dashboard
**วัตถุประสงค์**: แสดงผลการทดสอบล่าสุดและสถิติสรุป

#### 2.1.1 Summary Cards (5 Cards)
- **Total Executed**: จำนวน Test Case ทั้งหมดที่รัน
- **Passed**: จำนวน Test Case ที่ผ่าน (PASS)
- **FAIL (Major)**: จำนวน Test Case ที่ล้มเหลวระดับ Major
- **FAIL (Blocker)**: จำนวน Test Case ที่ล้มเหลวระดับ Blocker
- **Pass Rate**: อัตราการผ่านเป็นเปอร์เซ็นต์

**รองรับ 4 statuses หลัก**:
- **PASS**: ทดสอบผ่าน (สีเขียว #28a745)
- **FAIL (Major)**: ล้มเหลวระดับ Major (สีส้ม #ff5722)
- **FAIL (Blocker)**: ล้มเหลวระดับ Blocker (สีแดง #e51c23)
- **UNKNOWN**: ไม่ทราบสถานะ (สีเทา #6c757d)

#### 2.1.2 Pie Chart
- แสดงกราฟวงกลมของผลการทดสอบ
- ใช้ Chart.js library
- แสดงสัดส่วน 3 statuses: Pass (สีเขียว) / FAIL Major (สีส้ม) / FAIL Blocker (สีแดง)

#### 2.1.3 Latest Run Information
- แสดงข้อมูลการรันล่าสุด
- Timestamp ของการรัน
- จำนวน Feature ที่รัน
- สถานะการรันล่าสุด

#### 2.1.4 Action Buttons
- **Download PDF**: ดาวน์โหลด PDF ของการรันล่าสุด
- **Robot Report**: เปิด Robot Report HTML

### 2.2 History Section (Section 2)
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
- **Column Header**: "Summary (Total) Passed/Failed Major/Failed Blocker"

---

## 3. ฟีเจอร์การทำงาน (Functional Features)

### 3.1 View Details
**วัตถุประสงค์**: แสดงรายละเอียดของ Test Case และ Feature

#### 3.1.1 Modal Display
- แสดงข้อมูลในรูปแบบ Modal
- แสดงข้อมูล Test Case ทั้งหมดใน Feature
- แสดงสถานะและผลลัพธ์

#### 3.1.2 Test Case Information
- Test Case ID และ Description
- Expected Result
- Actual Result (ถ้ามี Error)
- Status Badge (Pass/FAIL Major/FAIL Blocker/Not Run) 
- Error Title แสดงระดับความรุนแรงของ Failure

#### 3.1.3 Evidence Display
- แสดง Screenshot และ Evidence
- รองรับการดูภาพแบบ Gallery
- แสดงข้อมูล Excel ที่เกี่ยวข้อง

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
- แสดงข้อมูล Test Case และ Evidence
- รองรับการแสดงผลภาษาไทย

#### 3.3.2 PDF Download in Main (Section 1 & 2)
- **Section 1**: ดาวน์โหลด PDF ของการรันล่าสุด
- **Section 2**: ดาวน์โหลด PDF ของการรันทั้งหมดใน Feature

#### 3.3.3 PDF Generation Features
- ใช้ ReportLab library
- รองรับฟอนต์ภาษาไทย
- แสดงข้อมูล Test Case และ Evidence
- รองรับการแสดงผลแบบ Full Page

---

## 4. Gallery และ Image Management

### 4.1 Gallery Modal
**วัตถุประสงค์**: แสดงภาพ Evidence และ Screenshot

#### 4.1.1 Modal Structure
- แสดงภาพในรูปแบบ Grid
- รองรับการคลิกเพื่อดูภาพขนาดใหญ่
- แสดงข้อมูลของแต่ละภาพ

#### 4.1.2 Image Display
- แสดงภาพแบบ Thumbnail
- รองรับการแสดงผลแบบ Responsive
- แสดงข้อมูลของแต่ละภาพ

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

### 5.1 Data Endpoints
- `/api/data`: ดึงข้อมูล Dashboard
- `/api/excel_preview`: แสดงผล Excel Preview
- `/api/export_pdf`: สร้าง PDF
- `/api/export_testcase_pdf`: สร้าง PDF ของ Test Case
- `/api/export_feature_pdfs_zip`: สร้าง ZIP ของ PDF ทั้งหมดใน Feature

### 5.2 Thumbnail Endpoints
- `/api/evidence_thumbnail`: สร้าง Thumbnail ของ Evidence
- `/api/html_thumbnail`: สร้าง Thumbnail ของ HTML
- `/api/thumbnail_info`: ข้อมูล Thumbnail
- `/api/clear_thumbnails`: ล้าง Thumbnail Cache

---

## 6. การจัดการข้อมูล (Data Management)

### 6.1 Excel Data Processing
- อ่านข้อมูลจาก Excel files
- แปลงข้อมูลเป็น DataFrame
- จัดการข้อมูลตาม Feature และ Test Case

### 6.2 Thumbnail Generation
- สร้าง Thumbnail จาก HTML และ Images
- ใช้ Playwright สำหรับ HTML rendering
- ใช้ PIL สำหรับ Image processing

### 6.3 Font Management
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

1. **FAIL (Blocker)** - Priority สูงสุด (สีแดง #e51c23)
2. **FAIL (Major)** - Priority ที่สอง (สีส้ม #ff5722)
3. **PASS** - Priority ที่สาม (สีเขียว #28a745)
4. **UNKNOWN** - Priority ต่ำสุด (สีเทา #6c757d)

### 8.2 Status Logic
- **Feature Level**: ถ้ามี test case เป็น blocker จะ stamp เป็น FAIL (Blocker)
- **Run Level**: ถ้ามี feature ใดๆ เป็น blocker จะ stamp เป็น FAIL (Blocker)
- **Fallback Logic**: รองรับ legacy status และมีการตรวจสอบ priority ที่ถูกต้อง

### 8.3 Status Badge Display
- **PASS**: แสดงเป็น "PASS"
- **FAIL (Major)**: แสดงเป็น "FAIL (Major)"
- **FAIL (Blocker)**: แสดงเป็น "FAIL (Blocker)"
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

## 10. การบำรุงรักษาและ Update

### 10.1 Color Scheme Management
- สีหลักของระบบสามารถปรับเปลี่ยนได้ง่าย
- ใช้ CSS variables สำหรับสีหลัก
- รองรับการปรับเปลี่ยนสีแบบ centralized

### 10.2 Status Management
- รองรับการเพิ่ม status ใหม่
- รองรับการปรับเปลี่ยน priority
- รองรับการปรับเปลี่ยนข้อความแสดงผล
