from flask import Flask, request, jsonify
from flask_login import current_user
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация CORS для React
    CORS(app,
         resources={r"/*": {"origins": "http://localhost:3000"}},
         supports_credentials=True)

    # Инициализация Keycloak
    from .extensions import keycloak_service
    keycloak_service.init_app(app)

    # Инициализация расширений
    from .extensions import db, login_manager, redis_client, oauth
    db.init_app(app)
    login_manager.init_app(app)
    redis_client.init_app(app)
    oauth.init_app(app)

    # Настройка CSRF (отключаем для API)
    csrf = CSRFProtect(app)
    csrf.exempt('auth.handle_login')  # Пример отключения для конкретного эндпоинта

    # Конфигурация менеджера логина
    from .extensions import configure_login_manager
    configure_login_manager()

    # Регистрация blueprint
    from .routes import main_bp, superset_bp
    from .auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(superset_bp)

    # Обработчики ошибок для JSON API
    @app.errorhandler(401)
    def unauthorized_handler(e):
        return jsonify({
            "error": "Unauthorized",
            "message": "Требуется авторизация"
        }), 401

    @app.errorhandler(404)
    def not_found_handler(e):
        return jsonify({
            "error": "Not Found",
            "message": "Ресурс не найден"
        }), 404

    @app.errorhandler(500)
    def internal_error_handler(e):
        return jsonify({
            "error": "Internal Server Error",
            "message": "Произошла внутренняя ошибка сервера"
        }), 500

    # Обновленная обработка куки после запроса
    @app.after_request
    def add_cors_headers(response):
        # Добавляем CORS заголовки ко всем ответам
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        return response

    return app