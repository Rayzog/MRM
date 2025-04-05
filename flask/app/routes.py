from flask import Blueprint, jsonify, make_response, request, Response
from flask_login import login_required, current_user
from .decorators import check_active_session
from .extensions import keycloak_service
from .models import User
import requests

main_bp = Blueprint('main', __name__)
superset_bp = Blueprint('superset', __name__)


@main_bp.route('/')
@login_required
def home():
    return jsonify({
        "message": "Добро пожаловать в систему",
        "user": {
            "username": current_user.username,
            "email": current_user.email
        }
    })


@main_bp.route('/profile')
@login_required
@check_active_session
def profile():
    return jsonify({
        "user": {
            "username": current_user.username,
            "email": current_user.email,
            "last_active": current_user.last_active.isoformat()
        }
    })


@superset_bp.route('/superset-auth-check')
@login_required
@check_active_session
def superset_auth_check():
    try:
        # Проверка валидности токена
        decoded_token = keycloak_service.validate_token(current_user.access_token)
        return jsonify({"status": "authorized"}), 200

    except Exception as e:
        return jsonify({
            "error": "Требуется обновление токена",
            "details": str(e)
        }), 401


@main_bp.route('/superset-proxy/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def superset_proxy(path):
    headers = {
        'Authorization': f'Bearer {current_user.access_token}',
        'Content-Type': request.headers.get('Content-Type', 'application/json')
    }

    # Передача cookies и данных
    response = requests.request(
        method=request.method,
        url=f'http://superset:8088/{path}',
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    # Фильтрация заголовков для проксирования
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = {
        name: value for name, value in response.raw.headers.items()
        if name.lower() not in excluded_headers
    }

    return Response(
        response.content,
        status=response.status_code,
        headers=headers
    )


@main_bp.route('/api/user-session')
@login_required
def check_session():
    return jsonify({
        "authenticated": True,
        "user": {
            "username": current_user.username,
            "email": current_user.email
        }
    })

#эндпоинт для проверки здоровья
@main_bp.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "services": {
            "database": "active",
            "redis": "active"
        }
    })