import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.secrets import get_secret

# 1. Try to obtain the complete DATABASE_URL first.
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. If no DATABASE_URL is found, then obtain DB parameters separately. 
#    priority: environment variables/K8s -> secrets.py -> default values
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER") or get_secret("DB_USER") or "app_user"
    DB_PASSWORD = os.getenv("DB_PASSWORD") or get_secret("DB_PASSWORD") or "UserPassword123!"
    DB_HOST = os.getenv("DB_HOST") or get_secret("DB_HOST") or "127.0.0.1"
    DB_PORT = os.getenv("DB_PORT") or get_secret("DB_PORT") or "3306"
    DB_NAME = os.getenv("DB_NAME") or get_secret("DB_NAME") or "inventory_db"
    
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. Create engine (plus pool_pre_ping to ensure stable connection)
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()









# import os
# import json
# import boto3
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# def get_db_secret():
#     secret_name = os.getenv("DB_SECRET_NAME", "prod/inventory/db-credentials-k8s")
#     region_name = os.getenv("AWS_REGION", "ap-northeast-1")

#     client = boto3.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )

#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#         secret = get_secret_value_response['SecretString']
#         return json.loads(secret)
#     except Exception as e:
#         print(f"Error fetching secret from AWS: {e}")
#         raise e

# # 優先讀取環境變數（適用於 Local / Kubernetes K8s Secret 注入），若無則降級向 AWS Secrets Manager 讀取
# if os.getenv("DB_HOST"):
#     DB_USER = os.getenv("DB_USER", "root")
#     DB_PASSWORD = os.getenv("DB_PASSWORD", "")
#     DB_HOST = os.getenv("DB_HOST", "localhost")
#     DB_PORT = int(os.getenv("DB_PORT", 3306))
#     DB_NAME = os.getenv("DB_NAME", "inventory")
# else:
#     db_config = get_db_secret()
#     config_lower = {str(k).lower(): v for k, v in db_config.items()}

#     DB_USER     = config_lower.get("db_user") or config_lower.get("username") or config_lower.get("user") or "root"
#     DB_PASSWORD = config_lower.get("db_password") or config_lower.get("password") or ""
#     DB_HOST     = config_lower.get("db_host") or config_lower.get("host") or "localhost"
#     DB_PORT     = int(config_lower.get("db_port") or config_lower.get("port") or 3306)
#     DB_NAME     = config_lower.get("db_name") or config_lower.get("dbname") or config_lower.get("database") or "inventory"

# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()















# import os
# import json
# import boto3
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# # 1.Get the function to read Secret directly inside
# import os
# import json
# import boto3
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# # 1. Get the function to read Secret directly inside
# def get_db_secret():
#     secret_name = "prod/inventory/db-credentials-k8s"  # 確保對齊最新 Secret 名稱
#     region_name = "ap-northeast-1"

#     client = boto3.client(
#         service_name='secretsmanager',
#         region_name=region_name
#     )

#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#         secret = get_secret_value_response['SecretString']
#         return json.loads(secret)
#     except Exception as e:
#         print(f"Error fetching secret from AWS: {e}")
#         raise e

# # 2. Get AWS Credentials with case-insensitive fallback
# db_config = get_db_secret()

# # 轉成全小寫字典，實現零失誤容錯匹配
# config_lower = {str(k).lower(): v for k, v in db_config.items()}

# DB_USER     = config_lower.get("db_user") or config_lower.get("username") or config_lower.get("user") or "root"
# DB_PASSWORD = config_lower.get("db_password") or config_lower.get("password") or ""
# DB_HOST     = config_lower.get("db_host") or config_lower.get("host") or "localhost"
# DB_PORT     = int(config_lower.get("db_port") or config_lower.get("port") or 3306)
# DB_NAME     = config_lower.get("db_name") or config_lower.get("dbname") or config_lower.get("database") or "inventory"

# # 3. Construct SQLAlchemy Database URL
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
