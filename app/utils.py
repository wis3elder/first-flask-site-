"""
    ============================================
    ФАЙЛ: utils.py
    НАЗНАЧЕНИЕ: Вспомогательные утилиты для работы с БД
    РАСПОЛОЖЕНИЕ: app/utils.py
    ИСПОЛЬЗУЕТСЯ В: post_routes.py, user_routes.py
    ============================================
"""

from database.modules import db_connect
from sqlalchemy.orm import Session

# ============================================
# ФУНКЦИЯ: get_session
# НАЗНАЧЕНИЕ: Создание сессии БД
# ============================================
def get_session():
    """
    Создает и возвращает новую сессию для работы с БД

    ВОЗВРАЩАЕТ:
    - Session: объект сессии SQLAlchemy

    ИСПОЛЬЗОВАНИЕ:
    session = get_session()
    try:
        # работа с БД
        session.commit()
    finally:
        session.close()
    """
    engine = db_connect()
    return Session(engine)
