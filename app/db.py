import os
import json
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1.Get the function to read Secret directly inside
def get_db_secret():
    secret_name = "prod/inventory/db-credentials-v1"  # ⚠️ Please confirm the AWS Secret name matches
    region_name = "ap-northeast-1"                    # ⚠️ Please specify the region (e.g., Tokyo)

    client = boto3.client(                            # Use boto3 to create a Secrets Manager client                   
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

DB_USER = db_config["DB_USER"]
DB_PASSWORD = db_config["DB_PASSWORD"]
DB_HOST = db_config["DB_HOST"]
DB_PORT = db_config["DB_PORT"]
DB_NAME = db_config["DB_NAME"]

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()