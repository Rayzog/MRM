from flask_appbuilder.security.manager import AUTH_OID
from flask_appbuilder.security.sqla.manager import SecurityManager
from flask_oidc import OpenIDConnect
from flask_session.sessions import RedisSessionInterface

class OIDCSecurityManager(SecurityManager):
    def __init__(self, appbuilder):
        super(OIDCSecurityManager, self).__init__(appbuilder)
        self.oid = OpenIDConnect(self.appbuilder.get_app)

AUTH_TYPE = AUTH_OID
OIDC_CLIENT_SECRETS = {
    "web": {
        "issuer": "http://keycloak:8080/realms/myMRM",
        "client_id": "superset",
        "client_secret": "yoursecretkey", # Из Keycloak
        "authorization_endpoint": "http://keycloak:8080/realms/myMRM/protocol/openid-connect/auth",
        "token_endpoint": "http://keycloak:8080/realms/myMRM/protocol/openid-connect/token",
        "userinfo_endpoint": "http://keycloak:8080/realms/myMRM/protocol/openid-connect/userinfo",
        "redirect_uris": ["http://localhost:8088/oauth-authorized/keycloak"],
    }
}
OIDC_SCOPES = ["openid", "profile", "email"]
CUSTOM_SECURITY_MANAGER = OIDCSecurityManager

# Маппинг ролей Keycloak -> Superset
KEYCLOAK_ROLE_MAPPING = {
    "superset_admin": "Admin",
    "superset_gamma": "Gamma"
}

# Настройка БД
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:password@postgres:5432/superset"

#app.session_interface = RedisSessionInterface(
#    redis.StrictRedis.from_url('redis://:123@redis:6379/1'),
#    key_prefix="superset:"
#)
