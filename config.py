import os
from dotenv import load_dotenv

# โหลด .env file ก่อน
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database configuration
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DRIVER = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Debug database config
    def __init__(self):
        print(f"Debug Config:")
        print(f"DB_SERVER: {self.DB_SERVER}")
        print(f"DB_NAME: {self.DB_NAME}")
        print(f"DB_USERNAME: {self.DB_USERNAME}")
        print(f"DB_DRIVER: {self.DB_DRIVER}")
    
    # Connection string for SQL Server
    @property
    def DATABASE_URL(self):
        if not all([self.DB_SERVER, self.DB_NAME, self.DB_USERNAME, self.DB_PASSWORD]):
            raise ValueError("Database configuration is incomplete. Please check your .env file.")
        return f'DRIVER={{{self.DB_DRIVER}}};SERVER={self.DB_SERVER};DATABASE={self.DB_NAME};UID={self.DB_USERNAME};PWD={self.DB_PASSWORD}'
    
    # Default admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1234')
    
    # File settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'downloads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size