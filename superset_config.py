from superset.security import SupersetSecurityManager
from flask_appbuilder.security.manager import AUTH_REMOTE_USER  # Добавьте этот импорт
from authlib.jose import jwt
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://:123@redis:6379/0",
    strategy="fixed-window"
)
# Настройки лимитера
RATELIMIT_ENABLED = False  # Полностью отключаем лимитер

# Или кастомизируем лимиты
#DEFAULT_RATE_LIMIT = "5000 per minute"
RATELIMIT_STORAGE_URI = "redis://:123@redis:6379/0"  # Используем Redis

class HeaderAuthSecurityManager(SupersetSecurityManager):
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        self.public_key = self._get_keycloak_public_key()
    
    def _get_keycloak_public_key(self):
        jwks_url = "http://keycloak:8080/realms/myMRM"
        response = requests.get(jwks_url)
        jwk_set = response.json()
        print(jwk_set)
        print(jwk_set["public_key"])
        return jwk_set["public_key"]
    
    def get_user_roles(self, user):
        return super().get_user_roles(user)

    # Обязательный метод для AUTH_REMOTE_USER
    def auth_user_remote_user(self, username):
        user = self.find_user(username=username)
        return user
    
    def get_user_by_access_token(self, token):
        try:
            decoded = jwt.decode(
                token,
                key=self.public_key,
                claims_options={
                    "exp": {"essential": True},
                    "aud": {"essential": True, "value": "superset"}
                }
            )
            return self.find_user(username=decoded["preferred_username"])
        except Exception as e:
            self.appbuilder.get_app.logger.error(f"Token error: {str(e)}")
            return None

CUSTOM_SECURITY_MANAGER = HeaderAuthSecurityManager

# Security
AUTH_TYPE = AUTH_REMOTE_USER
WTF_CSRF_ENABLED = False
FEATURE_FLAGS = {"EMBEDDED_SUPERSET": True}

# CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'origins': ['http://flask:5000']
}

# Iframe
HTTP_HEADERS = {
    'Content-Security-Policy': (
        "frame-ancestors 'self' http://flask:5000; "
        "default-src 'self'"
    )
}