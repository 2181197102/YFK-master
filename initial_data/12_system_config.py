# initial_data/01_system_config.py
"""
初始化系统常量（SystemConfig）。

目前仅包含 AUTH_PASSWORD：
- 若不存在 -> 以明文 'auth1234' 生成哈希后写入
- 若已存在 -> 根据参数决定忽略或覆盖更新

外层统一事务提交；此脚本只做 add / flush。
"""

from datetime import datetime

from modules.system_config.models import SystemConfig


def insert_data(db, *, update_if_exists: bool = False):
    """
    :param db: SQLAlchemy db 实例（与其他初始脚本保持一致）
    :param update_if_exists: True = 覆盖更新；False = 已存在时跳过
    """
    print("  - 正在导入初始系统常量 (SystemConfig)...")

    key = "AUTH_PASSWORD"
    raw_password = "auth1234"

    # 查找是否已存在
    cfg = db.session.query(SystemConfig).filter_by(key=key).first()

    if cfg:
        if update_if_exists:
            print("    AUTH_PASSWORD 已存在，将覆盖更新...")
            cfg.set_password(raw_password)
            cfg.updated_time = datetime.utcnow()
            print("    已更新 AUTH_PASSWORD")
        else:
            print("    AUTH_PASSWORD 已存在，跳过导入。")
        return  # 无论更新与否都结束函数

    # 不存在 -> 创建新记录
    cfg = SystemConfig(
        key=key,
        description="授权密码",
        is_sensitive=True,
        created_time=datetime.utcnow(),
        updated_time=datetime.utcnow(),
    )
    cfg.set_password(raw_password)  # 自动设置 value、value_type
    db.session.add(cfg)

    print("    已成功插入 AUTH_PASSWORD")
