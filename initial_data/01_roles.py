# initial_data/01_roles.py
from modules.auth.models import Role
from datetime import datetime

# 角色配置：{角色代码: 角色名称}
ROLES_CONFIG = {
    "PATIENT": "患者",
    "FAMILY_DOCTOR": "家庭医生",
    "ATTENDING_DOCTOR": "主治医生",
    "CROSS_HOSPITAL_DOCTOR": "跨院医生",
    "EMERGENCY_DOCTOR": "急救医生",
    "RESEARCHER": "科研人员",
    "ADMIN": "管理员",
}

def insert_data(db):
    """插入初始角色数据。"""
    print("  - 正在插入初始角色…")
    for code, name in ROLES_CONFIG.items():
        existing = db.session.query(Role).filter_by(role_code=code).first()
        if existing:
            print(f"    角色 '{code}' 已存在，跳过。")
            continue

        role = Role(
            role_code=code,
            role_name=name,
            description=f"系统预设角色：{name}",
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(role)
        print(f"    已添加角色: {code} - {name}")
