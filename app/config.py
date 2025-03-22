import os
import redis
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    WTF_CSRF_ENABLED = True
    #DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/MRM')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #REDIS
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://:123@redis:6379/0')
    SESSION_TYPE = 'redis'
    SESSION_LIFETIME = timedelta(seconds=30)  # Время жизни сессии
    SESSION_COOKIE_NAME = 'persistent_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Для HTTPS
    SESSION_REFRESH_EACH_REQUEST = True  # Обновление времени при активности
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = SESSION_LIFETIME
    #from app.extensions import redis_client
    #SESSION_REDIS = redis_client

    #KEYCLOAK
    SECRET_KEY = 'bVPpwHQwagtwKevHcqJVZ2qfPonDjANl'
    KEYCLOAK_URL = os.environ.get('KEYCLOAK_URL', 'http://keycloak:8080')
    KEYCLOAK_REALM = "myMRM"
    KEYCLOAK_CLIENT_ID = "flask-app"
    KEYCLOAK_CLIENT_SECRET = os.environ.get('SECRET_KEY', 'bVPpwHQwagtwKevHcqJVZ2qfPonDjANl')
    OIDC_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid-configuration"
    KEYCLOAK_PUBLIC_KEY = os.environ.get('KEYCLOAK_PUBLIC_KEY', "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAm6FmX4agbB7UHIWISsHGtXB0FxWXyLcV3IUFszNPjtpTtnjZARBmGrz2eK9bZbpP43mLzlfImeQYKImN6TfFNh0ZWpqrQPEzdUlcrfcNAS18yR8v9vJqPbkARANiZ6IJZlqWYSZHyMQrWdPv4hPtDRYqw1gDMSuyOrtMSQ3KyL2jdkiUxfPOp06K9WjnXbeAsy4FMidNpVQU10r2moos1d4T9Gg/np7E48nEnASLhvK6ghvxw4VrdL0p35KPe86j7mTnBisu4NpnEDOR/5HdTYuTDKWX4cGovutFf0yhGVgChPakTqJ9OzlFU9E/2jZFQvdZ43l4FyXCpqAnA3OJ6QIDAQAB")