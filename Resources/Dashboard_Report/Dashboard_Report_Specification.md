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

#### 2.1.1 Summary Cards
- **Total Executed**: จำนวน Test Case ทั้งหมดที่รัน
- **Passed**: จำนวน Test Case ที่ผ่าน
- **Failed**: จำนวน Test Case ที่ล้มเหลว  
- **Pass Rate**: อัตราการผ่านเป็นเปอร์เซ็นต์

#### 2.1.2 Pie Chart
- แสดงกราฟวงกลมของผลการทดสอบ
- ใช้ Chart.js library
- แสดงสัดส่วน Pass/Fail แบบ Visual

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
- Status Badge (Pass/Fail/Not Run)

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
- User-friendly error messages

---

## 8. การทำงานของระบบ (System Workflow)

### 8.1 การเริ่มต้นระบบ
1. โหลดข้อมูลจาก Results directory
2. สร้าง Thumbnail cache
3. แสดงผล Dashboard

### 8.2 การอัปเดตข้อมูล
1. อ่านข้อมูลใหม่จาก Results directory
2. อัปเดต Thumbnail cache
3. รีเฟรช UI

### 8.3 การสร้าง PDF
1. รับคำขอจาก User
2. สร้าง PDF content
3. ส่งไฟล์กลับไปยัง User

---

## 9. การจัดการ Performance

### 9.1 Thumbnail Caching
- สร้าง Thumbnail ไว้ล่วงหน้า
- ล้าง Cache ตามเวลาที่กำหนด
- ใช้ Memory และ Disk cache

### 9.2 Lazy Loading
- โหลดข้อมูลเมื่อจำเป็น
- ใช้ Pagination สำหรับข้อมูลจำนวนมาก
- Optimize การโหลด Images

---

## 10. การรักษาความปลอดภัย (Security)

### 10.1 File Access
- จำกัดการเข้าถึงไฟล์เฉพาะ Results directory
- Validate file paths
- Sanitize user inputs

### 10.2 Error Handling
- ไม่เปิดเผยข้อมูลระบบ
- Log errors อย่างเหมาะสม
- User-friendly error messages

---

## 11. การติดตั้งและ Deployment

### 11.1 Dependencies
- Flask (Web framework)
- ReportLab (PDF generation)
- Playwright (HTML rendering)
- PIL/Pillow (Image processing)
- Pandas (Data processing)

### 11.2 Configuration
- Font configuration
- Directory paths
- Thumbnail settings

---

## 12. การบำรุงรักษา (Maintenance)

### 12.1 Cache Management
- ล้าง Thumbnail cache ตามกำหนด
- จัดการ Disk space
- Monitor performance

### 12.2 Log Management
- Log การทำงานของระบบ
- Error logging
- Performance monitoring

---

## 13. การทดสอบ (Testing)

### 13.1 Unit Testing
- ทดสอบฟังก์ชันหลัก
- ทดสอบ API endpoints
- ทดสอบ PDF generation

### 13.2 Integration Testing
- ทดสอบการทำงานร่วมกันของระบบ
- ทดสอบการแสดงผล
- ทดสอบการจัดการข้อมูล

---

## 14. การพัฒนาต่อ (Future Development)

### 14.1 Planned Features
- Real-time updates
- Advanced filtering
- Custom report templates
- Export to other formats

### 14.2 Scalability Improvements
- Database integration
- Caching improvements
- Performance optimization

---

## 15. สรุป (Conclusion)

Dashboard Report เป็นระบบที่ครบครันสำหรับการจัดการและแสดงผลข้อมูลการทดสอบอัตโนมัติ โดยมีฟีเจอร์ที่ครอบคลุมตั้งแต่การแสดงผลข้อมูล การสร้างรายงาน การจัดการภาพ และการ Export ข้อมูลในรูปแบบต่างๆ ระบบได้รับการออกแบบให้ใช้งานง่าย มีประสิทธิภาพ และรองรับการใช้งานในสภาพแวดล้อมการทำงานจริง
