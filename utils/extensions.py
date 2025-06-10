# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# 仅在此处定义 SQLAlchemy 和 JWTManager 实例，但不进行初始化
db = SQLAlchemy()
jwt = JWTManager()