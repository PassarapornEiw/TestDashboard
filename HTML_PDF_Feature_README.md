# HTML to PDF Image Conversion Feature

## ภาพรวม

ฟีเจอร์ใหม่นี้ช่วยให้ Dashboard สามารถแสดง HTML files เป็นรูปภาพใน PDF reports ได้ เหมือนกับที่แสดงใน Gallery Modal ของเว็บไซต์

## ฟีเจอร์ที่เพิ่มเข้ามา

### 1. HTML to Image Conversion
- **ฟังก์ชันหลัก**: `html_to_image_for_pdf()`
- **การทำงาน**: แปลง HTML files เป็น PIL Image objects โดยใช้ Playwright
- **ขนาด**: รองรับการกำหนดขนาด viewport ที่ต้องการ
- **Full Page Capture**: รองรับการถ่ายภาพทั้งหน้าเว็บ (ไม่แหว่ง)

### 2. PDF Image Creation
- **ฟังก์ชันหลัก**: `create_html_preview_image()`
- **การทำงาน**: สร้าง ReportLab Image objects จาก HTML สำหรับใช้ใน PDF
- **การจัดการ**: รองรับการ resize, format conversion และ cleanup

### 3. PDF Integration
- **Main PDF Export**: รองรับ HTML files ในรายงานหลัก
- **Test Case PDF**: แสดง HTML evidence ในรายงาน test case
- **Optimized PDF**: รองรับ HTML ในเวอร์ชัน optimized

## การใช้งาน

### ใน PDF Reports
HTML files จะถูกแสดงเป็นรูปภาพพร้อมกับ:
- **Caption**: แสดงประเภทไฟล์ (HTML File หรือ Screenshot)
- **Dimensions**: ปรับขนาดให้เหมาะสมกับ PDF
- **Quality**: รักษาคุณภาพของเนื้อหา

### การแสดงผล
```python
# ตัวอย่างการใช้งาน
if file_extension in ['html', 'htm']:
    # แปลง HTML เป็นรูปภาพ (full page capture)
    reportlab_img = create_html_preview_image(file_abs, max_width=500, max_height=400, full_page=True)
    
    # แสดงใน PDF พร้อม caption
    file_type_label = "HTML File"
    img_with_caption = [
        [reportlab_img],
        [Paragraph(f"<b>{file_type_label}:</b> {filename}", caption_style)]
    ]
```

## ความต้องการของระบบ

### Required Dependencies
1. **Playwright**: สำหรับการแปลง HTML เป็นรูปภาพ
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Pillow (PIL)**: สำหรับการประมวลผลรูปภาพ
   ```bash
   pip install Pillow
   ```

3. **ReportLab**: สำหรับการสร้าง PDF
   ```bash
   pip install reportlab
   ```

### Optional Dependencies
- **Matplotlib**: สำหรับการสร้าง charts ใน PDF
- **Pandas**: สำหรับการอ่าน Excel files

## การตั้งค่า

### 1. ตรวจสอบ Dependencies
```python
# ใน dashboard_server.py
PLAYWRIGHT_AVAILABLE = True  # ถ้า Playwright ติดตั้งแล้ว
PIL_AVAILABLE = True         # ถ้า Pillow ติดตั้งแล้ว
```

### 2. การกำหนดขนาดรูปภาพ
```python
# กำหนดขนาดสูงสุดสำหรับ HTML preview ใน PDF
max_width = 500   # points
max_height = 400  # points
```

## การทำงาน

### 1. HTML Detection
ระบบจะตรวจสอบ file extension เพื่อระบุประเภทไฟล์:
- `.html`, `.htm` → HTML files
- อื่นๆ → Image files

### 2. Conversion Process
1. **HTML Loading**: ใช้ Playwright โหลด HTML file
2. **Content Detection**: ตรวจสอบและรอให้ dynamic content (charts, badges) โหลดเสร็จ
3. **Full Page Capture**: ถ่ายภาพทั้งหน้าเว็บ (ไม่แหว่ง) โดยใช้ `full_page=True`
4. **Image Processing**: แปลงเป็น PIL Image
5. **Resizing**: ปรับขนาดให้เหมาะสมกับ PDF
6. **Format Conversion**: แปลงเป็น JPEG สำหรับ ReportLab

### 3. Fallback Handling
หากการแปลง HTML ล้มเหลว ระบบจะ:
- สร้าง placeholder image
- แสดงข้อความแจ้งเตือน
- ข้ามไปยังไฟล์ถัดไป

