# initial_data/02_users.py
from modules.ins.models import ins_record_disease
from datetime import datetime

MEDICAL_RECORD_EXAMPLES = [
    # (病历号, 数据编码1)
    ("1", "a"),
    ("2", "a"),
    ("3", "b"),
    ("4", "b"),
    ("5", "c"),
    ("6", "d"),
]

def insert_data(db):
    """插入初始用户数据；角色关联放到 03_user_roles.py。"""
    print("  - 正在插入初始用户…")
    for medical_record_num, disease_code in MEDICAL_RECORD_EXAMPLES:
        existing = db.session.query(ins_record_disease).filter_by(medical_record_num=medical_record_num).first()
        if existing:
            print(f"    用户 '{medical_record_num}' 已存在，跳过。")
            continue

        record = ins_record_disease(
            medical_record_num=medical_record_num,
            disease_code=disease_code,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(record)
        print(f"    已添加病历病种: {medical_record_num}")