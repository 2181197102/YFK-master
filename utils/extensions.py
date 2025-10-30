# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import redis
from config import Config

# 仅在此处定义 SQLAlchemy 和 JWTManager 实例，但不进行初始化
db = SQLAlchemy()
jwt = JWTManager()

# Redis 实例
redis_client = redis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    password=Config.REDIS_PASSWORD,
    decode_responses=True  # 自动解码字符串
)