from flask import current_app, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user
from flask_redis import FlaskRedis
from authlib.integrations.flask_client import OAuth
from flask_login import user_loaded_from_request
from flask import make_response
from functools import lru_cache
from .services.keycloak_service import KeycloakService

login_manager = LoginManager()

db = SQLAlchemy()
redis_client = FlaskRedis()
oauth = OAuth()
login_manager.login_view = 'auth.login'

keycloak_service = KeycloakService()

def configure_login_manager():
    from .models import User  # Локальный импорт внутри функции

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @user_loaded_from_request.connect
    def check_session_active(sender, user=None):
        """Проверяет активность сессии в Redis при каждом запросе."""
        current_app.logger.debug(f"check_session_active start")
        if not user or not user.is_authenticated:
            current_app.logger.debug(f"check_session_active: not user or not user.is_authenticated")
            return

        session_id = user.get_session_id()
        current_app.logger.debug(f"check_session_active start: {session_id}")
        redis_key = f"user_session:{session_id}"
        if not session_id:
            logout_user()  # Сессия неактивна — принудительный выход
            return

        if redis_client.exists(f"invalidated:{session_id}"):
            current_app.logger.debug(f"check_session_active: redis_client.exists invalidated:{session_id}")
            logout_user()
            redis_client.delete(f"invalidated:{session_id}")
            response = make_response(redirect(url_for('auth.login')))
            response.delete_cookie(current_app.config['SESSION_COOKIE_NAME'])
            return response

        if not redis_client.exists(f"user_session:{session_id}"):
            current_app.logger.debug(f"check_session_active: redis_client.exists user_session:{session_id}")
            logout_user()  # Сессия неактивна — принудительный выход
            current_app.logger.info(f"Сессия {session_id} неактивна. Пользователь разлогинен.")
            # Удаляем куки через response (если возможно)
            response = make_response(redirect(url_for('auth.login')))
            response.delete_cookie(current_app.config['SESSION_COOKIE_NAME'])
            return response

@lru_cache(maxsize=1)
def get_keycloak_public_key():
    return f"-----BEGIN PUBLIC KEY-----\n{current_app.config['KEYCLOAK_PUBLIC_KEY']}\n-----END PUBLIC KEY-----"