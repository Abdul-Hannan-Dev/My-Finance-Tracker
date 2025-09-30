import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    
    DB_PATH = os.getenv('DB_PATH', str(BASE_DIR / "finance.db"))

    S3_UPLOAD_BUCKET = os.getenv('S3_UPLOAD_BUCKET')  
    USE_DYNAMODB = os.getenv('USE_DYNAMODB', '0') == '1'
    DDB_TABLE_NAME = os.getenv('DDB_TABLE_NAME', 'Transactions')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 5 * 1024 * 1024))

    JWT_SECRET = os.getenv('JWT_SECRET', os.getenv('SECRET_KEY', 'dev-secret-change-me'))
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    UCLASSIFY_READ_KEY = os.getenv('UCLASSIFY_READ_KEY')
    HF_API_KEY = os.getenv('HF_API_KEY')
