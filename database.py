import pyodbc
import pandas as pd
from config import Config

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection_string = self.config.DATABASE_URL
    
    def get_connection(self):
        """สร้าง connection กับ SQL Server"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อฐานข้อมูล"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_products_data(self):
        """ดึงข้อมูลสินค้าตาม query ที่กำหนด"""
        query = """
        SELECT 
            0 as keyboard_shortcut,
            i.itemdesc as product_name,
            ROW_NUMBER() OVER (ORDER BY i.itemcode) as lf_code,
            i.itemcode as product_code,
            101 as barcode_format,
            ip.price as unit_price,
            4 as weight_unit,
            0 as quantity,
            21 as department,
            0 as pt_code,
            7 as product_age,
            0 as pack_type,
            0 as container_weight,
            0 as error_percentage,
            0 as message_1,
            0 as message_2,
            0 as label,
            0 as discount_table,
            0 as account,
            0 as splu_field_title_20,
            0 as account_recommend,
            0 as recommend_days,
            0 as nutrition
        FROM itemprice ip
        INNER JOIN items i ON i.itemid = ip.itemid
        WHERE ip.customertypeid = 1 
            AND i.active = 1 
            AND i.itemtypeid IN (1,2)
            AND i.IsScaleDiGiApp = 1
        """
        
        try:
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn)
                return df
        except Exception as e:
            print(f"Error fetching products data: {e}")
            return None
    
    def get_products_summary(self):
        """ดึงข้อมูลสรุปสินค้าสำหรับแสดงในหน้าเว็บ จัดกลุ่มตาม category"""
        query = """
        SELECT 
            i.itemcode as product_code,
            i.itemdesc as product_name,
            ip.price as unit_price,
            ic.categoryname as category_name,
            CASE 
                WHEN i.active = 1 THEN 'Active'
                ELSE 'Inactive'
            END as status
        FROM itemprice ip
        INNER JOIN items i ON i.itemid = ip.itemid
        LEFT JOIN itemcategory ic ON i.categoryid = ic.categoryid
        WHERE ip.customertypeid = 1 
            AND i.active = 1 
            AND i.itemtypeid IN (1,2)
            AND i.IsScaleDiGiApp = 1
        ORDER BY ic.categoryname, i.itemcode
        """
        
        try:
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn)
                return df
        except Exception as e:
            print(f"Error fetching products summary: {e}")
            return None