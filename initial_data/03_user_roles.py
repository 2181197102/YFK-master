# initial_data/03_user_roles.py

from models.models import User, Role, UserRole
from datetime import datetime

def insert_data(db):
    """
    插入初始用户-角色关联数据。
    """
    print("  - 正在插入初始用户-角色关联...")

    # 获取用户和角色
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    patient_bob = db.session.query(User).filter_by(username="patient_bob").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()


    admin_role = db.session.query(Role).filter_by(name="ADMIN").first()
    patient_role = db.session.query(Role).filter_by(name="PATIENT").first()
    family_doctor_role = db.session.query(Role).filter_by(name="FAMILY_DOCTOR").first()
    attending_doctor_role = db.session.query(Role).filter_by(name="ATTENDING_DOCTOR").first()
    researcher_role = db.session.query(Role).filter_by(name="RESEARCHER").first()

    # 定义要创建的关联
    associations_to_add = []

    if admin_user and admin_role:
        associations_to_add.append({"user": admin_user, "role": admin_role})
    else:
        if not admin_user: print("    警告: 未找到 'admin' 用户。")
        if not admin_role: print("    警告: 未找到 'ADMIN' 角色。")

    if patient_alice and patient_role:
        associations_to_add.append({"user": patient_alice, "role": patient_role})
    else:
        if not patient_alice: print("    警告: 未找到 'patient_alice' 用户。")
        if not patient_role: print("    警告: 未找到 'PATIENT' 角色。")

    if patient_bob and patient_role:
        associations_to_add.append({"user": patient_bob, "role": patient_role})

    if dr_smith and family_doctor_role:
        associations_to_add.append({"user": dr_smith, "role": family_doctor_role})
    if dr_smith and attending_doctor_role: # 示例：医生可以有多个角色
        associations_to_add.append({"user": dr_smith, "role": attending_doctor_role})
    else:
        if not dr_smith: print("    警告: 未找到 'dr_smith' 用户。")
        if not family_doctor_role: print("    警告: 未找到 'FAMILY_DOCTOR' 角色。")
        if not attending_doctor_role: print("    警告: 未找到 'ATTENDING_DOCTOR' 角色。")

    if researcher_eve and researcher_role:
        associations_to_add.append({"user": researcher_eve, "role": researcher_role})
    else:
        if not researcher_eve: print("    警告: 未找到 'researcher_eve' 用户。")
        if not researcher_role: print("    警告: 未找到 'RESEARCHER' 角色。")

    for assoc in associations_to_add:
        existing_association = db.session.query(UserRole).filter_by(
            user_id=assoc["user"].id,
            role_id=assoc["role"].id
        ).first()
        if not existing_association:
            new_user_role = UserRole(
                user_id=assoc["user"].id,
                role_id=assoc["role"].id,
                created_at=datetime.utcnow()
            )
            db.session.add(new_user_role)
            print(f"    已关联用户 '{assoc['user'].username}' 与角色 '{assoc['role'].name}'。")
        else:
            print(f"    用户 '{assoc['user'].username}' 与角色 '{assoc['role'].name}' 的关联已存在，跳过。")
    # No commit here; it's handled by db_test_and_init.py