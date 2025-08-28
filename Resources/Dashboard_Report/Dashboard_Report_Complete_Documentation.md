# Dashboard Report - Complete Documentation
## เอกสารครบถ้วนสำหรับ Dashboard Report

---

## 📋 สารบัญ (Table of Contents)

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [ส่วนประกอบหลัก](#2-ส่วนประกอบหลัก)
3. [ฟีเจอร์การทำงาน](#3-ฟีเจอร์การทำงาน)
4. [การใช้งาน](#4-การใช้งาน)
5. [รายละเอียดทางเทคนิค](#5-รายละเอียดทางเทคนิค)
6. [การบำรุงรักษา](#6-การบำรุงรักษา)
7. [การพัฒนาต่อ](#7-การพัฒนาต่อ)

---

## 1. ภาพรวมระบบ

### 1.1 วัตถุประสงค์
Dashboard Report เป็นระบบแสดงผลและจัดการข้อมูลผลการทดสอบอัตโนมัติที่สร้างขึ้นจาก Robot Framework โดยมีวัตถุประสงค์หลักเพื่อ:

- แสดงผลสรุปการทดสอบแบบ Real-time
- จัดการข้อมูลตาม Timestamp และ Feature
- สร้าง PDF Report ที่ครบถ้วน
- แสดงผล Evidence และ Screenshot
- จัดการ Excel Data Preview

### 1.2 สถาปัตยกรรมระบบ
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Source   │
│   (HTML/CSS/JS) │◄──►│   (Flask)       │◄──►│   (Results Dir) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Components │    │   API Endpoints │    │   Excel Files   │
│   - Charts      │    │   - Data        │    │   - HTML Files  │
│   - Tables      │    │   - PDF         │    │   - Images      │
│   - Modals      │    │   - Thumbnails  │    │   - Logs        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 2. ส่วนประกอบหลัก

### 2.1 Latest Test Result (Section 1)
**ตำแหน่ง**: ส่วนบนของหน้า Dashboard

#### 2.1.1 Summary Cards
- **Total Executed**: จำนวน Test Case ทั้งหมดที่รัน
- **Passed**: จำนวน Test Case ที่ผ่าน
- **Failed**: จำนวน Test Case ที่ล้มเหลว (รวม Major + Blocker)
- **Pass Rate**: อัตราการผ่านเป็นเปอร์เซ็นต์

**สถานะที่รองรับ**:
- **PASS**: ทดสอบผ่าน (สีเขียว)
- **FAIL (Major)**: ล้มเหลวระดับ Major (สีเหลือง/ส้ม)
- **FAIL (Blocker)**: ล้มเหลวระดับ Blocker (สีแดง)

#### 2.1.2 Pie Chart
- แสดงกราฟวงกลมของผลการทดสอบ
- ใช้ Chart.js library
- แสดงสัดส่วน 3 statuses: Pass (สีเขียว) / FAIL Major (สีเหลือง) / FAIL Blocker (สีแดง)

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

## 3. ฟีเจอร์การทำงาน

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

### 3.4 Gallery และ Image Management

#### 3.4.1 Gallery Modal
- แสดงภาพในรูปแบบ Grid
- รองรับการคลิกเพื่อดูภาพขนาดใหญ่
- แสดงข้อมูลของแต่ละภาพ

#### 3.4.2 LightGallery Integration
- Zoom และ Fullscreen
- Navigation ระหว่างภาพ
- Keyboard shortcuts
- Touch gestures

---

## 4. การใช้งาน

### 4.1 การเริ่มต้นใช้งาน
1. เปิดเว็บเบราว์เซอร์
2. ไปที่ URL ของ Dashboard Report
3. ระบบจะแสดงหน้า Dashboard หลัก

### 4.2 การดูข้อมูลล่าสุด
- ข้อมูลการทดสอบล่าสุดจะแสดงในส่วนบนของหน้า
- สถิติสรุปจะอัปเดตอัตโนมัติ
- กราฟวงกลมแสดงสัดส่วน Pass/Fail

### 4.3 การใช้งาน History Section
1. คลิกแท็บ "📅 By Timestamp" หรือ "🔧 By Feature"
2. ใช้ช่อง Search เพื่อค้นหาข้อมูล
3. คลิกที่แถวข้อมูลเพื่อขยาย/ย่อ

### 4.4 การดูรายละเอียด
1. คลิกที่ Feature ในตาราง
2. ระบบจะแสดง Modal แสดงรายละเอียด
3. ดูข้อมูล Test Case และ Evidence

### 4.5 การดาวน์โหลด PDF
1. คลิกปุ่ม "📄 PDF" ที่ต้องการ
2. ระบบจะสร้าง PDF
3. ไฟล์จะดาวน์โหลดอัตโนมัติ

### 4.6 การดูภาพ
1. คลิกที่ Evidence หรือ Screenshot
2. ระบบจะแสดง Gallery Modal
3. ใช้ LightGallery features เพื่อดูภาพ

---

## 5. รายละเอียดทางเทคนิค

### 5.1 Backend API Endpoints

#### 5.1.1 Data Endpoints
- `/api/data`: ดึงข้อมูล Dashboard
- `/api/excel_preview`: แสดงผล Excel Preview
- `/api/export_pdf`: สร้าง PDF
- `/api/export_testcase_pdf`: สร้าง PDF ของ Test Case
- `/api/export_feature_pdfs_zip`: สร้าง ZIP ของ PDF ทั้งหมดใน Feature

#### 5.1.2 Thumbnail Endpoints
- `/api/evidence_thumbnail`: สร้าง Thumbnail ของ Evidence
- `/api/html_thumbnail`: สร้าง Thumbnail ของ HTML
- `/api/thumbnail_info`: ข้อมูล Thumbnail
- `/api/clear_thumbnails`: ล้าง Thumbnail Cache

### 5.2 การจัดการข้อมูล

#### 5.2.1 Excel Data Processing
- อ่านข้อมูลจาก Excel files
- แปลงข้อมูลเป็น DataFrame
- จัดการข้อมูลตาม Feature และ Test Case

#### 5.2.2 Thumbnail Generation
- สร้าง Thumbnail จาก HTML และ Images
- ใช้ Playwright สำหรับ HTML rendering
- ใช้ PIL สำหรับ Image processing

#### 5.2.3 Font Management
- รองรับฟอนต์ภาษาไทย
- ใช้ Unicode CID fonts
- Fallback ไปยัง TTF fonts

### 5.3 การแสดงผล

#### 5.3.1 Responsive Design
- รองรับการแสดงผลบน Mobile
- ใช้ CSS Grid และ Flexbox
- รองรับการแสดงผลแบบ Adaptive

#### 5.3.2 Loading States
- แสดง Loading indicator
- Blocking overlay สำหรับ PDF generation
- Progress indication

#### 5.3.3 Error Handling
- แสดงข้อความ Error ที่เหมาะสม
- Fallback mechanisms
- User-friendly error messages

### 5.4 การจัดการ Performance

#### 5.4.1 Thumbnail Caching
- สร้าง Thumbnail ไว้ล่วงหน้า
- ล้าง Cache ตามเวลาที่กำหนด
- ใช้ Memory และ Disk cache

#### 5.4.2 Lazy Loading
- โหลดข้อมูลเมื่อจำเป็น
- ใช้ Pagination สำหรับข้อมูลจำนวนมาก
- Optimize การโหลด Images

### 5.5 การรักษาความปลอดภัย

#### 5.5.1 File Access
- จำกัดการเข้าถึงไฟล์เฉพาะ Results directory
- Validate file paths
- Sanitize user inputs

#### 5.5.2 Error Handling
- ไม่เปิดเผยข้อมูลระบบ
- Log errors อย่างเหมาะสม
- User-friendly error messages

---

## 6. การบำรุงรักษา

### 6.1 การติดตั้งและ Deployment

#### 6.1.1 Dependencies
- Flask (Web framework)
- ReportLab (PDF generation)
- Playwright (HTML rendering)
- PIL/Pillow (Image processing)
- Pandas (Data processing)

#### 6.1.2 Configuration
- Font configuration
- Directory paths
- Thumbnail settings

### 6.2 การบำรุงรักษา

#### 6.2.1 Cache Management
- ล้าง Thumbnail cache ตามกำหนด
- จัดการ Disk space
- Monitor performance

#### 6.2.2 Log Management
- Log การทำงานของระบบ
- Error logging
- Performance monitoring

### 6.3 การทดสอบ

#### 6.3.1 Unit Testing
- ทดสอบฟังก์ชันหลัก
- ทดสอบ API endpoints
- ทดสอบ PDF generation

#### 6.3.2 Integration Testing
- ทดสอบการทำงานร่วมกันของระบบ
- ทดสอบการแสดงผล
- ทดสอบการจัดการข้อมูล

---

## 7. การพัฒนาต่อ

### 7.1 Planned Features
- Real-time updates
- Advanced filtering
- Custom report templates
- Export to other formats

### 7.2 Scalability Improvements
- Database integration
- Caching improvements
- Performance optimization

### 7.3 Technical Enhancements
- API versioning
- Enhanced security
- Better error handling
- Performance monitoring

---

## 📊 ตารางสรุปฟีเจอร์

| ฟีเจอร์ | สถานะ | คำอธิบาย | การใช้งาน |
|---------|--------|----------|-----------|
| **Latest Test Result** | ✅ Active | แสดงผลการทดสอบล่าสุด | ดูสถิติและกราฟ 3 สถานะ |
| **History Section** | ✅ Active | แสดงประวัติการรัน | ดูข้อมูลย้อนหลัง 3 สถานะ |
| **View Details** | ✅ Active | แสดงรายละเอียด Test Case | ดูข้อมูลเฉพาะเจาะจง 3 สถานะ |
| **Excel Preview** | ✅ Active | แสดงข้อมูล Excel | ดูข้อมูลดิบ |
| **PDF Download** | ✅ Active | สร้างรายงาน PDF | ดาวน์โหลดรายงาน |
| **Gallery Modal** | ✅ Active | แสดงภาพ Evidence | ดู Screenshot |
| **LightGallery** | ✅ Active | จัดการภาพแบบ Advanced | Zoom, Fullscreen |
| **Thumbnail Cache** | ✅ Active | จัดการ Thumbnail | เพิ่มความเร็ว |
| **3-Status Support** | 🆕 New | รองรับ PASS/FAIL Major/FAIL Blocker | แยกระดับความรุนแรง |

---

## 🔧 การตั้งค่าและการปรับแต่ง

### 7.1 Environment Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=false
RESULTS_DIR=/path/to/results
THUMBNAIL_CACHE_SIZE=1000
PDF_FONT_PATH=/path/to/fonts
```

### 7.2 Configuration File
```python
# config.py
class Config:
    RESULTS_DIR = '/path/to/results'
    THUMBNAIL_WIDTH = 800
    THUMBNAIL_HEIGHT = 450
    PDF_FONT_NORMAL = 'HeiseiMin-W3'
    PDF_FONT_BOLD = 'HeiseiKakuGo-W5'
    CACHE_TIMEOUT = 3600
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

---

## 📈 Performance Metrics

### 7.1 Response Times
- **Dashboard Load**: < 2 seconds
- **PDF Generation**: < 10 seconds
- **Thumbnail Generation**: < 5 seconds
- **Excel Preview**: < 3 seconds

### 7.2 Resource Usage
- **Memory**: < 512MB
- **CPU**: < 30% average
- **Disk I/O**: < 100MB/s
- **Network**: < 1MB/s average

---

## 🚀 การ Deploy

### 7.1 Production Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright
playwright install chromium

# Set environment
export FLASK_ENV=production

# Run application
python dashboard_server.py
```

### 7.2 Docker Deployment
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright
RUN playwright install chromium

# Copy application
COPY . /app
WORKDIR /app

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "dashboard_server.py"]
```

---

## 📝 สรุป

Dashboard Report เป็นระบบที่ครบครันสำหรับการจัดการและแสดงผลข้อมูลการทดสอบอัตโนมัติ โดยมีฟีเจอร์ที่ครอบคลุมตั้งแต่การแสดงผลข้อมูล การสร้างรายงาน การจัดการภาพ และการ Export ข้อมูลในรูปแบบต่างๆ

### Key Features:
- **Modular Architecture**: แยกส่วนการทำงานเป็นโมดูลที่ชัดเจน
- **Performance Optimization**: ใช้ caching และ lazy loading
- **Security**: ป้องกัน path traversal และ file access
- **Scalability**: รองรับการขยายระบบในอนาคต
- **Maintainability**: โค้ดที่อ่านง่ายและบำรุงรักษาได้

### Benefits:
- **ประสิทธิภาพ**: แสดงผลข้อมูลได้รวดเร็ว
- **ความสะดวก**: ใช้งานง่าย ไม่ซับซ้อน
- **ความครบครัน**: รองรับการทำงานทุกด้าน
- **ความยืดหยุ่น**: ปรับแต่งได้ตามความต้องการ

ระบบได้รับการออกแบบให้ใช้งานง่าย มีประสิทธิภาพ และรองรับการใช้งานในสภาพแวดล้อมการทำงานจริง โดยจะช่วยให้การจัดการข้อมูลการทดสอบอัตโนมัติเป็นไปอย่างมีประสิทธิภาพและเป็นระบบมากขึ้น

---

## 📚 เอกสารเพิ่มเติม

สำหรับข้อมูลเพิ่มเติม โปรดดูเอกสารต่อไปนี้:
- [Dashboard Report Specification](./Dashboard_Report_Specification.md)
- [Detailed Technical Specification](./Dashboard_Report_Detailed_Technical_Spec.md)
- [User Guide](./Dashboard_Report_User_Guide.md)

---

## 📞 การติดต่อ

หากมีคำถามหรือต้องการความช่วยเหลือ กรุณาติดต่อ:
- **Email**: support@company.com
- **Phone**: 02-XXX-XXXX
- **Internal Chat**: #dashboard-support

---

*เอกสารนี้ถูกสร้างขึ้นเมื่อ: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}*
*เวอร์ชัน: 1.0*
*ผู้สร้าง: AI Assistant*
