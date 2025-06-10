# initial_data/02_users.py

from models.models import User # 只需要 User 模型
from werkzeug.security import generate_password_hash
from datetime import datetime

def insert_data(db):
    """
    插入初始用户数据。
    用户在此处创建，角色的关联在 03_user_roles.py 中处理。
    """
    print("  - 正在插入初始用户...")

    users_to_add = [
        {"username": "admin", "email": "admin@example.com", "password": "adminpass"},
        {"username": "patient_alice", "email": "alice@patient.com", "password": "patientpass"},
        {"username": "patient_bob", "email": "bob@patient.com", "password": "patientpass"},
        {"username": "dr_smith", "email": "dr.smith@hospital.com", "password": "doctorpass"},
        {"username": "researcher_eve", "email": "eve@research.com", "password": "researchpass"},
    ]

    for user_data in users_to_add:
        existing_user = db.session.query(User).filter_by(username=user_data["username"]).first()
        if not existing_user:
            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_user)
            print(f"    已添加用户: {user_data['username']}")
        else:
            print(f"    用户 '{user_data['username']}' 已存在，跳过。")
    # No commit here; it's handled by db_test_and_init.py