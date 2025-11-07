# initial_data/02_users.py
from modules.auth.models import User
from datetime import datetime

# username, 密码, 姓名, 年龄, 性别, 身份证号码, 手机号码
USERS_TO_ADD = [
    ("admin",           "adminpass",      "系统管理员",   30, "M", "110101199001010001", "13800138001"),
    ("patient_alice",   "patientpass",    "Alice 患者",  25, "F", "110101199501010002", "13800138002"),
    ("patient_bob",     "patientpass",    "Bob 患者",    28, "M", "110101199201010003", "13800138003"),
    ("dr_smith",        "doctorpass",     "Dr. Smith",  40, "M", "110101198001010004", "13800138004"),
    ("researcher_eve",  "researchpass",   "Eve 研究员",   35, "F", "110101198501010005", "13800138005"),
    ("researcher_fh",   "researchpass",   "fh 研究员",    35, "F", "110101198501010006", "13800138006"),
    ("zhangwei",        "doctorpass",     "张伟",        35, "F", "110101198501010007", "13800138007"),
    ("lina",            "doctorpass",     "李娜",        35, "F", "110101198501010008", "13800138008"),
    ("wangjiangguo",    "doctorpass",     "王建国",      35, "F",  "110101198501010009", "13800138009"),
    ("liumin",          "doctorpass",     "刘敏",        35, "F",  "110101198501010010", "13800138010"),
    ("chenming",        "doctorpass",     "陈明",        35, "F",  "110101198501010011", "13800138011"),
    ("wumin",        "patientpass",     "吴敏",        25, "F",  "230101199908308901", "13800138012"),
    ("zhaoda", "doctorpass", "赵大", 35, "F", "110101198501010013", "13800138013"),
]

def insert_data(db):
    """插入初始用户数据；角色关联放到 03_user_roles.py。"""
    print("  - 正在插入初始用户…")
    for uname, pwd, name, age, gender, id_card, phone in USERS_TO_ADD:
        existing = db.session.query(User).filter_by(username=uname).first()
        if existing:
            print(f"    用户 '{uname}' 已存在，跳过。")
            continue

        user = User(
            username=uname,
            name=name,
            age=age,
            gender=gender,
            id_card=id_card,
            phone=phone,
            enable=True,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        user.set_password(pwd)
        db.session.add(user)
        print(f"    已添加用户: {uname} (身份证: {id_card})")