"""
    ============================================
    ФАЙЛ: post_routes.py
    НАЗНАЧЕНИЕ: Маршруты для работы с темами (постами)
    Blueprint: post
    ============================================
"""

from flask import Blueprint, render_template, request, redirect, flash, url_for, abort
from flask_login import login_required, current_user
from database.modules import User, Post
from app.forms import StudentForm
from app.utils import get_session

post = Blueprint("post", __name__)


# ============================================
# МАРШРУТ: Корневой URL
# URL: /
# METHOD: GET
# ============================================
@post.route("/")
def index():
    """Редирект в зависимости от статуса пользователя"""
    if current_user.is_authenticated:
        if current_user.status == 'teacher':
            return redirect(url_for('post.home_teacher', login=current_user.login))
        else:
            return redirect(url_for('user.user_login', login=current_user.login))
    return redirect(url_for('user.user_login'))


# ============================================
# МАРШРУТ: Главная страница учителя
# URL: /teacher/home/<login>
# METHOD: GET, POST
# ЗАЩИТА: Только учитель, только свой логин
# ============================================
@post.route("/teacher/home/<string:login>", methods=["GET", "POST"])
@login_required
def home_teacher(login):
    """Отображает список тем, созданных текущим учителем"""
    if current_user.status != 'teacher' or current_user.login != login:
        abort(403)

    session = get_session()
    posts = session.query(Post).filter_by(teacher=current_user.id).order_by(Post.date.desc()).all()
    session.close()
    return render_template('post/home_page.html', posts=posts, teacher_login=login)


# ============================================
# МАРШРУТ: Создание новой темы
# URL: /post/create
# METHOD: POST, GET
# ЗАЩИТА: Только учитель
# ============================================
@post.route("/post/create", methods=["POST", "GET"])
@login_required
def create():
    """Создание новой темы (учитель выбирает студента и вводит тему)"""
    if current_user.status != 'teacher':
        abort(404)

    form = StudentForm()
    session = get_session()
    form.student.choices = [(s.id, s.login) for s in session.query(User).filter_by(status='user')]

    if request.method == "POST":
        student_id = request.form["student"]
        subject = request.form["subject"]

        post = Post(
            teacher=current_user.id,
            student=student_id,
            subject=subject
        )

        try:
            session.add(post)
            session.commit()
            flash("Тема успешно создана!", "success")
            return redirect(url_for('post.home_teacher', login=current_user.login))
        except Exception as e:
            print(str(e))
            session.rollback()
            flash("Ошибка при создании поста", "danger")
        finally:
            session.close()
    else:
        session.close()
        return render_template("post/create.html", form=form)


# ============================================
# МАРШРУТ: Редактирование темы
# URL: /post/<id>/update
# METHOD: POST, GET
# ЗАЩИТА: Только учитель, только автор темы
# ============================================
@post.route("/post/<int:id>/update", methods=["POST", "GET"])
@login_required
def update(id):
    """Редактирование существующей темы (только автор)"""
    if current_user.status != 'teacher':
        abort(404)

    session = get_session()
    post = session.query(Post).get(id)

    if not post or post.teacher != current_user.id:
        session.close()
        abort(404)

    if request.method == "POST":
        subject = request.form.get("subject")
        student_id = request.form.get("student")

        if not subject or not student_id:
            flash("Заполни все поля!", "danger")
            return redirect(request.url)

        try:
            post.subject = subject
            post.student = student_id
            session.commit()
            flash("Пост обновлен!", "success")
            return redirect(url_for('post.home_teacher', login=current_user.login))
        except Exception as e:
            print(str(e))
            session.rollback()
            flash("Ошибка при обновлении", "danger")
        finally:
            session.close()
    else:
        users = session.query(User).filter_by(status='user').all()
        session.close()
        return render_template("post/upd.html", post=post, users=users)


# ============================================
# МАРШРУТ: Удаление темы
# URL: /post/<id>/delete
# METHOD: POST, GET
# ЗАЩИТА: Только учитель, только автор темы
# ============================================
@post.route("/post/<int:id>/delete", methods=["POST", "GET"])
@login_required
def delete(id):
    """Удаление темы (только автор)"""
    if current_user.status != 'teacher':
        abort(404)

    session = get_session()
    try:
        post = session.query(Post).get(id)

        if not post or post.teacher != current_user.id:
            abort(404)

        session.delete(post)
        session.commit()
        flash("Пост успешно удален!", "success")
        return redirect(url_for('post.home_teacher', login=current_user.login))
    except Exception as e:
        print(str(e))
        session.rollback()
        abort(404)
    finally:
        session.close()