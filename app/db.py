import os
import json
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1.Get the function to read Secret directly inside
def get_db_secret():
    secret_name = "prod/inventory/db-credentials-k8s" # ⚠️ Please confirm the AWS Secret name matches
    region_name = "ap-northeast-1"                    # ⚠️ Please specify the region (e.g., Tokyo)

    client = boto3.client(                            git # Use boto3 to create a Secrets Manager client                   
        service_name='secretsmanager',
        region_name=region_name
    )
                                   
    try:
        
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error fetching secret from AWS: {e}")
        raise e

# 2. Get AWS Credentials
db_config = get_db_secret()

# 2. Get AWS Credentials
db_config = get_db_secret()

# 使用 .get() 自動對齊大小寫與 common keys，避免 KeyError
DB_USER     = db_config.get("DB_USER") or db_config.get("username") or db_config.get("user")
DB_PASSWORD = db_config.get("DB_PASSWORD") or db_config.get("password")
DB_HOST     = db_config.get("DB_HOST") or db_config.get("host")
DB_PORT     = int(db_config.get("DB_PORT") or db_config.get("port") or 3306)
DB_NAME     = db_config.get("DB_NAME") or db_config.get("dbname") or db_config.get("database") or "inventory"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()