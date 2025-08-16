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

__all__ = [
    # 用户认证相关模型
    'User', 'Role', 'UserRoleRelation', 'Group', 'UserGroupRelation',
    
    # 数据管理相关模型
    'UserLogs',                        # 用户日志表
    'UserAccessSensitiveData',         # 用户访问敏感数据统计表
    'UserAccessLocationTracker',       # 用户访问地点统计表
    'UserIps',                         # 用户常用IP表
    'UserAccessSuccessTracker',        # 用户访问成功率统计表
    'UserAccessTimeTracker',           # 用户访问时间统计表
    'UserOperationBehaviorTracker',    # 用户操作行为统计表
    'ICD10Code',                       # ICD-10码表
    'DiseaseDataItem',                 # 病种-数据项字段表
    
    # 系统配置相关模型
    'SystemConfig'
]
