from flask import Blueprint, jsonify, request
from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, DecodeError
from .extensions import db, redis_client, get_keycloak_public_key
from .extensions import keycloak_service
from .services.keycloak_service import KeycloakServiceError
from .models import User
import requests
from datetime import datetime
from flask import current_app
from flask_login import login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def handle_login():
    try:
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()
        tokens = keycloak_service.get_tokens(
            username=data.get('username'),
            password=data.get('password')
        )

        decoded_token = keycloak_service.validate_token(tokens['access_token'])
        session_id = decoded_token.get('sid')

        user_info = keycloak_service.get_user_info(tokens['access_token'])

        user = User.query.filter_by(keycloak_id=user_info['sub']).first()
        if not user:
            user = User(
                keycloak_id=user_info['sub'],
                username=user_info.get('preferred_username'),
                email=user_info.get('email')
            )
            db.session.add(user)

        user.update_tokens(
            access_token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token')
        )
        db.session.commit()

        redis_key = f"user_session:{session_id}"
        redis_client.setex(redis_key, current_app.config['SESSION_LIFETIME'], session_id)

        login_user(user)
        return jsonify({
            "access_token": tokens['access_token'],
            "refresh_token": tokens.get('refresh_token'),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "last_active": user.last_active.isoformat()
            }
        }), 200

    except KeycloakServiceError as e:
        return jsonify({"error": str(e), "code": "AUTH_ERROR"}), 401
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "Not authenticated"}), 401

        public_key = get_keycloak_public_key()
        decoded_token = jwt.decode(
            current_user.access_token,
            key=public_key,
            claims_options={"validate_aud": False}
        )
        session_id = decoded_token.get('sid')

        redis_client.delete(f"user_session:{session_id}")

        logout_url = f"{current_app.config['KEYCLOAK_URL']}/realms/{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/logout"
        requests.post(logout_url, data={
            'client_id': current_app.config['KEYCLOAK_CLIENT_ID'],
            'client_secret': current_app.config['KEYCLOAK_CLIENT_SECRET'],
            'refresh_token': current_user.refresh_token
        }, timeout=5)

        logout_user()
        return jsonify({"message": "Logged out successfully"}), 200

    except (BadSignatureError, DecodeError) as e:
        current_app.logger.error(f"Token decode error: {str(e)}")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_tokens():
    try:
        refresh_token = request.json.get('refresh_token')
        if not refresh_token:
            return jsonify({"error": "Refresh token required"}), 400

        new_tokens = keycloak_service.refresh_token(refresh_token)
        decoded_token = keycloak_service.validate_token(new_tokens['access_token'])

        user = User.query.filter_by(access_token=current_user.access_token).first()
        user.update_tokens(
            access_token=new_tokens['access_token'],
            refresh_token=new_tokens.get('refresh_token')
        )
        db.session.commit()

        return jsonify({
            "access_token": new_tokens['access_token'],
            "refresh_token": new_tokens.get('refresh_token')
        }), 200

    except KeycloakServiceError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Refresh error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/logout/backchannel', methods=['POST'])
def handle_backchannel_logout():
    try:
        logout_token = request.form.get('logout_token')
        if not logout_token:
            return jsonify({"error": "Missing logout_token"}), 400

        public_key = get_keycloak_public_key()
        decoded = jwt.decode(
            logout_token,
            key=public_key,
            claims_options={
                "exp": {"essential": True},
                "aud": {"essential": True, "value": current_app.config['KEYCLOAK_CLIENT_ID']},
            }
        )

        session_id = decoded.get('sid')
        redis_client.delete(f"user_session:{session_id}")
        logout_user()

        return jsonify({"status": "success"}), 200

    except (BadSignatureError, DecodeError) as e:
        current_app.logger.error(f"Backchannel error: {str(e)}")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        current_app.logger.error(f"Backchannel internal error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500