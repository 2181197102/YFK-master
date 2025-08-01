# initial_data/02_users.py
from modules.ins.models import ins_record_data
from datetime import datetime

MEDICAL_DATA_EXAMPLES = [
    # (病历号, 数据编码1, 数据编码2, 数据编码3, 数据编码4, 数据编码5, 数据编码6, 数据编码7, 数据编码8, 数据编码9)
    ("1", "1", "0", "0", "1", "0", "0", "1", "0", "1"),
    ("2", "1", "1", "1", "0", "0", "0", "0", "0", "0"),
    ("3", "1", "0", "0", "0", "0", "1", "0", "1", "0"),
    ("4", "0", "1", "1", "0", "0", "1", "0", "0", "0"),
    ("5", "0", "0", "0", "1", "0", "1", "1", "1", "0"),
    ("6", "0", "0", "0", "1", "0", "1", "1", "1", "0"),
]

def insert_data(db):
    """插入初始用户数据；角色关联放到 03_user_roles.py。"""
    print("  - 正在插入初始用户…")
    for medical_record_num, data_code1, data_code2, data_code3, data_code4, data_code5, data_code6, data_code7, data_code8, data_code9 in MEDICAL_DATA_EXAMPLES:
        existing = db.session.query(ins_record_data).filter_by(medical_record_num=medical_record_num).first()
        if existing:
            print(f"    用户 '{medical_record_num}' 已存在，跳过。")
            continue

        record = ins_record_data(
            medical_record_num=medical_record_num,
            data_code1=data_code1,
            data_code2=data_code2,
            data_code3=data_code3,
            data_code4=data_code4,
            data_code5=data_code5,
            data_code6=data_code6,
            data_code7=data_code7,
            data_code8=data_code8,
            data_code9=data_code9,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(record)
        print(f"    已添加病历数据项: {medical_record_num}")