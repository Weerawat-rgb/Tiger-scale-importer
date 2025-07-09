# สร้างไฟล์ batch
@"
@echo off
cd /d "D:\_project\Tiger-scale-importer"
python app.py
"@ | Out-File -FilePath "flask_runner.bat" -Encoding ASCII

# ลบ task เก่า (ถ้ามี)
schtasks /delete /tn "TigerScaleFlaskApp" /f

# สร้าง task ใหม่
schtasks /create /tn "TigerScaleFlaskApp" /tr "D:\_project\Tiger-scale-importer\flask_runner.bat" /sc onstart /ru "SYSTEM" /f

# เริ่มต้น task
schtasks /run /tn "TigerScaleFlaskApp"