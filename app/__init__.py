from flask import Flask
from flask_assets import Environment, Bundle
from database.cfg import Config
from database.modules import init_db, create_tables, login_manager
from app.post_routes import post
from app.user_routes import user
import os


def create_app(cfg_class=Config):
    app = Flask(__name__)
    app.config.from_object(cfg_class)

    init_db()
    create_tables()

    app.register_blueprint(user)
    app.register_blueprint(post)

    # Инициализация login_manager
    login_manager.init_app(app)
    login_manager.login_view = 'user.user_login'
    login_manager.login_message = 'Please log in to access this page.'

    # ========== FLASK-ASSETS НАСТРОЙКА ==========
    assets = Environment(app)

    # Убедиться, что директория для скомпилированных файлов существует
    gen_dir = os.path.join(app.static_folder, 'gen')
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir)

    # Регистрируем бандлы (без фильтров для простоты)
    main_css = Bundle(
        'css/main.css',
        'css/table.css',
        'css/avatar.css',
        output='gen/packed.css'
    )

    auth_css = Bundle(
        'css/auth_login.css',
        output='gen/auth.css'
    )

    create_css = Bundle(
        'css/create.css',
        output='gen/create.css'
    )

    update_css = Bundle(
        'css/update.css',
        output='gen/update.css'
    )

    assets.register('main_css', main_css)
    assets.register('auth_css', auth_css)
    assets.register('create_css', create_css)
    assets.register('update_css', update_css)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)