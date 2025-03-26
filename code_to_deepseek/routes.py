from flask import Blueprint, render_template, redirect, url_for, current_app, make_response
from flask_login import login_required, current_user, logout_user
from flask import request

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
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self' http://localhost:5000;"
        return response

    except KeycloakAuthError:
        # Если токен недействителен, обновляем его
        new_tokens = keycloak_service.get_tokens(username=current_user.username,
                                                 password=None)  # Подумайте, как хотите обновлять токен
        current_user.update_tokens(
            access_token=new_tokens['access_token'],
            refresh_token=new_tokens.get('refresh_token')
        )

    return response