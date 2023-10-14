from directorio import base_path, app_path, public_path, registro_path


class Config:
    SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^'
    BASE_PATH = base_path()
    APP_PATH = app_path()
    PUBLIC_PATH = public_path()
    REGISTRO_PATH = registro_path()

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'users'


config = {
    'development': DevelopmentConfig
}