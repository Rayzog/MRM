from flask import Flask, request
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect

from .auth import handle_backchannel_logout, handle_login
from .extensions import db, login_manager, redis_client, oauth, keycloak_service

csrf = CSRFProtect()

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    keycloak_service.init_app(app)

    # Инициализация расширений
    from app.extensions import db, login_manager, redis_client, oauth
    csrf.init_app(app)
    csrf.exempt(handle_backchannel_logout)
    csrf.exempt(handle_login)
    db.init_app(app)
    login_manager.init_app(app)
    redis_client.init_app(app)
    oauth.init_app(app)

    # Конфигурация менеджера логина
    from app.extensions import configure_login_manager
    configure_login_manager()  # Вызываем после инициализации db

    # Регистрация blueprint
    from .routes import main_bp
    from .auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    @app.after_request
    def delete_invalid_cookies(response):
        """Удаляет куки, если сессия помечена как недействительная."""
        if current_user.is_authenticated:
            return response

        session_cookie = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        if session_cookie:
            response.delete_cookie(app.config['SESSION_COOKIE_NAME'])
        return response

    return app
