# initial_data/18_medical_institutions_sample.py

from modules.medical_institutions.models import (
    PatientMedicalRecord, MedicalRecordDisease, 
    MedicalRecordDataItem, DoctorMedicalRecord
)
from modules.data_management.models import ICD10Code
from modules.auth.models import User
from datetime import datetime, timedelta, timezone
import random
import json

def insert_data(db):
    """
    插入医疗机构相关的示例数据
    """
    print("  - 正在插入初始数据 (Medical Institutions)...")

    # 获取现有用户作为患者和医生
    users = db.session.query(User).all()
    if not users:
        print("    警告: 未找到用户数据，跳过医疗机构数据插入。")
        return

    # 获取一些ICD-10疾病编码
    icd_codes = db.session.query(ICD10Code).limit(10).all()
    if not icd_codes:
        print("    警告: 未找到ICD-10疾病编码，跳过医疗机构数据插入。")
        return

    # 定义医生信息
    doctors = [
        {"name": "张医生", "code": "DOC001"},
        {"name": "李医生", "code": "DOC002"},
        {"name": "王医生", "code": "DOC003"},
        {"name": "刘医生", "code": "DOC004"},
        {"name": "陈医生", "code": "DOC005"}
    ]

    # 创建患者病历
    record_id_counter = 1
    patient_users = [user for user in users if any(role.name == "PATIENT" for role in user.roles)]
    
    for i, patient in enumerate(patient_users[:5]):  # 限制为前5个患者
        doctor = random.choice(doctors)
        
        # 创建病历
        record_id = f"rec_{patient.id_card}_{datetime.now(timezone.utc).strftime('%Y%m%d')}{record_id_counter:03d}"
        
        medical_record = PatientMedicalRecord(
            id=record_id,
            patient_id_num=patient.id_card,
            patient_name=patient.username,
            patient_sex=random.choice([1, 2]),  # 1男2女
            doctor_code=doctor["code"],
            created_time=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
            updated_time=datetime.now(timezone.utc)
        )
        
        db.session.add(medical_record)
        print(f"    已添加患者病历: {record_id} - {patient.username}")
        
        # 为病历添加疾病诊断
        selected_diseases = random.sample(icd_codes, min(3, len(icd_codes)))
        for disease in selected_diseases:
            disease_record = MedicalRecordDisease(
                id=f"mrd_{record_id}_{disease.code}_{record_id_counter}",
                medical_record_num=record_id,
                disease_code=disease.code,
                created_time=datetime.now(timezone.utc),
                updated_time=datetime.now(timezone.utc)
            )
            db.session.add(disease_record)
            print(f"      添加疾病诊断: {disease.code}")
        
        # 为病历添加数据项
        data_items = [
            {
                "associated_code": "PATIENT_BASIC_INFO",
                "data_fields": {
                    "age": random.randint(20, 80),
                    "height": random.randint(150, 190),
                    "weight": random.randint(45, 90)
                }
            },
            {
                "associated_code": "BLOOD_PRESSURE",
                "data_fields": {
                    "systolic": random.randint(90, 160),
                    "diastolic": random.randint(60, 100),
                    "measurement_time": datetime.now(timezone.utc).isoformat()
                }
            },
            {
                "associated_code": "BLOOD_ROUTINE",
                "data_fields": {
                    "white_blood_cell": round(random.uniform(4.0, 10.0), 2),
                    "red_blood_cell": round(random.uniform(4.0, 5.5), 2),
                    "hemoglobin": round(random.uniform(120, 160), 1)
                }
            }
        ]
        
        for item_data in data_items:
            data_item = MedicalRecordDataItem(
                id=f"mdi_{record_id}_{item_data['associated_code']}_{record_id_counter}",
                medical_record_num=record_id,
                associated_code=item_data["associated_code"],
                created_time=datetime.now(timezone.utc),
                updated_time=datetime.now(timezone.utc)
            )
            data_item.set_data_fields_dict(item_data["data_fields"])
            db.session.add(data_item)
            print(f"      添加数据项: {item_data['associated_code']}")
        
        # 创建医生-病历关联
        doctor_record = DoctorMedicalRecord(
            id=f"dmr_{doctor['code']}_{record_id}_{record_id_counter}",
            doctor_name=doctor["name"],
            doctor_code=doctor["code"],
            patient_name=patient.username,
            patient_id_num=patient.id_card,
            medical_record_num=record_id,
            created_time=datetime.now(timezone.utc),
            updated_time=datetime.now(timezone.utc)
        )
        db.session.add(doctor_record)
        print(f"      添加医生关联: {doctor['name']} ({doctor['code']})")
        
        record_id_counter += 1

    print("  - Medical Institutions 数据插入完成。")
    # 事务提交由 db_test_and_init.py 处理
