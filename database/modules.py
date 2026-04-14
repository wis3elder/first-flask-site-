"""
    ============================================
    ФАЙЛ: modules.py
    НАЗНАЧЕНИЕ: Модели БД, подключение, инициализация
    РАСПОЛОЖЕНИЕ: database/modules.py
    ============================================

    ЧТО СОДЕРЖИТ ЭТОТ ФАЙЛ:
    - Модели User и Post (SQLAlchemy)
    - Подключение к БД
    - Хеширование паролей (bcrypt)
    - Управление сессиями (Flask-Login)
    - Создание таблиц
"""

import datetime
from database.cfg import Config
from sqlalchemy import create_engine, Integer
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager

# ============================================
# ГЛОБАЛЬНЫЕ ОБЪЕКТЫ
# ============================================
bcrypt = Bcrypt()  # Хеширование паролей
login_manager = LoginManager()

# ============================================
# ПОДКЛЮЧЕНИЕ К БД
# ============================================
def db_connect():
    """Создает и возвращает соединение с БД"""
    engine = create_engine(Config.DATABASE_URL)
    return engine


# ============================================
# БАЗОВЫЙ КЛАСС ДЛЯ МОДЕЛЕЙ
# ============================================
class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""
    pass


# ============================================
# МОДЕЛЬ: User (Пользователь)
# Таблица: user
# ============================================
class User(Base, UserMixin):
    """
    Модель пользователя (студент или учитель)

    ПОЛЯ:
    - id: первичный ключ
    - status: 'user' (студент) или 'teacher' (учитель)
    - name: полное имя
    - login: уникальный логин
    - password: хеш пароля
    - date: дата регистрации
    - avatar: имя файла аватарки

    СВЯЗИ:
    - posts: все темы, созданные пользователем (как учитель)
    """
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(50), default="user")
    name: Mapped[str] = mapped_column(String(50))
    login: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(200))
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    avatar: Mapped[str] = mapped_column(String(200), default='default_avatar.png')

    # Связь: все темы, где пользователь является учителем (автором)
    posts: Mapped[list['Post']] = relationship(
        'Post',
        foreign_keys='Post.teacher',
        back_populates='author'
    )


# ============================================
# МОДЕЛЬ: Post (Тема)
# Таблица: post
# ============================================
class Post(Base):
    """
    Модель темы (связь учитель-студент)

    ПОЛЯ:
    - id: первичный ключ
    - teacher: ID учителя (внешний ключ)
    - subject: название темы
    - student: ID студента (внешний ключ)
    - date: дата создания

    СВЯЗИ:
    - author: объект User (учитель)
    - student_user: объект User (студент)
    """
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    subject: Mapped[str] = mapped_column(String(250))
    student: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    # Связь с учителем (автором)
    author: Mapped['User'] = relationship(
        'User',
        foreign_keys=[teacher],
        back_populates='posts',
        lazy='joined'
    )

    # Связь со студентом
    student_user: Mapped['User'] = relationship(
        'User',
        foreign_keys=[student],
        lazy='joined'
    )


# ============================================
# ЗАГРУЗЧИК ПОЛЬЗОВАТЕЛЯ ДЛЯ FLASK-LOGIN
# ============================================
@login_manager.user_loader
def load_user(user_id):
    """Загружает пользователя по ID для Flask-Login"""
    engine = db_connect()
    with Session(engine) as session:
        return session.get(User, int(user_id))


# ============================================
# ИНИЦИАЛИЗАЦИЯ БД
# ============================================
def init_db():
    """Проверяет подключение к базе данных"""
    engine = db_connect()
    with engine.connect() as conn:
        print("Connection to the database successful! ✅")
        engine.dispose()


def create_tables():
    """Создает все таблицы в БД (если их нет)"""
    engine = db_connect()
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    engine.dispose()


# ============================================
# ЗАПУСК ПРИ ПРЯМОМ ВЫЗОВЕ
# ============================================
if __name__ == "__main__":
    init_db()
    create_tables()