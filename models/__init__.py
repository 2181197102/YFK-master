# models/__init__.py
"""
集中导入所有模型，确保在调用 db.create_all() / 迁移脚本时
SQLAlchemy 能发现这些类。
"""

# from modules.auth.models import User, Role, UserRole
# from modules.data_management.models import (
#     AccessSuccessTracker, OperationBehaviorTracker, DataSensitivityTracker,
#     AccessTimeTracker, AccessLocationTracker
# )

from modules.auth.models import *
from modules.data_management.models import *

__all__ = [
    'User', 'Role', 'UserRole',
    'AccessSuccessTracker', 'OperationBehaviorTracker', 'DataSensitivityTracker',
    'AccessTimeTracker', 'AccessLocationTracker'
]
