import os
import json
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def get_db_secret():
    secret_name = os.getenv("DB_SECRET_NAME", "prod/inventory/db-credentials-k8s")
    region_name = os.getenv("AWS_REGION", "ap-northeast-1")

    client = boto3.client(
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

# Get the environment variables.If none are found, degrade to reading from AWS Secrets Manager.

if os.getenv("DB_HOST"):
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "inventory")
else:
    db_config = get_db_secret()
    config_lower = {str(k).lower(): v for k, v in db_config.items()}

    DB_USER     = config_lower.get("db_user") or config_lower.get("username") or config_lower.get("user") or "root"
    DB_PASSWORD = config_lower.get("db_password") or config_lower.get("password") or ""
    DB_HOST     = config_lower.get("db_host") or config_lower.get("host") or "localhost"
    DB_PORT     = int(config_lower.get("db_port") or config_lower.get("port") or 3306)
    DB_NAME     = config_lower.get("db_name") or config_lower.get("dbname") or config_lower.get("database") or "inventory"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()