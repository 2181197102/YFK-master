# initial_data/02_users.py
from modules.ins.models import ins_doctor_record
from datetime import datetime

DOCTOR_PATIENT_RECORDS = [
    # (医生姓名, 医生编码, 患者姓名, 患者身份证号, 病历号)
    ("张伟", "DOC202309000000001", "李明", "110101199001011234", "1"),
    ("李娜", "DOC202309000000002", "王芳", "310104199205206789", "2"),
    ("王建国", "DOC202309000000003", "赵强", "440301198512081234", "3"),
    ("刘敏", "DOC202309000000004", "孙梅", "120103198809125678", "4"),
    ("陈明", "DOC202309000000005", "周丽", "510104199507259012", "5"),
    ("陈明", "DOC202309000000005", "周丽", "510104199507259012", "6"),
]

def insert_data(db):
    """插入初始用户数据；角色关联放到 03_user_roles.py。"""
    print("  - 正在插入初始用户…")
    for doctor_name, doctor_code, patient_name, patient_id_num, medical_record_num in DOCTOR_PATIENT_RECORDS:
        existing = db.session.query(ins_doctor_record).filter_by(medical_record_num=medical_record_num).first()
        if existing:
            print(f"    用户 '{medical_record_num}' 已存在，跳过。")
            continue

        record = ins_doctor_record(
            doctor_name=doctor_name,
            doctor_code=doctor_code,
            patient_name=patient_name,
            patient_id_num=patient_id_num,
            medical_record_num=medical_record_num,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(record)
        print(f"    已添加医生病历: {medical_record_num}")