# initial_data/02_users.py
from modules.ins.models import ins_record
from datetime import datetime

USER_EXAMPLES = [
    # (姓名, 年龄, 性别, 身份证号, 医生编码)
    ("王建国", 45, "男", "110101197803152345", "DOC2023000001"),
    ("李小红", 32, "女", "310104199105206789", "DOC2023000002"),
    ("张伟", 28, "男", "440301199512081234", "PAT2023000001"),
    ("刘芳", 50, "女", "120103197309125678", "PAT2023000002"),
    ("赵明", 36, "男", "510104198707259012", "DOC2023000003"),
    ("孙梅", 22, "女", "610102200103183456", "PAT2023000003"),
    ("周强", 55, "男", "320105196811057890", "DOC2023000004"),
]

def insert_data(db):
    """插入初始用户数据；角色关联放到 03_user_roles.py。"""
    print("  - 正在插入初始用户…")
    for name, age, gender, id_card, doctor_code in USER_EXAMPLES:
        existing = db.session.query(ins_record).filter_by(name=name).first()
        if existing:
            print(f"    用户 '{name}' 已存在，跳过。")
            continue
        record = ins_record(
            name=name,
            age=age,
            gender=gender,
            id_card=id_card,
            doctor_code=doctor_code,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(record)
        print(f"    已添加用户: {record} (身份证: {id_card})")