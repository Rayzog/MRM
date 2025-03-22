from flask import Blueprint, jsonify
from authlib.jose import jwt
from authlib.jose.errors import BadSignatureError, DecodeError
from app.extensions import db, redis_client, get_keycloak_public_key  # После объявления Blueprint
from flask import request
from app.extensions import keycloak_service
from app.services.keycloak_service import KeycloakServiceError

auth_bp = Blueprint('auth', __name__)
import requests
from datetime import datetime
from flask import request, flash, redirect, url_for, current_app, render_template
from flask_login import login_user, current_user, logout_user
from app.models import User


@auth_bp.route('/login', methods=['GET'])
def login():
    current_app.logger.debug("login: Start login")
    if current_user.is_authenticated:
        current_app.logger.debug("login: end profile")
        return redirect(url_for('main.profile'))
    current_app.logger.debug("login: End login")
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def handle_login():
    try:
        # Получаем токены через сервис
        tokens = keycloak_service.get_tokens(
            username=request.form.get('username'),
            password=request.form.get('password')
        )

        # Валидируем access token
        decoded_token = keycloak_service.validate_token(tokens['access_token'])
        session_id = decoded_token.get('sid')

        # Получаем информацию о пользователе
        user_info = keycloak_service.get_user_info(tokens['access_token'])

        # Создаем/обновляем пользователя в БД
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

        # Сохраняем сессию в Redis
        redis_key = f"user_session:{session_id}"
        redis_client.setex(redis_key, current_app.config['SESSION_LIFETIME'], session_id)

        login_user(user)
        return redirect(url_for('main.profile'))

    except KeycloakServiceError as e:
        flash(str(e), 'danger')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout', methods=['POST'])
def logout():
    current_app.logger.debug(f"logout: Start logout")
    if current_user.is_authenticated:
        try:
            # Декодируем access_token для получения session_id
            #public_key = f"-----BEGIN PUBLIC KEY-----\n{current_app.config['KEYCLOAK_PUBLIC_KEY']}\n-----END PUBLIC KEY-----"
            public_key = get_keycloak_public_key()
            decoded_token = jwt.decode(
                current_user.access_token,
                key=public_key,
                claims_options={"validate_aud": False}
            )
            session_id = decoded_token.get('sid')

            # Удаляем сессию из Redis по session_id
            redis_client.delete(f"user_session:{session_id}")

            # Вызов logout в Keycloak (оставьте текущий код)
            logout_url = f"{current_app.config['KEYCLOAK_URL']}/realms/{current_app.config['KEYCLOAK_REALM']}/protocol/openid-connect/logout"
            data = {
                'client_id': current_app.config['KEYCLOAK_CLIENT_ID'],
                'client_secret': current_app.config['KEYCLOAK_CLIENT_SECRET'],
                'refresh_token': current_user.refresh_token  # Используем сохраненный токен
            }
            response = requests.post(logout_url, data=data, timeout=60)

            # Удаляем сессию Flask-Login
            cookies = request.cookies
            current_app.logger.debug(f"logout: Все куки before logout:{cookies}")
            logout_user()
            cookies = request.cookies
            current_app.logger.debug(f"logout: Все куки after logout:{cookies}")
        except (BadSignatureError, DecodeError) as e:
            current_app.logger.error(f"logout: Ошибка декодирования токена: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"logout: Ошибка выхода: {str(e)}")
    current_app.logger.debug(f"logout: END logout")
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout/backchannel', methods=['POST'])
#@cross_origin(origins="*")
def handle_backchannel_logout():
    """
    Обработчик Backchannel Logout от Keycloak.
    Удаляет сессию пользователя в Redis по logout_token.
    """
    current_app.logger.debug(f"backchannel: start backchannel")
    current_app.logger.debug("backchannel: Headers: %s", request.headers)
    current_app.logger.debug("backchannel: Form Data: %s", request.form)

    try:
        # Получаем токен из запроса
        logout_token = request.form.get('logout_token')
        current_app.logger.debug(f"logout_token: {logout_token}")
        if not logout_token:
            current_app.logger.warning("Backchannel Logout: отсутствует logout_token")
            return jsonify({"error": "Missing logout_token"}), 400

        # Конфигурация Keycloak
        realm_url = f"{current_app.config['KEYCLOAK_URL']}/realms/{current_app.config['KEYCLOAK_REALM']}"
        #public_key = f"-----BEGIN PUBLIC KEY-----\n{current_app.config['KEYCLOAK_PUBLIC_KEY']}\n-----END PUBLIC KEY-----"
        public_key = get_keycloak_public_key()
        current_app.logger.debug(f"backchannel: Received token: {logout_token}")
        current_app.logger.debug(f"backchannel: Public key: {public_key}")

        try:
            decoded = jwt.decode(
                logout_token,
                key=public_key,
                claims_options={
                    "exp": {"essential": True},
                    "aud": {"essential": True, "value": current_app.config['KEYCLOAK_CLIENT_ID']},
                }
            )
        except BadSignatureError as e:
            current_app.logger.error(f"Ошибка подписи: {str(e)}")
            flash("Ошибка аутентификации", "danger")
            return redirect(url_for('auth.login'))
        except DecodeError as e:
            current_app.logger.error(f"Ошибка декодирования: {str(e)}")
            flash("Неверный формат токена", "danger")
            return redirect(url_for('auth.login'))
        current_app.logger.debug(f"backchannel: Decoded token: {decoded}")  # Добавьте эту строку

        # Извлекаем идентификатор сессии
        session_id = decoded.get('sid')
        if not session_id:
            current_app.logger.error("Backchannel Logout: sid не найден в токене")
            return jsonify({"error": "Invalid token"}), 400

        # Удаляем сессию пользователя из Redis
        redis_client.delete(f"user_session:{session_id}")
        current_app.logger.debug(f"backchannel: разлогиниваем пользователя")
        cookies = request.cookies
        current_app.logger.debug(f"logout: Все куки before logout:{cookies}")
        logout_user()
        redis_client.setex(f"invalidated:{session_id}", 60, "1")
        cookies = request.cookies
        current_app.logger.debug(f"logout: Все куки after logout:{cookies}")
        current_app.logger.info(f"Backchannel Logout: сессия {session_id} удалена")
        current_app.logger.debug(f"backchannel: end of backchennel")
        return jsonify({"status": "success"}), 200


    except (BadSignatureError, DecodeError) as e:
        current_app.logger.error(f"Backchannel Logout: ошибка токена - {str(e)}")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        current_app.logger.error(f"Backchannel Logout: внутренняя ошибка - {str(e)}")
        return jsonify({"error": "Internal server error"}), 500