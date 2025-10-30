# -*- coding: utf-8 -*-
"""
sms_code.py - 短信验证码相关功能
"""

import random
from utils.extensions import redis_client
from modules.auth.models import User


def generate_verification_code(length=6):
    """
    生成指定长度的数字验证码
    :param length: 验证码长度，默认6位
    :return: 验证码字符串
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def store_verification_code(key_prefix, phone, code, expire_seconds=600):
    """
    将验证码存储到 Redis
    :param key_prefix: 键前缀（如 'login' 或 'auth'）
    :param phone: 手机号
    :param code: 验证码
    :param expire_seconds: 过期时间（秒），默认600秒（10分钟）
    :return: 是否存储成功
    """
    try:
        redis_key = f"{key_prefix}:{phone}"

        # 如果该手机号之前存在，先删除旧的
        if redis_client.exists(redis_key):
            redis_client.delete(redis_key)

        # 存储新的验证码，设置过期时间
        redis_client.set(redis_key, code, ex=expire_seconds)
        return True
    except Exception as e:
        print(f"Redis 存储验证码失败：{e}")
        return False


def verify_code(key_prefix, phone, code):
    """
    验证验证码是否正确
    :param key_prefix: 键前缀（如 'login' 或 'auth'）
    :param phone: 手机号
    :param code: 用户输入的验证码
    :return: 验证是否通过
    """
    try:
        redis_key = f"{key_prefix}:{phone}"
        stored_code = redis_client.get(redis_key)

        # 兼容 decode_responses=True 或 False 两种情况
        if isinstance(stored_code, bytes):
            stored_code = stored_code.decode("utf-8")

        if stored_code and stored_code == code:
            # 验证成功后删除验证码（一次性使用）
            redis_client.delete(redis_key)
            return True
        return False
    except Exception as e:
        print(f"Redis 验证码验证失败：{e}")
        return False


def get_phone_by_id_card(id_card):
    """
    根据身份证号查询用户手机号
    :param id_card: 身份证号
    :return: 手机号或 None
    """
    try:
        user = User.query.filter_by(id_card=id_card).first()
        return user.phone if user else None
    except Exception as e:
        print(f"查询用户手机号失败：{e}")
        return None


def is_phone_number(account):
    """
    判断输入是否为手机号（简单判断：11位数字）
    :param account: 账号（可能是手机号或身份证号）
    :return: 是否为手机号
    """
    return len(account) == 11 and account.isdigit()

