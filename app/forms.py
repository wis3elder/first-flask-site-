"""
    ============================================
    ФАЙЛ: forms.py
    НАЗНАЧЕНИЕ: Определение всех WTForms для валидации данных
    РАСПОЛОЖЕНИЕ: app/forms.py
    ИСПОЛЬЗУЕТСЯ В: user_routes.py, post_routes.py
    ============================================

    ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ:
    - Создает формы для ввода данных пользователями
    - Валидирует данные перед отправкой в БД
    - Защищает от некорректного ввода
    - Обеспечивает CSRF защиту
"""

from random import choices  # ❌ НЕ ИСПОЛЬЗУЕТСЯ - можно удалить
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed  # ❌ НЕ ИСПОЛЬЗУЕТСЯ - можно удалить
from sqlalchemy.orm import Session
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField, FileField, BooleanField, PasswordField
from wtforms.validators import DataRequired, length, EqualTo, ValidationError
from database.modules import db_connect
from database.modules import User


# ============================================
# ФОРМА РЕГИСТРАЦИИ СТУДЕНТА
# Используется в: user_routes.py -> user_register()
# Шаблон: main/auth.html (active_mode='register')
# ============================================
class RegistrationForm(FlaskForm):
    """
    Форма для регистрации нового студента

    ПОЛЯ:
    - name: полное имя пользователя
    - login: уникальный логин для входа
    - password: пароль (будет захеширован)
    - confirm_password: подтверждение пароля
    - submit: кнопка отправки

    ВАЛИДАЦИЯ:
    - Все поля обязательны для заполнения
    - name: от 4 до 30 символов
    - login: от 6 до 20 символов
    - confirm_password: должно совпадать с password
    - login: проверка на уникальность (метод validate_login)
    """

    name = StringField(
        'Name',
        validators=[DataRequired(), length(min=4, max=30)]
    )

    login = StringField(
        'Login',
        validators=[DataRequired(), length(min=6, max=20)]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )

    submit = SubmitField('Sign Up')

    # ========== КАСТОМНАЯ ВАЛИДАЦИЯ ЛОГИНА ==========
    def validate_login(self, login):
        """
        Проверяет, существует ли пользователь с таким логином в БД
        Вызывается автоматически при валидации формы

        ПАРАМЕТРЫ:
        - login: поле формы с логином

        ИСКЛЮЧЕНИЕ:
        - ValidationError: если пользователь уже существует
        """
        engine = db_connect()
        with Session(engine) as session:
            user = session.query(User).filter_by(login=login.data).first()
            if user:
                raise ValidationError('User already exists')


# ============================================
# ФОРМА ВХОДА ДЛЯ СТУДЕНТА
# Используется в: user_routes.py -> user_login()
# Шаблон: main/auth.html (active_mode='login')
# ============================================
class LoginForm(FlaskForm):
    """
    Форма для входа студента в систему

    ПОЛЯ:
    - login: логин пользователя
    - password: пароль
    - remember: запомнить сессию (чекбокс)
    - submit: кнопка отправки

    ВАЛИДАЦИЯ:
    - Все поля обязательны для заполнения
    - login: от 6 до 20 символов
    """

    login = StringField(
        'Login',
        validators=[DataRequired(), length(min=6, max=20)]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    remember = BooleanField('Remember Me')

    submit = SubmitField('Sign In')


# ============================================
# ФОРМА ВХОДА ДЛЯ УЧИТЕЛЯ
# Используется в: user_routes.py -> teacher_login()
# Шаблон: main/auth.html (active_tab='teacher')
# ============================================
class TeacherLoginForm(FlaskForm):
    """
    Форма для входа учителя в систему

    ПОЛЯ:
    - login: логин учителя
    - password: пароль
    - remember: запомнить сессию (чекбокс)
    - submit: кнопка отправки

    ВАЛИДАЦИЯ:
    - Все поля обязательны для заполнения
    - login: от 6 до 20 символов

    ПРИМЕЧАНИЕ:
    - Внешне идентична LoginForm, но используется отдельно
    - Разделение позволяет разной логике валидации в будущем
    """

    login = StringField(
        'Login',
        validators=[DataRequired(), length(min=6, max=20)]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    remember = BooleanField('Remember Me')

    submit = SubmitField('Sign In')


# ============================================
# ФОРМА ВЫБОРА СТУДЕНТА ДЛЯ УЧИТЕЛЯ
# Используется в: post_routes.py -> create()
# Шаблон: post/create.html
# ============================================
class StudentForm(FlaskForm):
    """
    Форма для выбора студента при создании темы

    ПОЛЯ:
    - student: выпадающий список со студентами

    ОСОБЕННОСТИ:
    - choices = [] - заполняется динамически в маршруте
    - render_kw={'class': 'form-control'} - CSS класс для поля

    КАК ЗАПОЛНЯЮТСЯ CHOICES:
    В post_routes.py в методе create():
    form.student.choices = [(s.id, s.login) for s in session.query(User).filter_by(status='user')]

    ГДЕ:
    - s.id - значение (сохраняется в БД)
    - s.login - отображаемый текст (показывается пользователю)
    """

    student = SelectField(
        'student',
        choices=[],  # Заполняется динамически в маршруте
        render_kw={'class': 'form-control'}
    )