# initial_data/03_user_roles.py
from modules.auth.models import User, Role, UserRoleRelation
from datetime import datetime

# 用户‑角色映射（username, role_code）
USER_ROLE_MAP = [
    ("admin",          ["ADMIN"]),
    ("patient_alice",  ["PATIENT"]),
    ("patient_bob",    ["PATIENT"]),
    ("dr_smith",       ["FAMILY_DOCTOR", "ATTENDING_DOCTOR"]),
    ("researcher_eve", ["RESEARCHER"]),
]

def insert_data(db):
    """插入用户‑角色关联。"""
    print("  - 正在插入用户‑角色关联…")
    for uname, role_codes in USER_ROLE_MAP:
        user = db.session.query(User).filter_by(username=uname).first()
        if not user:
            print(f"    警告: 未找到用户 '{uname}'。")
            continue

        for code in role_codes:
            role = db.session.query(Role).filter_by(role_code=code).first()
            if not role:
                print(f"    警告: 未找到角色 '{code}'。")
                continue

            exists = db.session.query(UserRoleRelation).filter_by(
                user_id=user.id, role_id=role.id
            ).first()
            if exists:
                print(f"    用户 '{uname}' 已关联角色 '{code}'，跳过。")
                continue

            rel = UserRoleRelation(
                user_id=user.id,
                role_id=role.id,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow(),
            )
            db.session.add(rel)
            print(f"    已关联用户 '{uname}' ↔ 角色 '{code}'")
