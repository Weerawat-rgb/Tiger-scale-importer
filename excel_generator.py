import pandas as pd
import os
from datetime import datetime
from database import DatabaseManager

class ExcelGenerator:
    def __init__(self, download_folder='downloads'):
        self.download_folder = download_folder
        self.db_manager = DatabaseManager()
        
        # สร้างโฟลเดอร์ download ถ้ายังไม่มี
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
    
    def generate_excel_file(self, user_id='admin'):
        """สร้างไฟล์ Excel จากข้อมูลในฐานข้อมูล"""
        try:
            # ดึงข้อมูลจากฐานข้อมูล
            df = self.db_manager.get_products_data()
            
            if df is None or df.empty:
                return None, "ไม่พบข้อมูลสินค้า"
            
            # สร้างชื่อไฟล์ด้วย timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products_export_{timestamp}.xlsx"
            filepath = os.path.join(self.download_folder, filename)
            
            # เขียนไฟล์ Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Products', index=False)
                
                # จัดรูปแบบคอลัมน์
                worksheet = writer.sheets['Products']
                
                # ปรับความกว้างคอลัมน์
                column_widths = {
                    'A': 15,  # keyboard_shortcut
                    'B': 30,  # product_name
                    'C': 15,  # lf_code
                    'D': 20,  # product_code
                    'E': 15,  # barcode_format
                    'F': 15,  # unit_price
                    'G': 15,  # weight_unit
                    'H': 10,  # quantity
                    'I': 15,  # department
                    'J': 10,  # pt_code
                    'K': 15,  # product_age
                    'L': 15,  # pack_type
                    'M': 15,  # container_weight
                    'N': 15,  # error_percentage
                    'O': 15,  # message_1
                    'P': 15,  # message_2
                    'Q': 10,  # label
                    'R': 15,  # discount_table
                    'S': 15,  # account
                    'T': 20,  # splu_field_title_20
                    'U': 15,  # account_recommend
                    'V': 15,  # recommend_days
                    'W': 15,  # nutrition
                }
                
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width
            
            # บันทึกข้อมูลการดาวน์โหลดลงใน log
            self.log_download(user_id, filename, len(df))
            
            return filepath, f"สร้างไฟล์ Excel สำเร็จ: {filename} ({len(df)} รายการ)"
            
        except Exception as e:
            return None, f"เกิดข้อผิดพลาดในการสร้างไฟล์: {str(e)}"
    
    def log_download(self, user_id, filename, record_count):
        """บันทึกประวัติการดาวน์โหลด"""
        log_file = os.path.join(self.download_folder, 'download_log.txt')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"{timestamp} | User: {user_id} | File: {filename} | Records: {record_count}\n"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing log: {e}")
    
    def get_download_history(self, limit=50):
        """ดึงประวัติการดาวน์โหลด"""
        log_file = os.path.join(self.download_folder, 'download_log.txt')
        
        try:
            if not os.path.exists(log_file):
                return []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # ย้อนลำดับและจำกัดจำนวน
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            recent_lines.reverse()
            
            history = []
            for line in recent_lines:
                line = line.strip()
                if line:
                    parts = line.split(' | ')
                    if len(parts) >= 4:
                        history.append({
                            'timestamp': parts[0],
                            'user': parts[1].replace('User: ', ''),
                            'filename': parts[2].replace('File: ', ''),
                            'records': parts[3].replace('Records: ', '')
                        })
            
            return history
            
        except Exception as e:
            print(f"Error reading download history: {e}")
            return []
    
    def cleanup_old_files(self, days_old=7):
        """ลบไฟล์เก่าที่เก่ากว่า x วัน"""
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.download_folder):
                if filename.endswith('.xlsx'):
                    filepath = os.path.join(self.download_folder, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    
                    if (current_time - file_time).days > days_old:
                        os.remove(filepath)
                        print(f"Deleted old file: {filename}")
                        
        except Exception as e:
            print(f"Error cleaning up old files: {e}")