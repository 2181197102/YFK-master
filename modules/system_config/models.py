# modules/system_config/models.py
from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class SystemConfig(db.Model):
    """
    用于保存系统级常量 / 配置项。
    建议以『键值对』形式设计，并区分是否敏感、是否只读等属性。
    """
    __tablename__ = "system_configs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 配置键，建议全局唯一，可加前缀区分业务域。
    key = db.Column(db.String(128), unique=True, nullable=False)

    # 配置值；敏感时可存密文 / 哈希。
    value = db.Column(db.Text, nullable=False)

    # 类型：string / int / bool / json / password 等，便于反序列化或哈希验证
    value_type = db.Column(db.String(32), default="string", nullable=False)

    # 是否敏感（true 表示对外接口/日志/导出需隐藏或打码）
    is_sensitive = db.Column(db.Boolean, default=False, nullable=False)

    # 是否只读（true 表示只能在迁移脚本或代码层面改）
    read_only = db.Column(db.Boolean, default=False, nullable=False)

    description = db.Column(db.String(255), nullable=True)

    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(
        db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False
    )

    # ----------- 针对 password 类型的辅助方法 -----------
    def set_password(self, raw_pwd: str):
        self.value = generate_password_hash(raw_pwd)
        self.value_type = "password"
        self.is_sensitive = True

    def check_password(self, raw_pwd: str) -> bool:
        if self.value_type != "password":
            raise ValueError("当前配置项并不是 password 类型")
        return check_password_hash(self.value, raw_pwd)
