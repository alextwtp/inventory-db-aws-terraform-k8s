from unittest.mock import MagicMock
import boto3
import json

# Create a Mock Secrets Manager return value that meets the requirements of app/db.py.
mock_secrets_client = MagicMock()
mock_secrets_client.get_secret_value.return_value = {
    "SecretString": json.dumps({
        "DB_USER": "root",
        "DB_PASSWORD": "password",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_NAME": "test_db",
        "username": "root",
        "password": "password",
        "host": "localhost",
        "port": 3306,
        "dbname": "test_db"
    })
}

# Replace boto3.client
original_boto3_client = boto3.client
def side_effect_client(service_name, *args, **kwargs):
    if service_name == "secretsmanager":
        return mock_secrets_client
    return original_boto3_client(service_name, *args, **kwargs)

boto3.client = MagicMock(side_effect=side_effect_client)

# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from api.fastapi_app import app  

@pytest.fixture
def client():
    return TestClient(app)