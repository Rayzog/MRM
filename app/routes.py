from flask import Blueprint, render_template, redirect, url_for, current_app, make_response
from flask_login import login_required, current_user, logout_user
from flask import request

from app.decorators import check_active_session
from app.extensions import login_manager, redis_client  # Убедитесь в наличии
from app.models import User

main_bp = Blueprint('main', __name__)

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
