from flask import current_app
from datetime import datetime
from .extensions import db, get_keycloak_public_key
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'local_users'

    id = db.Column(db.Integer, primary_key=True)
    keycloak_id = db.Column(db.String(36), unique=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120))
    last_active = db.Column(db.DateTime)
    refresh_token = db.Column(db.String(2000))
    access_token = db.Column(db.String(2000))

    def __repr__(self):
        return f'<User {self.username}>'

    def get_session_id(self):
        """Получает session_id (sid) из access_token."""
        if not self.access_token:
            return None

        try:
            from authlib.jose import jwt  # Локальный импорт
            #public_key = f"-----BEGIN PUBLIC KEY-----\n{current_app.config['KEYCLOAK_PUBLIC_KEY']}\n-----END PUBLIC KEY-----"
            public_key = get_keycloak_public_key()
            decoded = jwt.decode(
                self.access_token,
                key=public_key,
                claims_options={"validate_aud": False}
            )
            exp = decoded.get('exp')
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                return None  # Токен просрочен
            return decoded.get('sid')
        except Exception as e:
            current_app.logger.error(f"Ошибка декодирования токена: {str(e)}")
            return None

    def update_tokens(self, access_token: str, refresh_token: str):
        """Обновляет токены пользователя и сохраняет в БД"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.last_active = datetime.utcnow()
        db.session.add(self)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "last_active": self.last_active.isoformat()
        }