## ตัวอย่างผลลัพธ์

### ใน PDF Report
```
┌─────────────────────────────────────┐
│           HTML Preview              │
│  ┌─────────────────────────────┐    │
│  │    Test Case Evidence       │    │
│  │    Report Content           │    │
│  │    With Styling            │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
HTML File: test_case_evidence.html
```

### การเปรียบเทียบ
- **ก่อนหน้า**: HTML files จะไม่แสดงใน PDF
- **ปัจจุบัน**: HTML files แสดงเป็นรูปภาพที่มีคุณภาพสูง

## การแก้ไขปัญหา

### 1. Playwright ไม่ทำงาน
```bash
# ติดตั้ง Playwright
pip install playwright

# ติดตั้ง browser
playwright install chromium

# ตรวจสอบการติดตั้ง
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### 2. HTML ไม่แสดงใน PDF
- ตรวจสอบว่า HTML file มีอยู่จริง
- ตรวจสอบ file permissions
- ดู debug logs ใน console

### 3. รูปภาพมีขนาดใหญ่เกินไป
- ปรับค่า `max_width` และ `max_height`
- ใช้ optimized PDF mode
- ลดจำนวน evidence files

## การปรับแต่งเพิ่มเติม

### 1. Full Page vs Viewport Capture
```python
# Full page capture (default) - แสดงเนื้อหาทั้งหมด
reportlab_img = create_html_preview_image(file_abs, full_page=True)

# Viewport only capture - แสดงเฉพาะส่วนที่มองเห็น
reportlab_img = create_html_preview_image(file_abs, full_page=False)
```

### 2. เปลี่ยน Browser Engine
```python
# เปลี่ยนจาก Chromium เป็น Firefox
browser = p.firefox.launch()
```

### 3. ปรับ Viewport Settings
```python
# ปรับขนาด viewport (minimum 1200x800 for better rendering)
page = browser.new_page(viewport={"width": 1200, "height": 800})
```

### 4. เพิ่ม Wait Time
```python
# รอให้ dynamic content โหลดเสร็จ
page.wait_for_timeout(3000)  # 3 seconds total
```

### 5. Content Detection
```python
# รอให้ charts และ dynamic elements โหลดเสร็จ
page.wait_for_selector('canvas, svg, .chart, .pie-chart, .status-badge', timeout=5000)
```

## ข้อจำกัด

1. **Performance**: การแปลง HTML อาจใช้เวลานานสำหรับไฟล์ที่ซับซ้อน
2. **Memory**: ใช้ memory มากขึ้นเมื่อประมวลผล HTML ขนาดใหญ่
3. **Dependencies**: ต้องมี Playwright และ browser engine
4. **File Size**: PDF อาจมีขนาดใหญ่ขึ้นเมื่อมี HTML files หลายไฟล์
5. **Content Loading**: ต้องรอให้ dynamic content โหลดเสร็จก่อนถ่ายภาพ

## การพัฒนาต่อ

### 1. Caching
- Cache HTML preview images
- ลดการแปลงซ้ำ

### 2. Batch Processing
- แปลง HTML หลายไฟล์พร้อมกัน
- ใช้ multiprocessing

### 3. Quality Options
- เลือกระดับคุณภาพของรูปภาพ
- รองรับ format ต่างๆ (PNG, WebP)

## สรุป

ฟีเจอร์ HTML to PDF Image Conversion ช่วยให้ Dashboard สามารถแสดง HTML evidence files ได้อย่างสมบูรณ์ใน PDF reports ทำให้รายงานมีความครบถ้วนและน่าเชื่อถือมากขึ้น 

### ✨ ฟีเจอร์หลัก
- **Full Page Capture**: ถ่ายภาพทั้งหน้าเว็บ ไม่แหว่ง
- **Dynamic Content Support**: รองรับ charts, badges และ dynamic elements
- **High Quality**: คุณภาพรูปภาพสูง (90% JPEG quality)
- **Smart Scaling**: ปรับขนาดอัตโนมัติให้เหมาะสมกับ PDF

### 🚀 การใช้งาน
```bash
# ทดสอบฟีเจอร์ใหม่
python test_full_page_capture.py

# ใช้งานปกติ (full page capture เป็น default)
python Resources/Dashboard_Report/dashboard_server.py
```

โดยใช้เทคโนโลยีที่ทันสมัยและมีประสิทธิภาพ
