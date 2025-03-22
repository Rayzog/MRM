# app/services/keycloak_service.py
import requests
from flask import current_app
from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, DecodeError


class KeycloakServiceError(Exception):
    """Базовое исключение для ошибок Keycloak"""
    pass


class KeycloakConnectionError(KeycloakServiceError):
    """Ошибка подключения к Keycloak"""
    pass


class KeycloakAuthError(KeycloakServiceError):
    """Ошибка аутентификации/авторизации"""
    pass


class KeycloakService:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Инициализация с конфигом приложения"""
        self.base_url = app.config['KEYCLOAK_URL']
        self.realm = app.config['KEYCLOAK_REALM']
        self.client_id = app.config['KEYCLOAK_CLIENT_ID']
        self.client_secret = app.config['KEYCLOAK_CLIENT_SECRET']
        self.public_key = f"-----BEGIN PUBLIC KEY-----\n{app.config['KEYCLOAK_PUBLIC_KEY']}\n-----END PUBLIC KEY-----"

    def get_tokens(self, username: str, password: str) -> dict:
        """Получение токенов от Keycloak"""
        url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': username,
            'password': password,
            'grant_type': 'password',
            'scope': 'openid'
        }

        try:
            response = requests.post(
                url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Keycloak connection error: {str(e)}")
            raise KeycloakConnectionError("Ошибка подключения к серверу аутентификации")

    def get_user_info(self, access_token: str) -> dict:
        """Получение информации о пользователе"""
        url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/userinfo"

        try:
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Failed to fetch user info: {str(e)}")
            raise KeycloakAuthError("Ошибка получения данных пользователя")

    def validate_token(self, token: str) -> dict:
        """Валидация и декодирование JWT токена"""
        try:
            decoded = jwt.decode(
                token,
                key=self.public_key,
                claims_options={
                    "alg": {"essential": True, "values": ["RS256"]},
                    "exp": {"essential": True},
                    "aud": {"essential": True, "value": self.client_id}
                }
            )
            return decoded
        except (BadSignatureError, DecodeError) as e:
            current_app.logger.error(f"Token validation error: {str(e)}")
            raise KeycloakAuthError("Недействительный токен")
        except Exception as e:
            current_app.logger.error(f"Unexpected token error: {str(e)}")
            raise KeycloakAuthError("Ошибка проверки токена")

    def logout(self, refresh_token: str) -> None:
        """Выход из Keycloak"""
        url = f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/logout"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Logout error: {str(e)}")
            raise KeycloakConnectionError("Ошибка выхода из системы")