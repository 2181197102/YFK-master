import os
from datetime import timedelta
from dotenv import load_dotenv
from urllib.parse import quote

# 加载环境变量
load_dotenv()


class Config:
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST', '122.207.103.159')
    DB_PORT = int(os.environ.get('DB_PORT', 13306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '!TuXy1D8oQ@122.207.103.159')  # 示例密码
    DB_NAME = os.environ.get('DB_NAME', 'medical_system')

    # 对密码进行 URL 编码
    DB_PASSWORD_ENCODED = quote(DB_PASSWORD)

    # SQLAlchemy 配置
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    JWT_ALGORITHM = 'HS256'

    # 应用配置
    APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.environ.get('APP_PORT', 7878))

    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

    # RBAC角色配置
    ROLES = {
        'PATIENT': '患者',
        'FAMILY_DOCTOR': '家庭医生',
        'ATTENDING_DOCTOR': '主治医生',
        'CROSS_HOSPITAL_DOCTOR': '跨院医生',
        'EMERGENCY_DOCTOR': '急救医生',
        'RESEARCHER': '科研人员',
        'ADMIN': '管理员'
    }


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}