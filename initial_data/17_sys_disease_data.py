from modules.ins.models import db, Disease_data
from datetime import datetime

# 1. 核心配置：每个病种对应的英文字段列表（严格对应ins3_record_data模型）
DISEASE_EN_FIELDS = {
    "I10": [  # 高血压对应的英文字段
        "smoking_history",
        "drinking_history",
        "hypertension_history",
        "blood_type",
        "heart_rate",
        "triglyceride",
        "total_cholesterol",
        "hdl_cholesterol",
        "ldl_cholesterol",
        "left_ventricular_ejection_fraction",
        "serum_creatinine",
        "troponin",
        "diagnosis_name_code",
        "planned_operation_code",
        "transfusion_method",
        "drug_name",
        "medication_guidance",
        "cost"
    ],
    "I25.1": [  # 冠心病对应的英文字段
        "smoking_start_age",
        "smoking_quit_age",
        "occupational_dust_exposure",
        "environmental_risk_factors",
        "fev1",
        "fev1_fvc_ratio",
        "tlc",
        "frc",
        "dlco",
        "dlco_va_ratio",
        "pef",
        "cat_score",
        "mmrc_score",
        "spo2",
        "diagnosis_name_code",
        "drug_name",
        "medication_guidance",
        "lifestyle_guidance",
        "cost"
    ],
    "E10": [  # 糖尿病对应的英文字段
        "family_history",
        "medication_history",
        "daily_staple_food",
        "exercise_method",
        "exercise_duration",
        "fasting_blood_glucose",
        "postprandial_blood_glucose",
        "hypoglycemia_code",
        "hba1c",
        "insulin",
        "c_peptide",
        "abdominal_ultrasound",
        "fundus_examination",
        "lower_limb_vascular_ultrasound",
        "diagnosis_name_code",
        "drug_name",
        "medication_guidance",
        "lifestyle_guidance",
        "cost"
    ],
    "J44": [  # 慢阻肺对应的英文字段
        "smoking_history",
        "drinking_history",
        "family_history",
        "past_history",
        "bmi",
        "waist_circumference",
        "heart_rate",
        "sitting_standing_blood_pressure",
        "ambulatory_blood_pressure_24h",
        "serum_creatinine",  # 与“血肌酐”统一为模型字段serum_creatinine
        "blood_uric_acid",
        "fundus_examination",
        "urine_microalbumin_creatinine_ratio",
        "arterial_stiffness",
        "diagnosis_name_code",
        "drug_name",
        "medication_guidance",
        "cost"
    ]
}

# 2. 英文字段敏感规则（敏感=0.8，非敏感=0.1）
EN_FIELD_SENSITIVE = {
    # 非敏感字段（健康状况信息）
    "smoking_history": 0.1,
    "drinking_history": 0.1,
    "family_history": 0.1,
    "past_history": 0.1,
    "medication_history": 0.1,
    "occupational_dust_exposure": 0.1,
    "environmental_risk_factors": 0.1,
    "hypertension_history": 0.1,
    "smoking_start_age": 0.1,
    "smoking_quit_age": 0.1,
    "daily_staple_food": 0.1,
    "exercise_method": 0.1,
    "exercise_duration": 0.1,
    "blood_type": 0.1,
    "heart_rate": 0.1,
    "bmi": 0.1,
    "waist_circumference": 0.1,
    "sitting_standing_blood_pressure": 0.1,
    "ambulatory_blood_pressure_24h": 0.1,
    "spo2": 0.1,
    "arterial_stiffness": 0.1,
    "triglyceride": 0.1,
    "total_cholesterol": 0.1,
    "hdl_cholesterol": 0.1,
    "ldl_cholesterol": 0.1,
    "left_ventricular_ejection_fraction": 0.1,
    "serum_creatinine": 0.1,
    "troponin": 0.1,
    "blood_uric_acid": 0.1,
    "fasting_blood_glucose": 0.1,
    "postprandial_blood_glucose": 0.1,
    "hypoglycemia_code": 0.1,
    "hba1c": 0.1,
    "insulin": 0.1,
    "c_peptide": 0.1,
    "urine_microalbumin_creatinine_ratio": 0.1,
    "fundus_examination": 0.1,
    "abdominal_ultrasound": 0.1,
    "lower_limb_vascular_ultrasound": 0.1,
    "fev1": 0.1,
    "fev1_fvc_ratio": 0.1,
    "tlc": 0.1,
    "frc": 0.1,
    "dlco": 0.1,
    "dlco_va_ratio": 0.1,
    "pef": 0.1,
    "cat_score": 0.1,
    "mmrc_score": 0.1,
    # 敏感字段（诊疗服务/费用信息）
    "diagnosis_name_code": 0.8,
    "planned_operation_code": 0.8,
    "transfusion_method": 0.8,
    "drug_name": 0.8,
    "medication_guidance": 0.8,
    "lifestyle_guidance": 0.8,
    "cost": 0.8
}

# 3. 每个病种的similar值（按需求或业务逻辑调整）
DISEASE_SIMILAR = {
    "I10": 0.2,
    "I25.1": 0.3,
    "E10": 0.4,
    "J44": 0.25
}


def insert_data(db):
    """插入病种-英文字段关联数据，按规则设置敏感值"""
    print("  - Starting to insert disease-field data...")

    for disease_code, en_fields in DISEASE_EN_FIELDS.items():
        print(f"\n    Processing disease: {disease_code} (Total fields: {len(en_fields)})")
        current_similar = DISEASE_SIMILAR[disease_code]

        for en_field in en_fields:
            # 获取当前字段的敏感值
            sensitive = EN_FIELD_SENSITIVE[en_field]
            # 创建记录（仅使用英文字段）
            record = Disease_data(
                disease_code=disease_code,
                data_code=en_field,  # 存储模型对应的英文字段名
                similar=current_similar,
                sensitive=sensitive,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(record)
            print(f"      Added field: {en_field} (sensitive: {sensitive})")

        # 批量提交当前病种数据
        try:
            db.session.commit()
            print(f"    Successfully committed data for disease: {disease_code}")
        except Exception as e:
            db.session.rollback()
            print(f"    Failed to commit data for disease {disease_code}: {str(e)}")
            continue

    print("\n  - All disease-field data processing completed!")

