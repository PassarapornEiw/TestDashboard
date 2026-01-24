# Flexible Results Directory Configuration

## Overview

ระบบ Dashboard ได้รับการปรับปรุงให้สามารถค้นหา `results` directory อัตโนมัติ โดยไม่ต้องผูกติดกับชื่อโฟลเดอร์ project ใดเฉพาะ

## การทำงานของระบบ

### 1. ลำดับการค้นหา (Search Order)

ระบบจะค้นหา results directory ตามลำดับดังนี้:

1. **Environment Variable** - `RESULTS_DIR` (สำหรับกำหนดเองโดยตรง)
2. **Auto-Discovery** - ค้นหาโฟลเดอร์ `results` ในโปรเจค subdirectories (1 level ลึก)
3. **Fallback** - ใช้ `PROJECT_ROOT/results` (ถ้ามีอยู่)
4. **Default** - สร้าง `PROJECT_ROOT/results` ใหม่

### 2. เงื่อนไขการตรวจสอบ

ระบบจะยอมรับ results directory เมื่อ:
- โฟลเดอร์ `results` มีอยู่จริง
- ภายในมี timestamp folders รูปแบบ `YYYYMMDD-HHMMSS` หรือ `YYYYMMDD_HHMMSS`
- Timestamp folders มีข้อมูล test results

## วิธีการใช้งาน

### วิธีที่ 1: Auto-Discovery (แนะนำ)

```
Project Root/
├── Automation Project/
│   └── results/
│       ├── 20250516-161132/
│       ├── 20250522-111220/
│       └── 20250523-111221/
├── Test Dashboard/
│   └── Dashboard_Report/
│       └── dashboard_server.py
└── Another Project/
    └── results/
        └── 20250620-111221/
```

ระบบจะหา results directory ที่มีข้อมูลล่าสุดโดยอัตโนมัติ

### วิธีที่ 2: Environment Variable Override

**Windows:**
```cmd
set RESULTS_DIR=C:\Path\To\Your\Results
python dashboard_server.py
```

**Linux/Mac:**
```bash
export RESULTS_DIR=/path/to/your/results
python dashboard_server.py
```

**PowerShell:**
```powershell
$env:RESULTS_DIR = "C:\Path\To\Your\Results"
python dashboard_server.py
```

### วิธีที่ 3: Direct Results Folder

```
Project Root/
├── results/              # ← ตรงนี้
│   ├── 20250516-161132/
│   └── 20250522-111220/
└── Test Dashboard/
    └── Dashboard_Report/
        └── dashboard_server.py
```

## ข้อดีของระบบใหม่

### ✅ ความยืดหยุ่น
- ไม่ผูกติดกับชื่อโฟลเดอร์ "Automation Project"
- รองรับโครงสร้างโปรเจคหลายแบบ
- สามารถใช้กับโปรเจคใดก็ได้

### ✅ การตั้งค่าง่าย
- ไม่ต้องแก้โค้ดเมื่อเปลี่ยนโครงสร้าง
- ใช้ environment variable สำหรับ override
- Auto-discovery ทำงานโดยอัตโนมัติ

### ✅ ความปลอดภัย
- ตรวจสอบความถูกต้องของข้อมูล
- แสดงสถานะการค้นหาอย่างชัดเจน
- สร้าง default directory เมื่อไม่พบ

## การแสดงผลระหว่าง Startup

```
🚀 Starting Dashboard Report Server...
📁 Project Root: C:\Users\Eiw\Documents\Krungsri Tasks
📊 Results Directory: C:\Users\Eiw\Documents\Krungsri Tasks\Automation Project\results

============================================================
RESULTS DIRECTORY DISCOVERY
============================================================
🔍 Auto-discovering results directory in: C:\Users\Eiw\Documents\Krungsri Tasks
📂 Found project subdirectories: ['Automation Project', 'Test Dashboard', 'backup']
✅ Found valid results directory: C:\Users\Eiw\Documents\Krungsri Tasks\Automation Project\results
📊 Contains 7 timestamp folders
✅ Results directory successfully discovered
📂 Path: C:\Users\Eiw\Documents\Krungsri Tasks\Automation Project\results
📊 Contains 7 valid test run folders
🔄 Latest runs:
   • 20250717-120127 (1 features)
   • 20250620-111221_xxxxxxx (0 features)
   • 20250620-111221 (3 features)

💡 Configuration options:
   • Set environment variable RESULTS_DIR to override auto-discovery
   • Place any project with 'results' folder under project root
   • Results folder should contain timestamp folders (YYYYMMDD-HHMMSS)
============================================================
```

## การ Debug และ Troubleshooting

### ปัญหา: ไม่พบ Results Directory

**อาการ:**
```
⚠️ No results directory found. Creating default: C:\Project\results
```

**วิธีแก้:**
1. ตรวจสอบว่ามีโฟลเดอร์ `results` ในโปรเจคหรือไม่
2. ตรวจสอบว่า timestamp folders มีรูปแบบที่ถูกต้อง
3. ใช้ environment variable `RESULTS_DIR` สำหรับกำหนดเองโดยตรง

### ปัญหา: พบหลาย Results Directories

ระบบจะเลือก results directory แรกที่มีข้อมูลที่ถูกต้อง หากต้องการเฉพาะเจาะจง ให้ใช้ environment variable

### ปัญหา: Timestamp Format ไม่ถูกต้อง

รูปแบบที่ยอมรับ:
- `20250516-161132` (ถูก)
- `20250516_161132` (ถูก)
- `20250516161132` (ผิด - ขาดตัวคั่น)
- `2025-05-16` (ผิด - รูปแบบไม่ตรง)

## Migration จากระบบเดิม

ไฟล์เดิมที่ใช้:
```python
RESULTS_DIR = PROJECT_ROOT / "Automation Project" / "results"
```

ไฟล์ใหม่:
```python
# Auto-discover results directory
RESULTS_DIR = discover_results_directory()
```

**ไม่จำเป็นต้องแก้ไขโค้ดอื่น** เพราะ `RESULTS_DIR` ยังคงเป็น Path object เหมือนเดิม

## ตัวอย่างการใช้งานจริง

### Scenario 1: โปรเจคเดียว
```
MyProject/
├── Test Dashboard/
└── results/  # ← ระบบจะเจอโฟลเดอร์นี้
```

### Scenario 2: หลายโปรเจค
```
Workspace/
├── Project A/
│   └── results/  # ← มี timestamp folders
├── Project B/
│   └── results/  # ← ว่างเปล่า
└── Test Dashboard/  # ← ระบบจะเลือก Project A
```

### Scenario 3: Custom Path
```bash
# ใช้ results จากที่อื่น
export RESULTS_DIR="/opt/shared/test_results"
python dashboard_server.py
```

## สรุป

การปรับปรุงนี้ทำให้ Dashboard สามารถใช้งานได้กับโครงสร้างโปรเจคที่หลากหลาย โดยไม่ต้องแก้ไขโค้ดทุกครั้งที่เปลี่ยนโครงสร้าง และยังคงความเข้ากันได้กับระบบเดิม
