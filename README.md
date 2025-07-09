# ระบบ Export Excel

ระบบเว็บสำหรับ export ข้อมูลสินค้าจากฐานข้อมูล SQL Server เป็นไฟล์ Excel

## คุณสมบัติ

- 🔐 ระบบเข้าสู่ระบบ (Login/Logout)
- 📊 แสดงรายละเอียดสินค้าและราคา
- 📋 สร้างไฟล์ Excel ตามรูปแบบที่กำหนด
- 📈 แสดงสถิติข้อมูลสินค้า
- 📝 ประวัติการดาวน์โหลดไฟล์
- 🔌 ทดสอบการเชื่อมต่อฐานข้อมูล
- 🔄 รีเฟรชข้อมูลแบบ Real-time

## ความต้องการของระบบ

- Python 3.8+
- SQL Server Database
- ODBC Driver for SQL Server

## การติดตั้ง

### 1. Clone หรือดาวน์โหลดโปรเจค

```bash
git clone <repository-url>
cd excel-export-system
```

### 2. สร้าง Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 4. ติดตั้ง ODBC Driver

#### Windows:
- ดาวน์โหลดและติดตั้ง [Microsoft ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

#### Linux (Ubuntu/Debian):
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### 5. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` จากไฟล์ `.env.example`:

```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env`:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this

# Database Configuration
DB_SERVER=your-sql-server-ip-or-name
DB_NAME=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=1234

# File Settings
UPLOAD_FOLDER=downloads
```

### 6. สร้างโฟลเดอร์และตารางฐานข้อมูล

ตรวจสอบให้แน่ใจว่าฐานข้อมูลมีตารางและข้อมูลตาม schema ดังนี้:

```sql
-- ตัวอย่างโครงสร้างตาราง
CREATE TABLE items (
    itemid INT PRIMARY KEY,
    itemcode NVARCHAR(50),
    itemdesc NVARCHAR(200),
    active BIT,
    itemtypeid INT,
    IsScaleDiGiApp BIT
);

CREATE TABLE itemprice (
    itemid INT,
    customertypeid INT,
    price DECIMAL(10,2),
    FOREIGN KEY (itemid) REFERENCES items(itemid)
);
```

## การใช้งาน

### 1. เริ่มต้นระบบ

```bash
python app.py
```

### 2. เข้าถึงระบบ

เปิดเบราว์เซอร์และไปที่: `http://localhost:5000`

### 3. เข้าสู่ระบบ

- ชื่อผู้ใช้: `admin`
- รหัสผ่าน: `1234`

## โครงสร้างไฟล์

```
excel-export-system/
├── app.py                 # ไฟล์หลักของระบบ
├── config.py             # การตั้งค่าระบบ
├── database.py           # จัดการฐานข้อมูล
├── excel_generator.py    # สร้างไฟล์ Excel
├── requirements.txt      # Dependencies
├── .env.example         # ตัวอย่างไฟล์ environment
├── README.md            # คู่มือการใช้งาน
├── templates/           # Template HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── 404.html
│   └── 500.html
└── downloads/           # โฟลเดอร์เก็บไฟล์ที่สร้าง
```

## รูปแบบไฟล์ Excel ที่สร้าง

ไฟล์ Excel ที่สร้างจะมีคอลัมน์ดังนี้ (รวม 23 คอลัมน์):

- keyboard_shortcut
- product_name
- lf_code
- product_code
- barcode_format
- unit_price
- weight_unit
- quantity
- department
- pt_code
- product_age
- pack_type
- container_weight
- error_percentage
- message_1
- message_2
- label
- discount_table
- account
- splu_field_title_20
- account_recommend
- recommend_days
- nutrition

## การพัฒนาต่อ

### เพิ่ม User Management
- เพิ่มตาราง users ในฐานข้อมูล
- สร้างหน้าจัดการผู้ใช้
- เพิ่มระบบสิทธิ์การเข้าถึง

### เพิ่ม API
- สร้าง REST API สำหรับ mobile app
- เพิ่ม authentication token

### เพิ่ม Features
- กำหนดตัวกรองข้อมูล
- ส่งอีเมลไฟล์ Excel
- รายงานสถิติการใช้งาน

## การแก้ไขปัญหา

### ปัญหาการเชื่อมต่อฐานข้อมูล
1. ตรวจสอบ connection string ในไฟล์ `.env`
2. ตรวจสอบว่า SQL Server เปิดให้เชื่อมต่อจากภายนอก
3. ตรวจสอบ firewall settings
4. ทดสอบการเชื่อมต่อด้วยเครื่องมืออื่น เช่น SQL Server Management Studio

### ปัญหา ODBC Driver
1. ตรวจสอบว่าติดตั้ง ODBC Driver แล้ว
2. ตรวจสอบชื่อ driver ในระบบ:
   ```bash
   # Windows
   odbcad32.exe
   
   # Linux
   odbcinst -j
   ```

### ปัญหา Permission
1. ตรวจสอบสิทธิ์ในการเขียนไฟล์ในโฟลเดอร์ `downloads`
2. ตรวจสอบสิทธิ์ในการเข้าถึงฐานข้อมูล

## License

MIT License

## ติดต่อ

หากมีปัญหาหรือข้อสงสัย กรุณาติดต่อทีมพัฒนา