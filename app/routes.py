from flask import Blueprint, render_template, redirect, url_for, current_app, make_response, Response
from flask_login import login_required, current_user, logout_user
from flask import request
from flask import make_response
import requests
from app.decorators import check_active_session
from app.extensions import login_manager, redis_client  # Убедитесь в наличии
from app.models import User
from app.services.keycloak_service import KeycloakAuthError
from app.extensions import keycloak_service

main_bp = Blueprint('main', __name__)
superset_bp = Blueprint('superset', __name__)

@main_bp.route('/')
@login_required
#@check_active_session
def home():
    return render_template('index.html')

@main_bp.route('/profile')
@login_required
@check_active_session
def profile():
    cookies = request.cookies
    current_app.logger.debug(f"profile: Все куки profile:{cookies}")
    current_app.logger.debug(f"profile: is_authenticated:{current_user.is_authenticated}")
    return render_template('profile.html', user=current_user)

@superset_bp.route('/superset')
@login_required
@check_active_session
def view_superset():
    # Проверяем, пройдена ли аутентификация
    if not current_user.is_authenticated:
        # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
        return redirect(url_for('auth.login'))

    # Применяем логику обновления токенов, если они истекли
    try:
        # Проверяем, истек ли токен
        #keycloak_service = current_app.config['KEYCLOAK_SERVICE']  # Предполагаем, что это ваш экземпляр сервис-класса
        decoded_token = keycloak_service.validate_token(current_user.access_token)
        response = make_response(render_template('superset.html'))
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self' http://localhost:5000; frame-src 'self' http://localhost:8088"
        current_app.logger.debug(f"view_superset: ответ:{response.json}")
        return response

    except KeycloakAuthError:
        # Если токен недействителен, обновляем его
        new_tokens = keycloak_service.get_tokens(username=current_user.username,
                                                 password=None)  # Подумайте, как хотите обновлять токен
        current_user.update_tokens(
            access_token=new_tokens['access_token'],
            refresh_token=new_tokens.get('refresh_token')
        )
        return redirect(url_for('superset.view_superset'))

# @main_bp.route('/superset-proxy')
# @login_required
# @check_active_session
# def superset_proxy():
#     # Передаем токен в заголовке Authorization
#     response = make_response(redirect('http://superset:8088/superset/welcome/'))
#     response.headers['Authorization'] = f'Bearer {current_user.access_token}'
#     return response




@main_bp.route('/superset-proxy/<path:path>')
@login_required
def superset_proxy(path):
    # Формируем URL Superset
    if path.startswith('static/'):
        return redirect(f'http://superset:8088/{path}')

    # Проксируем запрос с токеном в заголовках
    headers = {
        'Authorization': f'Bearer {current_user.access_token}'
    }
    response = requests.get(
        f'http://superset:8088/{path}',
        headers=headers,
        params=request.args
    )

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding']
    return Response(
        response.content,
        status=response.status_code,
        headers={k: v for k, v in response.headers.items() if k.lower() not in excluded_headers}
    )