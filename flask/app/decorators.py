from datetime import datetime
from functools import wraps
from flask import redirect, url_for, current_app, jsonify
from flask_login import current_user, logout_user

from .extensions import redis_client, keycloak_service


def check_active_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            decoded = keycloak_service.validate_token(current_user.access_token)
            if datetime.utcnow() > datetime.fromtimestamp(decoded['exp']):
                return jsonify({"error": "Token expired"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401
        session_id = current_user.get_session_id()
        #current_app.logger.debug(f"check_active_session: session_id:{session_id}")
        is_redis_session_created = redis_client.exists(f"user_session:{session_id}")
        #current_app.logger.debug(f"check_active_session: is_redis_session_created:{is_redis_session_created}")
        is_redis_session_invalid = redis_client.exists(f"invalidated:{session_id}")
        #current_app.logger.debug(f"check_active_session: is_redis_session_invalid:{is_redis_session_invalid}")
        if not session_id or not is_redis_session_created or is_redis_session_invalid:
            if is_redis_session_invalid:
                redis_client.delete(f"invalidated:{session_id}")
            logout_user()
            return redirect(url_for('auth.login'))

        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return wrapper