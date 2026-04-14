"""
    ============================================
    ФАЙЛ: user_routes.py
    НАЗНАЧЕНИЕ: Маршруты для аутентификации и работы пользователей
    Blueprint: user
    ============================================
"""

from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, current_user, login_required
from database.modules import User, bcrypt, Post
from app.forms import RegistrationForm, LoginForm, TeacherLoginForm
from app.functions import save_pic
from app.utils import get_session

user = Blueprint("user", __name__)


# ============================================
# МАРШРУТ: Логин студента
# URL: /auth, /auth/user/login
# METHOD: GET, POST
# ============================================
@user.route("/auth", methods=["GET", "POST"])
@user.route("/auth/user/login", methods=["GET", "POST"])
def user_login():
    """Страница входа для студентов"""
    form = LoginForm()
    if form.validate_on_submit():
        session = get_session()
        user_db = session.query(User).filter_by(login=form.login.data).first()
        session.close()

        if user_db and user_db.status == 'user' and bcrypt.check_password_hash(user_db.password, form.password.data):
            login_user(user_db, remember=form.remember.data)
            flash(f"Welcome back, {user_db.name}!", "success")
            return redirect(url_for('user.home_user', login=user_db.login))
        else:
            flash("Invalid login or password", "danger")

    return render_template('main/auth.html', form=form, active_tab='user', active_mode='login')


# ============================================
# МАРШРУТ: Регистрация студента
# URL: /auth/user/register
# METHOD: GET, POST
# ============================================
@user.route("/auth/user/register", methods=["GET", "POST"])
def user_register():
    """Страница регистрации для студентов"""
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        new_user = User(
            name=form.name.data,
            login=form.login.data,
            password=hash_password,
            status='user'
        )

        session = get_session()
        try:
            session.add(new_user)
            session.commit()

            registered_user = session.query(User).filter_by(login=form.login.data).first()
            login_user(registered_user, remember=False)
            flash(f"Congrats, {form.login.data}! You have successfully registered!", "success")
            return redirect(url_for('user.home_user', login=registered_user.login))

        except Exception as e:
            print(f"ERROR: {e}")
            session.rollback()
            flash("An error occurred during registration", "danger")
        finally:
            session.close()

    return render_template('main/auth.html', form=form, active_tab='user', active_mode='register')


# ============================================
# МАРШРУТ: Главная страница студента
# URL: /home/<login>
# METHOD: GET, POST
# ЗАЩИТА: Только авторизованный, только свой логин
# ============================================
@user.route("/home/<string:login>", methods=["GET", "POST"])
@login_required
def home_user(login):
    """Отображает список тем, назначенных текущему студенту"""
    if current_user.login != login:
        flash("Access denied", "danger")
        return redirect(url_for('user.user_login'))

    session = get_session()
    posts = session.query(Post).filter_by(student=current_user.id).order_by(Post.date.desc()).all()
    session.close()
    return render_template('main/home_page.html', posts=posts, user_login=login)


# ============================================
# МАРШРУТ: Логин учителя
# URL: /auth/teacher/login
# METHOD: GET, POST
# ============================================
@user.route("/auth/teacher/login", methods=["GET", "POST"])
def teacher_login():
    """Страница входа для учителей"""
    form = TeacherLoginForm()
    if form.validate_on_submit():
        session = get_session()
        user_db = session.query(User).filter_by(login=form.login.data).first()
        session.close()

        if user_db and user_db.status == 'teacher' and bcrypt.check_password_hash(user_db.password, form.password.data):
            login_user(user_db, remember=form.remember.data)
            flash(f"Welcome back, {user_db.name} (Teacher)!", "success")
            return redirect(url_for('post.home_teacher', login=user_db.login))
        else:
            flash("Invalid teacher credentials", "danger")

    return render_template('main/auth.html', form=form, active_tab='teacher', active_mode=None)


# ============================================
# МАРШРУТ: Выход из системы
# URL: /user/logout
# METHOD: GET, POST
# ============================================
@user.route('/user/logout', methods=['GET', 'POST'])
def logout():
    """Выход пользователя из системы"""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('user.user_login'))