import os
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

    #KEYCLOAK
    SECRET_KEY = 'bVPpwHQwagtwKevHcqJVZ2qfPonDjANl'
    KEYCLOAK_URL = os.environ.get('KEYCLOAK_URL', 'http://keycloak:8080')
    KEYCLOAK_REALM = "myMRM"
    KEYCLOAK_CLIENT_ID = "flask-app"
    KEYCLOAK_CLIENT_SECRET = os.environ.get('SECRET_KEY', 'bVPpwHQwagtwKevHcqJVZ2qfPonDjANl')
    OIDC_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid-configuration"
    KEYCLOAK_PUBLIC_KEY = os.environ.get('KEYCLOAK_PUBLIC_KEY', "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnMaPr5zVithwO3m1QkxfV9p+uOEyAl7WhjuPZRjo32vngAjjND5Vbk1lxv+SDXSc+TTUGw5QnApC5AL1zesN4vkCGsq43xp54u56HozjfUI+qUECr7WJ4z68LKMaYsJ/HnCeeJI+pfX0VJQB166be6HMQy0xH1hIlakbNQ/Xzl3HrED6KqBqiDVEQOpejp3cjgopgiGThKEqh2p1x+x+GVR47pUpI3zRu7ZIHxPUhOZt9kMlcTBf+aZWu++8SjLA7HCrtCqjXxDE+/AhwkOH/8QTEQ4IXTGFCAdEpa/c1Z7oQN1h3usHTCqRbZgI1lktRCwQJfzMAgI5P5igatYE9QIDAQAB")