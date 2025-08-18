# initial_data/16_data_items.py

from modules.data_items.models import DataItem
from datetime import datetime

def insert_data(db):
    """
    插入数据项初始数据
    """
    print("  - 正在插入初始数据 (DataItem)...")

    # 定义常见的医疗数据项
    data_items = [
        {"associated_name": "患者基本信息", "associated_code": "PATIENT_BASIC_INFO"},
        {"associated_name": "发病时间", "associated_code": "ONSET_TIME"},
        {"associated_name": "临床症状", "associated_code": "CLINICAL_SYMPTOMS"},
        {"associated_name": "体温", "associated_code": "BODY_TEMPERATURE"},
        {"associated_name": "血压", "associated_code": "BLOOD_PRESSURE"},
        {"associated_name": "心率", "associated_code": "HEART_RATE"},
        {"associated_name": "血常规", "associated_code": "BLOOD_ROUTINE"},
        {"associated_name": "肝功能检查", "associated_code": "LIVER_FUNCTION"},
        {"associated_name": "肾功能检查", "associated_code": "KIDNEY_FUNCTION"},
        {"associated_name": "心电图", "associated_code": "ECG"},
        {"associated_name": "胸部X光", "associated_code": "CHEST_XRAY"},
        {"associated_name": "CT扫描", "associated_code": "CT_SCAN"},
        {"associated_name": "MRI检查", "associated_code": "MRI_EXAM"},
        {"associated_name": "超声检查", "associated_code": "ULTRASOUND"},
        {"associated_name": "治疗方案", "associated_code": "TREATMENT_PLAN"},
        {"associated_name": "用药记录", "associated_code": "MEDICATION_RECORD"},
        {"associated_name": "手术记录", "associated_code": "SURGERY_RECORD"},
        {"associated_name": "护理记录", "associated_code": "NURSING_RECORD"},
        {"associated_name": "出院小结", "associated_code": "DISCHARGE_SUMMARY"},
        {"associated_name": "复查计划", "associated_code": "FOLLOWUP_PLAN"},
        {"associated_name": "病理检查", "associated_code": "PATHOLOGY_EXAM"},
        {"associated_name": "免疫检查", "associated_code": "IMMUNOLOGY_TEST"},
        {"associated_name": "内镜检查", "associated_code": "ENDOSCOPY"},
        {"associated_name": "放射治疗", "associated_code": "RADIOTHERAPY"},
        {"associated_name": "化疗记录", "associated_code": "CHEMOTHERAPY"}
    ]

    item_id_counter = 1

    for item_data in data_items:
        # 检查是否已存在相同的数据项
        existing_item = db.session.query(DataItem).filter_by(
            associated_code=item_data["associated_code"]
        ).first()
        
        if not existing_item:
            item_id = f"di_{item_id_counter:03d}"
            
            new_item = DataItem(
                id=item_id,
                associated_name=item_data["associated_name"],
                associated_code=item_data["associated_code"],
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            
            db.session.add(new_item)
            print(f"    已添加数据项: {item_data['associated_code']} - {item_data['associated_name']}")
            
        else:
            print(f"    数据项 {item_data['associated_code']} 已存在，跳过。")
            
        item_id_counter += 1

    print("  - DataItem 数据插入完成。")
    # 事务提交由 db_test_and_init.py 处理
