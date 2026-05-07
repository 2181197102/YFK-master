from utils.extensions import db
from datetime import datetime
import json


class HealthRecord24h(db.Model):
    __tablename__ = "health_record_24h"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    id_card = db.Column(db.String(255), nullable=False)

    # 0时数据（0:00）
    hr_0 = db.Column(db.Integer, nullable=False, comment="0时心率（bpm）")
    sys_0 = db.Column(db.Integer, nullable=False, comment="0时收缩压（mmHg）")
    dia_0 = db.Column(db.Integer, nullable=False, comment="0时舒张压（mmHg）")
    spo2_0 = db.Column(db.Integer, nullable=False, comment="0时血氧饱和度（%）")

    # 2时数据（2:00）
    hr_2 = db.Column(db.Integer, nullable=False, comment="2时心率（bpm）")
    sys_2 = db.Column(db.Integer, nullable=False, comment="2时收缩压（mmHg）")
    dia_2 = db.Column(db.Integer, nullable=False, comment="2时舒张压（mmHg）")
    spo2_2 = db.Column(db.Integer, nullable=False, comment="2时血氧饱和度（%）")

    # 4时数据（4:00）
    hr_4 = db.Column(db.Integer, nullable=False, comment="4时心率（bpm）")
    sys_4 = db.Column(db.Integer, nullable=False, comment="4时收缩压（mmHg）")
    dia_4 = db.Column(db.Integer, nullable=False, comment="4时舒张压（mmHg）")
    spo2_4 = db.Column(db.Integer, nullable=False, comment="4时血氧饱和度（%）")

    # 6时数据（6:00）
    hr_6 = db.Column(db.Integer, nullable=False, comment="6时心率（bpm）")
    sys_6 = db.Column(db.Integer, nullable=False, comment="6时收缩压（mmHg）")
    dia_6 = db.Column(db.Integer, nullable=False, comment="6时舒张压（mmHg）")
    spo2_6 = db.Column(db.Integer, nullable=False, comment="6时血氧饱和度（%）")

    # 8时数据（8:00）
    hr_8 = db.Column(db.Integer, nullable=False, comment="8时心率（bpm）")
    sys_8 = db.Column(db.Integer, nullable=False, comment="8时收缩压（mmHg）")
    dia_8 = db.Column(db.Integer, nullable=False, comment="8时舒张压（mmHg）")
    spo2_8 = db.Column(db.Integer, nullable=False, comment="8时血氧饱和度（%）")

    # 10时数据（10:00）
    hr_10 = db.Column(db.Integer, nullable=False, comment="10时心率（bpm）")
    sys_10 = db.Column(db.Integer, nullable=False, comment="10时收缩压（mmHg）")
    dia_10 = db.Column(db.Integer, nullable=False, comment="10时舒张压（mmHg）")
    spo2_10 = db.Column(db.Integer, nullable=False, comment="10时血氧饱和度（%）")

    # 12时数据（12:00）
    hr_12 = db.Column(db.Integer, nullable=False, comment="12时心率（bpm）")
    sys_12 = db.Column(db.Integer, nullable=False, comment="12时收缩压（mmHg）")
    dia_12 = db.Column(db.Integer, nullable=False, comment="12时舒张压（mmHg）")
    spo2_12 = db.Column(db.Integer, nullable=False, comment="12时血氧饱和度（%）")

    # 14时数据（14:00）
    hr_14 = db.Column(db.Integer, nullable=False, comment="14时心率（bpm）")
    sys_14 = db.Column(db.Integer, nullable=False, comment="14时收缩压（mmHg）")
    dia_14 = db.Column(db.Integer, nullable=False, comment="14时舒张压（mmHg）")
    spo2_14 = db.Column(db.Integer, nullable=False, comment="14时血氧饱和度（%）")

    # 16时数据（16:00）
    hr_16 = db.Column(db.Integer, nullable=False, comment="16时心率（bpm）")
    sys_16 = db.Column(db.Integer, nullable=False, comment="16时收缩压（mmHg）")
    dia_16 = db.Column(db.Integer, nullable=False, comment="16时舒张压（mmHg）")
    spo2_16 = db.Column(db.Integer, nullable=False, comment="16时血氧饱和度（%）")

    # 18时数据（18:00）
    hr_18 = db.Column(db.Integer, nullable=False, comment="18时心率（bpm）")
    sys_18 = db.Column(db.Integer, nullable=False, comment="18时收缩压（mmHg）")
    dia_18 = db.Column(db.Integer, nullable=False, comment="18时舒张压（mmHg）")
    spo2_18 = db.Column(db.Integer, nullable=False, comment="18时血氧饱和度（%）")

    # 20时数据（20:00）
    hr_20 = db.Column(db.Integer, nullable=False, comment="20时心率（bpm）")
    sys_20 = db.Column(db.Integer, nullable=False, comment="20时收缩压（mmHg）")
    dia_20 = db.Column(db.Integer, nullable=False, comment="20时舒张压（mmHg）")
    spo2_20 = db.Column(db.Integer, nullable=False, comment="20时血氧饱和度（%）")

    # 22时数据（22:00）
    hr_22 = db.Column(db.Integer, nullable=False, comment="22时心率（bpm）")
    sys_22 = db.Column(db.Integer, nullable=False, comment="22时收缩压（mmHg）")
    dia_22 = db.Column(db.Integer, nullable=False, comment="22时舒张压（mmHg）")
    spo2_22 = db.Column(db.Integer, nullable=False, comment="22时血氧饱和度（%）")

    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'id_card': self.id_card,

            # 各时间点心率数据
            'hr_0': self.hr_0,
            'hr_2': self.hr_2,
            'hr_4': self.hr_4,
            'hr_6': self.hr_6,
            'hr_8': self.hr_8,
            'hr_10': self.hr_10,
            'hr_12': self.hr_12,
            'hr_14': self.hr_14,
            'hr_16': self.hr_16,
            'hr_18': self.hr_18,
            'hr_20': self.hr_20,
            'hr_22': self.hr_22,

            # 各时间点收缩压数据
            'sys_0': self.sys_0,
            'sys_2': self.sys_2,
            'sys_4': self.sys_4,
            'sys_6': self.sys_6,
            'sys_8': self.sys_8,
            'sys_10': self.sys_10,
            'sys_12': self.sys_12,
            'sys_14': self.sys_14,
            'sys_16': self.sys_16,
            'sys_18': self.sys_18,
            'sys_20': self.sys_20,
            'sys_22': self.sys_22,

            # 各时间点舒张压数据
            'dia_0': self.dia_0,
            'dia_2': self.dia_2,
            'dia_4': self.dia_4,
            'dia_6': self.dia_6,
            'dia_8': self.dia_8,
            'dia_10': self.dia_10,
            'dia_12': self.dia_12,
            'dia_14': self.dia_14,
            'dia_16': self.dia_16,
            'dia_18': self.dia_18,
            'dia_20': self.dia_20,
            'dia_22': self.dia_22,

            # 各时间点血氧饱和度数据
            'spo2_0': self.spo2_0,
            'spo2_2': self.spo2_2,
            'spo2_4': self.spo2_4,
            'spo2_6': self.spo2_6,
            'spo2_8': self.spo2_8,
            'spo2_10': self.spo2_10,
            'spo2_12': self.spo2_12,
            'spo2_14': self.spo2_14,
            'spo2_16': self.spo2_16,
            'spo2_18': self.spo2_18,
            'spo2_20': self.spo2_20,
            'spo2_22': self.spo2_22,

            # 时间字段
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }