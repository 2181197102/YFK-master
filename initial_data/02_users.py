# initial_data/02_users.py
from modules.auth.models import User
from datetime import datetime

# username, 密码, 姓名, 年龄, 性别
USERS_TO_ADD = [
    ("admin",           "adminpass",      "系统管理员",   30, "M"),
    ("patient_alice",   "patientpass",    "Alice 患者",   25, "F"),
    ("patient_bob",     "patientpass",    "Bob 患者",     28, "M"),
    ("dr_smith",        "doctorpass",     "Dr. Smith",    40, "M"),
    ("researcher_eve",  "researchpass",   "Eve 研究员",   35, "F"),
]

def insert_data(db):
    """插入初始用户数据；角色关联放到 03_user_roles.py。"""
    print("  - 正在插入初始用户…")
    for uname, pwd, name, age, gender in USERS_TO_ADD:
        existing = db.session.query(User).filter_by(username=uname).first()
        if existing:
            print(f"    用户 '{uname}' 已存在，跳过。")
            continue

        user = User(
            username=uname,
            name=name,
            age=age,
            gender=gender,
            enable=True,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        user.set_password(pwd)
        db.session.add(user)
        print(f"    已添加用户: {uname}")
