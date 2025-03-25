# superset_config.py
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.manager import AUTH_OAUTH

AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {
        'name': 'keycloak',
        'token_key': 'access_token',  # Имя ключа в ответе токена
        'icon': 'fa-key',
        'remote_app': {
            'client_id': 'superset',  # ваш clientId из Keycloak
            'client_secret': 'bVPpwHQwagtwKevHcqJVZ2qfPonDjANl',  # ваш клиентский секрет из Keycloak
            'api_base_url': 'http://keycloak:8080/realms/myMRM/protocol/openid-connect',
            'access_token_url': 'http://keycloak:8080/realms/myMRM/protocol/openid-connect/token',
            'authorize_url': 'http://keycloak:8080/realms/myMRM/protocol/openid-connect/auth',
            'server_metadata_url': "http://keycloak:8080/realms/myMRM/.well-known/openid-configuration",
            'client_kwargs': {
                'scope': 'openid email profile',
            },
            'redirect_uri': 'http://localhost:8088/login/complete/keycloak/'
        },
    }
]

# Маппинг ролей Keycloak -> Superset
AUTH_ROLE_ADMIN = "superset_admin"
AUTH_ROLE_PUBLIC = "superset_gamma"

# Отключить X-Frame-Options
HTTP_HEADERS = {}
# Или разрешить определенные источники
HTTP_HEADERS = {'X-Frame-Options': 'ALLOW-FROM http://localhost:5000'}  # Порт вашего Flask-приложения

ENABLE_CORS = True
CORS_OPTIONS = {
    'origins': ['http://localhost:8088', 'http://localhost:5000'],  # добавьте свои домены
    'methods': ['GET', 'POST', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization']
}

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:password@postgres:5432/superset'