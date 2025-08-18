# models/__init__.py
"""
集中导入所有模型，确保在调用 db.create_all() / 迁移脚本时
SQLAlchemy 能发现这些类。
"""

# 导入认证模块
from modules.auth.models import *

# 导入数据管理模块
from modules.data_management.models import *

# 导入系统配置模块
from modules.system_config.models import *

# 导入医疗机构模块
from modules.medical_institutions.models import *

# 导入数据项管理模块
from modules.data_items.models import *

__all__ = [
    # 认证相关模型
    'User', 'Role', 'UserRoleRelation', 'Group', 'UserGroupRelation',
    
    # 数据管理相关模型
    'UserLogs', 'UserAccessSensitiveData', 'UserAccessLocationTracker', 
    'UserIps', 'UserAccessSuccessTracker', 'UserAccessTimeTracker',
    'UserOperationBehaviorTracker', 'ICD10Code', 'DiseaseDataItem',
    
    # 系统配置模型
    'SystemConfig',
    
    # 医疗机构相关模型
    'PatientMedicalRecord', 'MedicalRecordDisease', 
    'MedicalRecordDataItem', 'DoctorMedicalRecord',
    
    # 数据项管理相关模型
    'DataItem', 'StaticSensitivityLevel',
    
    # 向后兼容的旧模型名称
    'AccessSuccessTracker', 'OperationBehaviorTracker', 'DataSensitivityTracker',
    'AccessTimeTracker', 'AccessLocationTracker'
]
