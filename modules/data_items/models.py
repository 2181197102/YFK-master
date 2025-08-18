# modules/data_items/models.py
"""
数据项管理相关数据模型
根据数据库设计part2.md中的数据项表和静态敏感等级表实现
"""

from utils.extensions import db
from datetime import datetime


class DataItem(db.Model):
    """数据项表"""
    __tablename__ = 'data_item'

    id = db.Column(db.String(20), primary_key=True)
    associated_name = db.Column(db.String(200), nullable=False, comment='数据项名称')
    associated_code = db.Column(db.String(20), nullable=False, unique=True, comment='数据项代码')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'associated_name': self.associated_name,
            'associated_code': self.associated_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

    def __repr__(self):
        return f"<DataItem {self.associated_code} - {self.associated_name}>"


class StaticSensitivityLevel(db.Model):
    """静态敏感等级表"""
    __tablename__ = 'static_sensitivity_level'

    id = db.Column(db.String(20), primary_key=True)
    data_name = db.Column(db.String(200), nullable=False, comment='数据项名称')
    description = db.Column(db.String(500), nullable=False, comment='数据项描述')
    sensitivity_level = db.Column(db.SmallInteger, nullable=False, comment='敏感等级：1-准标识符，2-显示标识符，3-低敏感，4-高敏感')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    @property
    def sensitivity_level_text(self):
        """获取敏感等级文本描述"""
        level_map = {
            1: '准标识符',
            2: '显示标识符', 
            3: '低敏感数据',
            4: '高敏感数据'
        }
        return level_map.get(self.sensitivity_level, '未知')

    @property
    def sensitivity_risk_value(self):
        """获取敏感度风险值（根据设计文档）"""
        risk_map = {
            1: 0.1,  # quasi_identifier_risk
            2: 0.4,  # explicit_identifier_risk
            3: 0.2,  # low_sensitivity_risk
            4: 0.3   # high_sensitivity_risk
        }
        return risk_map.get(self.sensitivity_level, 0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'data_name': self.data_name,
            'description': self.description,
            'sensitivity_level': self.sensitivity_level,
            'sensitivity_level_text': self.sensitivity_level_text,
            'sensitivity_risk_value': self.sensitivity_risk_value,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

    def __repr__(self):
        return f"<StaticSensitivityLevel {self.data_name} - Level {self.sensitivity_level}>"
