"""
    ============================================
    ФАЙЛ: functions.py
    НАЗНАЧЕНИЕ: Вспомогательные утилиты для обработки данных
    РАСПОЛОЖЕНИЕ: app/functions.py
    ИСПОЛЬЗУЕТСЯ В: user_routes.py (закомментирован)
    ============================================

    ЧТО ДЕЛАЕТ ЭТОТ ФАЙЛ:
    - Обрабатывает загрузку аватарок пользователей
    - Изменяет размер изображений
    - Генерирует уникальные имена для файлов
    - Сохраняет изображения на сервер

    СТАТУС: ❌ В НАСТОЯЩЕЕ ВРЕМЯ НЕ ИСПОЛЬЗУЕТСЯ
    (в user_routes.py функция save_pic закомментирована)
"""

import os
import secrets
from PIL import Image
from flask import current_app


# ============================================
# ФУНКЦИЯ: save_pic
# НАЗНАЧЕНИЕ: Сохраняет загруженную аватарку пользователя
# ============================================
def save_pic(picture):
    """
    Сохраняет изображение на сервер с изменением размера

    ПАРАМЕТРЫ:
    - picture: файл изображения из формы (request.files)

    ВОЗВРАЩАЕТ:
    - picture_fn: уникальное имя сохраненного файла

    АЛГОРИТМ РАБОТЫ:
    1. Генерирует случайное имя файла (16 символов в hex)
    2. Сохраняет оригинальное расширение файла
    3. Формирует полный путь для сохранения
    4. Изменяет размер изображения до 125x125 пикселей
    5. Сохраняет изображение на диск
    6. Возвращает имя файла для сохранения в БД

    ПРИМЕР:
    Вход: picture = user_avatar.jpg
    Выход: a1b2c3d4e5f6g7h8.jpg
    Файл сохраняется: /static/upload/a1b2c3d4e5f6g7h8.jpg
    """

    # Генерация случайного имени файла (8 байт = 16 символов в hex)
    # Пример: random_hex = 'a1b2c3d4e5f6g7h8'
    random_hex = secrets.token_hex(8)

    # Разделение имени файла на имя и расширение
    # picture.filename = 'avatar.jpg' → _, f_ext = ('avatar', '.jpg')
    _, f_ext = os.path.splitext(picture.filename)

    # Формирование уникального имени файла
    # Пример: picture_fn = 'a1b2c3d4e5f6g7h8.jpg'
    picture_fn = random_hex + f_ext

    # Формирование полного пути для сохранения
    # current_app.config['ABSOLUTE_PATH'] - путь к папке static/upload/
    # Пример: '/home/user/project/static/upload/a1b2c3d4e5f6g7h8.jpg'
    picture_path = os.path.join(current_app.config['ABSOLUTE_PATH'], picture_fn)

    # Размер для миниатюры (125x125 пикселей)
    output_size = (125, 125)

    # Открытие изображения с помощью Pillow (PIL)
    i = Image.open(picture)

    # Изменение размера с сохранением пропорций (thumbnail)
    # Изображение будет уменьшено, но не увеличено
    i.thumbnail(output_size)

    # Сохранение изображения на диск
    i.save(picture_path)

    # Возврат имени файла для сохранения в БД
    return picture_fn


"""
    ============================================
    КАК ЭТО ДОЛЖНО БЫЛО ИСПОЛЬЗОВАТЬСЯ:
    ============================================

    В user_routes.py в методе user_register():

    # Было закомментировано:
    # if form.picture.data:
    #     picture_file = save_pic(form.picture.data)
    #     new_user.avatar = picture_file

    СЕЙЧАС:
    avatar_filename = 'default_avatar.png'  # Всегда используется стандартная аватарка
"""

"""
    ============================================
    ТРЕБОВАНИЯ ДЛЯ РАБОТЫ ФУНКЦИИ:
    ============================================

    1. Установленная библиотека Pillow:
       pip install Pillow

    2. В конфигурации приложения (cfg.py) должен быть:
       ABSOLUTE_PATH = os.path.join(os.getcwd(), 'static/upload/')

    3. Папка static/upload/ должна существовать и иметь права на запись

    4. В форме регистрации должно быть поле:
       picture = FileField('Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
"""

"""
    ============================================
    ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
    ============================================

    # Пример 1: Загрузка аватарки при регистрации
    if form.validate_on_submit():
        if form.picture.data:
            avatar_file = save_pic(form.picture.data)
        else:
            avatar_file = 'default_avatar.png'

        new_user = User(avatar=avatar_file, ...)

    # Пример 2: Обновление аватарки пользователя
    if form.picture.data:
        # Удаление старой аватарки (если не default)
        if current_user.avatar != 'default_avatar.png':
            old_path = os.path.join(current_app.config['ABSOLUTE_PATH'], current_user.avatar)
            if os.path.exists(old_path):
                os.remove(old_path)

        # Сохранение новой аватарки
        current_user.avatar = save_pic(form.picture.data)
"""
