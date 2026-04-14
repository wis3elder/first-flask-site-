import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_PATH = os.path.join(PROJECT_ROOT, 'app', 'static', 'upload')
    ABSOLUTE_PATH = UPLOAD_PATH

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "flask_db")
    DB_USER = os.getenv("DB_USER", "admin_flask")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")


    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = '216FIVGHJLBKWQNgydgwuqklLM;'