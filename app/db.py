import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def build_database_url() -> str:
    # 1. Use the complete DATABASE_URL (e.g., passed in from GCP Cloud Run / Supabase / Heroku) 
    #    whenever possible.
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 2. Secondly, individual environment variables (AWS ECS / K8s ConfigMap & Secret / Local .env)
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME")

    # If there are sufficient variables in the basic environment, proceed directly to assembly.
    if host and user:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

    # 3.AWS Secrets Manager is only triggered as a fallback mechanism when there are absolutely 
    #   no environmental variables.
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
        # 4. The lowest level local default value (Local Dev)
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