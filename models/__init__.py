# models/__init__.py
"""
集中导入所有模型，确保在调用 db.create_all() / 迁移脚本时
SQLAlchemy 能发现这些类。
"""

# from modules.auth.models import User, Role, UserRoleRelation
# from modules.data_management.models import (
#     AccessSuccessTracker, OperationBehaviorTracker, DataSensitivityTracker,
#     AccessTimeTracker, AccessLocationTracker
# )

from modules.auth.models import *
from modules.data_management.models import *
from modules.system_config.models import *
from modules.ins.models import *

__all__ = [
    'User', 'Role', 'UserRoleRelation', 'Group', 'UserGroupRelation',
    'AccessSuccessTracker', 'OperationBehaviorTracker', 'DataSensitivityTracker',
    'AccessTimeTracker', 'AccessLocationTracker', 'SystemConfig','ins_record','ins_record_disease','ins_record_data','ins_doctor_record'
]

