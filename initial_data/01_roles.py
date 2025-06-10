# initial_data/01_roles.py

from models.models import Role
from datetime import datetime

# RBAC角色配置
ROLES_CONFIG = {
    'PATIENT': '患者',
    'FAMILY_DOCTOR': '家庭医生',
    'ATTENDING_DOCTOR': '主治医生',
    'CROSS_HOSPITAL_DOCTOR': '跨院医生',
    'EMERGENCY_DOCTOR': '急救医生',
    'RESEARCHER': '科研人员',
    'ADMIN': '管理员'
}

def insert_data(db):
    """
    插入初始角色数据。
    """
    print("  - 正在插入初始角色...")
    for name, description in ROLES_CONFIG.items():
        existing_role = db.session.query(Role).filter_by(name=name).first()
        if not existing_role:
            new_role = Role(
                name=name,
                description=description,
                permissions=0, # 默认权限，可根据需求调整
                created_at=datetime.utcnow()
            )
            db.session.add(new_role)
            print(f"    已添加角色: {name} - {description}")
        else:
            print(f"    角色 '{name}' 已存在，跳过。")
    # No commit here; it's handled by db_test_and_init.py