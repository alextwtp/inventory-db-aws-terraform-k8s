import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def build_database_url() -> str:
    # 1. 優先採用完整 DATABASE_URL (如 GCP Cloud Run / Supabase / Heroku 傳入)
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 2. 次之採用個別環境變數 (AWS ECS / K8s ConfigMap & Secret / Local .env)
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME")

    # 如果基本環境變數充足，直接組裝
    if host and user:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

    # 3. 只有在完全沒有環境變數時，才觸發 AWS Secrets Manager 作為 Fallback (回退機制)
    try:
        import json

        import boto3

        secret_name = os.getenv(
            "DB_SECRET_NAME", "prod/inventory/db-credentials-k8s"
        )
        region_name = os.getenv("AWS_REGION", "ap-northeast-1")
        client = boto3.client(
            service_name="secretsmanager", region_name=region_name
        )
        secret_res = client.get_secret_value(SecretId=secret_name)
        config = json.loads(secret_res["SecretString"])
        config_lower = {str(k).lower(): v for k, v in config.items()}

        u = (
            config_lower.get("db_user")
            or config_lower.get("username")
            or "root"
        )
        p = (
            config_lower.get("db_password")
            or config_lower.get("password")
            or ""
        )
        h = config_lower.get("db_host") or config_lower.get("host") or "localhost"
        pt = config_lower.get("db_port") or config_lower.get("port") or 3306
        n = (
            config_lower.get("db_name")
            or config_lower.get("database")
            or "inventory"
        )

        return f"mysql+pymysql://{u}:{p}@{h}:{pt}/{n}"
    except Exception as e:
        print(
            f"[Warning] AWS Secret fetch failed or boto3 unavailable: {e}. Falling back to default local config."
        )
        # 4. 最底層本地預設值 (Local Dev)
        return "mysql+pymysql://root:password@127.0.0.1:3306/inventory"


DATABASE_URL = build_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
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

# # Get the environment variables.If none are found, degrade to reading from AWS Secrets Manager.

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