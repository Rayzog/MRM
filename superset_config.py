# superset_config.py
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.manager import AUTH_OAUTH

CUSTOM_SECURITY_MANAGER = SupersetSecurityManager

AUTH_TYPE = AUTH_OAUTH
AUTHOIZE_URL = 'http://keycloak:8080/realms/myMRM/protocol/openid-connect/auth'
OAUTH_PROVIDERS = [
    {
        'name': 'keycloak',
        'token_key': 'access_token',  # Token Key in response from IdP
        'icon': 'fa-key',
        'remote_app': {
            'client_id': 'superset',  # Client ID from Keycloak
            'client_secret': 'YOUR_CLIENT_SECRET',  # Client Secret from Keycloak
            'api_base_url': 'http://keycloak:8080/realms/myMRM/protocol/openid-connect',
            'access_token_url': 'http://keycloak:8080/realms/myMRM/protocol/openid-connect/token',
            'authorize_url': 'http://keycloak:8080/realms/myMRM/protocol/openid-connect/auth',
            'client_kwargs': {
                'scope': 'email profile',
            },
        },
    }
]

ENABLE_CORS = True
CORS_OPTIONS = {
    'origins': ['http://localhost:8088', 'http://localhost:5000'],
    'methods': ['GET', 'POST', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization']
}

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:password@postgres:5432/superset'