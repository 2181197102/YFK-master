# modules/auth/models.py
from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ----------------------- 病历表 -----------------------
class ins1_record(db.Model):
    __tablename__ = 'ins1_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 姓名字段
    age = db.Column(db.Integer, nullable=False)  # 年龄字段
    gender = db.Column(db.String(10), nullable=False)  # 性别字段
    id_card = db.Column(db.String(18), unique=False, nullable=False)  # 身份证号码，作为唯一标识
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'id_card': self.id_card,
            'doctor_code': self.doctor_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历-病种表 -----------------------
class ins1_record_disease(db.Model):
    __tablename__ = 'ins1_record_disease'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识
    disease_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'disease_code': self.disease_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------------- 病历-数据项表 -----------------------
class ins1_record_data(db.Model):
    __tablename__ = 'ins1_record_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识

    # 基础健康信息
    smoking_history = db.Column(db.String(50), nullable=False, comment='吸烟史')
    drinking_history = db.Column(db.String(50), nullable=False, comment='饮酒史')
    hypertension_history = db.Column(db.String(50), nullable=False, comment='高血压史')
    blood_type = db.Column(db.String(50), nullable=False, comment='血型')
    heart_rate = db.Column(db.String(50), nullable=False, comment='心率')
    triglyceride = db.Column(db.String(50), nullable=False, comment='甘油三酯')
    total_cholesterol = db.Column(db.String(50), nullable=False, comment='总胆固醇')
    hdl_cholesterol = db.Column(db.String(50), nullable=False, comment='高密度脂蛋白胆固醇')
    ldl_cholesterol = db.Column(db.String(50), nullable=False, comment='低密度脂蛋白胆固醇')
    left_ventricular_ejection_fraction = db.Column(db.String(50), nullable=False, comment='左心室射血分数')
    serum_creatinine = db.Column(db.String(50), nullable=False, comment='血清肌酐')
    troponin = db.Column(db.String(50), nullable=False, comment='肌钙蛋白')

    # 诊断与治疗相关
    diagnosis_name_code = db.Column(db.String(50), nullable=False, comment='诊断名称及代码')
    planned_operation_code = db.Column(db.String(50), nullable=False, comment='拟实施手术及操作编码')
    transfusion_method = db.Column(db.String(50), nullable=False, comment='输血方式')
    drug_name = db.Column(db.String(50), nullable=False, comment='药物名称')
    medication_guidance = db.Column(db.String(50), nullable=False, comment='用药指导')
    lifestyle_guidance = db.Column(db.String(50), nullable=False, comment='生活方式指导')
    cost = db.Column(db.String(50), nullable=False, comment='费用')

    # 吸烟相关信息
    smoking_start_age = db.Column(db.String(50), nullable=False, comment='开始吸烟年龄(岁)')
    smoking_quit_age = db.Column(db.String(50), nullable=False, comment='戒烟年龄(岁)')
    occupational_dust_exposure = db.Column(db.String(50), nullable=False, comment='职业性烟尘接触史')
    environmental_risk_factors = db.Column(db.String(50), nullable=False, comment='环境危险因素史')

    # 肺功能检查
    fev1 = db.Column(db.String(50), nullable=False, comment='肺功能检查-第一秒用力呼气容积(FEV1)')
    fev1_fvc_ratio = db.Column(db.String(50), nullable=False, comment='肺功能检查-第一秒用力呼气容积与用力肺活量百分比(FEV1/FVC)')
    tlc = db.Column(db.String(50), nullable=False, comment='肺功能检查-总肺活量(TLC)')
    frc = db.Column(db.String(50), nullable=False, comment='肺功能检查-功能参气量(FRC)')
    dlco = db.Column(db.String(50), nullable=False, comment='肺功能检查-一氧化碳弥散量(DLCO)')
    dlco_va_ratio = db.Column(db.String(50), nullable=False, comment='肺功能检查-一氧化碳弥散量(DLCO)与肺泡通气量(VA)比值(DLCO/VA)')
    pef = db.Column(db.String(50), nullable=False, comment='肺功能检查-峰流速(PEF)')
    cat_score = db.Column(db.String(50), nullable=False, comment='慢阻肺评估测试(CAT)')
    mmrc_score = db.Column(db.String(50), nullable=False, comment='改良版英国医学研究委员会呼吸困难问卷(mMRC)评分')
    spo2 = db.Column(db.String(50), nullable=False, comment='脉搏血氧饱和度（SpO2)')

    # 家族与用药史
    family_history = db.Column(db.String(50), nullable=False, comment='家族史')
    medication_history = db.Column(db.String(50), nullable=False, comment='用药史')
    past_history = db.Column(db.String(50), nullable=False, comment='既往史')

    # 生活方式
    daily_staple_food = db.Column(db.String(50), nullable=False, comment='日主食量(g)')
    exercise_method = db.Column(db.String(50), nullable=False, comment='运动方式')
    exercise_duration = db.Column(db.String(50), nullable=False, comment='运动时长')

    # 血糖相关
    fasting_blood_glucose = db.Column(db.String(50), nullable=False, comment='空腹血糖值(mmol/L)')
    postprandial_blood_glucose = db.Column(db.String(50), nullable=False, comment='餐后两小时血糖值(mmol/L)')
    hypoglycemia_code = db.Column(db.String(50), nullable=False, comment='低血糖反应代码')
    hba1c = db.Column(db.String(50), nullable=False, comment='糖化血红蛋白值(%)')
    insulin = db.Column(db.String(50), nullable=False, comment='胰岛素')
    c_peptide = db.Column(db.String(50), nullable=False, comment='C肽')

    # 检查项目
    abdominal_ultrasound = db.Column(db.String(50), nullable=False, comment='腹部彩超')
    fundus_examination = db.Column(db.String(50), nullable=False, comment='眼底检查')
    lower_limb_vascular_ultrasound = db.Column(db.String(50), nullable=False, comment='下肢血管彩超')
    urine_microalbumin_creatinine_ratio = db.Column(db.String(50), nullable=False, comment='尿微量白蛋白/肌酐比值')
    arterial_stiffness = db.Column(db.String(50), nullable=False, comment='动脉僵硬度')

    # 血压相关
    bmi = db.Column(db.String(50), nullable=False, comment='BMI指数')
    waist_circumference = db.Column(db.String(50), nullable=False, comment='腰围')
    sitting_standing_blood_pressure = db.Column(db.String(50), nullable=False, comment='坐位、立位血压')
    ambulatory_blood_pressure_24h = db.Column(db.String(50), nullable=False, comment='24h动态血压')
    blood_uric_acid = db.Column(db.String(50), nullable=False, comment='血尿酸')

    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'smoking_history': self.smoking_history,
            'drinking_history': self.drinking_history,
            'hypertension_history': self.hypertension_history,
            'blood_type': self.blood_type,
            'heart_rate': self.heart_rate,
            'triglyceride': self.triglyceride,
            'total_cholesterol': self.total_cholesterol,
            'hdl_cholesterol': self.hdl_cholesterol,
            'ldl_cholesterol': self.ldl_cholesterol,
            'left_ventricular_ejection_fraction': self.left_ventricular_ejection_fraction,
            'serum_creatinine': self.serum_creatinine,
            'troponin': self.troponin,
            'diagnosis_name_code': self.diagnosis_name_code,
            'planned_operation_code': self.planned_operation_code,
            'transfusion_method': self.transfusion_method,
            'drug_name': self.drug_name,
            'medication_guidance': self.medication_guidance,
            'lifestyle_guidance': self.lifestyle_guidance,
            'cost': self.cost,
            'smoking_start_age': self.smoking_start_age,
            'smoking_quit_age': self.smoking_quit_age,
            'occupational_dust_exposure': self.occupational_dust_exposure,
            'environmental_risk_factors': self.environmental_risk_factors,
            'fev1': self.fev1,
            'fev1_fvc_ratio': self.fev1_fvc_ratio,
            'tlc': self.tlc,
            'frc': self.frc,
            'dlco': self.dlco,
            'dlco_va_ratio': self.dlco_va_ratio,
            'pef': self.pef,
            'cat_score': self.cat_score,
            'mmrc_score': self.mmrc_score,
            'spo2': self.spo2,
            'family_history': self.family_history,
            'medication_history': self.medication_history,
            'past_history': self.past_history,
            'daily_staple_food': self.daily_staple_food,
            'exercise_method': self.exercise_method,
            'exercise_duration': self.exercise_duration,
            'fasting_blood_glucose': self.fasting_blood_glucose,
            'postprandial_blood_glucose': self.postprandial_blood_glucose,
            'hypoglycemia_code': self.hypoglycemia_code,
            'hba1c': self.hba1c,
            'insulin': self.insulin,
            'c_peptide': self.c_peptide,
            'abdominal_ultrasound': self.abdominal_ultrasound,
            'fundus_examination': self.fundus_examination,
            'lower_limb_vascular_ultrasound': self.lower_limb_vascular_ultrasound,
            'urine_microalbumin_creatinine_ratio': self.urine_microalbumin_creatinine_ratio,
            'arterial_stiffness': self.arterial_stiffness,
            'bmi': self.bmi,
            'waist_circumference': self.waist_circumference,
            'sitting_standing_blood_pressure': self.sitting_standing_blood_pressure,
            'ambulatory_blood_pressure_24h': self.ambulatory_blood_pressure_24h,
            'blood_uric_acid': self.blood_uric_acid,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------------- 医生-病历表 -----------------------
class ins1_doctor_record(db.Model):
    __tablename__ = 'ins1_doctor_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_name = db.Column(db.String(100), nullable=False)  # 姓名字段
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    patient_name = db.Column(db.String(18), unique=False, nullable=False)
    patient_id_num = db.Column(db.String(18), unique=False, nullable=False)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_name': self.doctor_name,
            'doctor_code': self.doctor_code,
            'patient_name': self.patient_name,
            'patient_id_num': self.patient_id_num,
            'medical_record_num': self.medical_record_num,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历表 -----------------------
class ins2_record(db.Model):
    __tablename__ = 'ins2_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 姓名字段
    age = db.Column(db.Integer, nullable=False)  # 年龄字段
    gender = db.Column(db.String(10), nullable=False)  # 性别字段
    id_card = db.Column(db.String(18), unique=False, nullable=False)  # 身份证号码，作为唯一标识
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'id_card': self.id_card,
            'doctor_code': self.doctor_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历-病种表 -----------------------
class ins2_record_disease(db.Model):
    __tablename__ = 'ins2_record_disease'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识
    disease_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'disease_code': self.disease_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历-数据项表 -----------------------
class ins2_record_data(db.Model):
    __tablename__ = 'ins2_record_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识

    # 基础健康信息
    smoking_history = db.Column(db.String(50), nullable=False, comment='吸烟史')
    drinking_history = db.Column(db.String(50), nullable=False, comment='饮酒史')
    hypertension_history = db.Column(db.String(50), nullable=False, comment='高血压史')
    blood_type = db.Column(db.String(50), nullable=False, comment='血型')
    heart_rate = db.Column(db.String(50), nullable=False, comment='心率')
    triglyceride = db.Column(db.String(50), nullable=False, comment='甘油三酯')
    total_cholesterol = db.Column(db.String(50), nullable=False, comment='总胆固醇')
    hdl_cholesterol = db.Column(db.String(50), nullable=False, comment='高密度脂蛋白胆固醇')
    ldl_cholesterol = db.Column(db.String(50), nullable=False, comment='低密度脂蛋白胆固醇')
    left_ventricular_ejection_fraction = db.Column(db.String(50), nullable=False, comment='左心室射血分数')
    serum_creatinine = db.Column(db.String(50), nullable=False, comment='血清肌酐')
    troponin = db.Column(db.String(50), nullable=False, comment='肌钙蛋白')

    # 诊断与治疗相关
    diagnosis_name_code = db.Column(db.String(50), nullable=False, comment='诊断名称及代码')
    planned_operation_code = db.Column(db.String(50), nullable=False, comment='拟实施手术及操作编码')
    transfusion_method = db.Column(db.String(50), nullable=False, comment='输血方式')
    drug_name = db.Column(db.String(50), nullable=False, comment='药物名称')
    medication_guidance = db.Column(db.String(50), nullable=False, comment='用药指导')
    lifestyle_guidance = db.Column(db.String(50), nullable=False, comment='生活方式指导')
    cost = db.Column(db.String(50), nullable=False, comment='费用')

    # 吸烟相关信息
    smoking_start_age = db.Column(db.String(50), nullable=False, comment='开始吸烟年龄(岁)')
    smoking_quit_age = db.Column(db.String(50), nullable=False, comment='戒烟年龄(岁)')
    occupational_dust_exposure = db.Column(db.String(50), nullable=False, comment='职业性烟尘接触史')
    environmental_risk_factors = db.Column(db.String(50), nullable=False, comment='环境危险因素史')

    # 肺功能检查
    fev1 = db.Column(db.String(50), nullable=False, comment='肺功能检查-第一秒用力呼气容积(FEV1)')
    fev1_fvc_ratio = db.Column(db.String(50), nullable=False, comment='肺功能检查-第一秒用力呼气容积与用力肺活量百分比(FEV1/FVC)')
    tlc = db.Column(db.String(50), nullable=False, comment='肺功能检查-总肺活量(TLC)')
    frc = db.Column(db.String(50), nullable=False, comment='肺功能检查-功能参气量(FRC)')
    dlco = db.Column(db.String(50), nullable=False, comment='肺功能检查-一氧化碳弥散量(DLCO)')
    dlco_va_ratio = db.Column(db.String(50), nullable=False, comment='肺功能检查-一氧化碳弥散量(DLCO)与肺泡通气量(VA)比值(DLCO/VA)')
    pef = db.Column(db.String(50), nullable=False, comment='肺功能检查-峰流速(PEF)')
    cat_score = db.Column(db.String(50), nullable=False, comment='慢阻肺评估测试(CAT)')
    mmrc_score = db.Column(db.String(50), nullable=False, comment='改良版英国医学研究委员会呼吸困难问卷(mMRC)评分')
    spo2 = db.Column(db.String(50), nullable=False, comment='脉搏血氧饱和度（SpO2)')

    # 家族与用药史
    family_history = db.Column(db.String(50), nullable=False, comment='家族史')
    medication_history = db.Column(db.String(50), nullable=False, comment='用药史')
    past_history = db.Column(db.String(50), nullable=False, comment='既往史')

    # 生活方式
    daily_staple_food = db.Column(db.String(50), nullable=False, comment='日主食量(g)')
    exercise_method = db.Column(db.String(50), nullable=False, comment='运动方式')
    exercise_duration = db.Column(db.String(50), nullable=False, comment='运动时长')

    # 血糖相关
    fasting_blood_glucose = db.Column(db.String(50), nullable=False, comment='空腹血糖值(mmol/L)')
    postprandial_blood_glucose = db.Column(db.String(50), nullable=False, comment='餐后两小时血糖值(mmol/L)')
    hypoglycemia_code = db.Column(db.String(50), nullable=False, comment='低血糖反应代码')
    hba1c = db.Column(db.String(50), nullable=False, comment='糖化血红蛋白值(%)')
    insulin = db.Column(db.String(50), nullable=False, comment='胰岛素')
    c_peptide = db.Column(db.String(50), nullable=False, comment='C肽')

    # 检查项目
    abdominal_ultrasound = db.Column(db.String(50), nullable=False, comment='腹部彩超')
    fundus_examination = db.Column(db.String(50), nullable=False, comment='眼底检查')
    lower_limb_vascular_ultrasound = db.Column(db.String(50), nullable=False, comment='下肢血管彩超')
    urine_microalbumin_creatinine_ratio = db.Column(db.String(50), nullable=False, comment='尿微量白蛋白/肌酐比值')
    arterial_stiffness = db.Column(db.String(50), nullable=False, comment='动脉僵硬度')

    # 血压相关
    bmi = db.Column(db.String(50), nullable=False, comment='BMI指数')
    waist_circumference = db.Column(db.String(50), nullable=False, comment='腰围')
    sitting_standing_blood_pressure = db.Column(db.String(50), nullable=False, comment='坐位、立位血压')
    ambulatory_blood_pressure_24h = db.Column(db.String(50), nullable=False, comment='24h动态血压')
    blood_uric_acid = db.Column(db.String(50), nullable=False, comment='血尿酸')

    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'smoking_history': self.smoking_history,
            'drinking_history': self.drinking_history,
            'hypertension_history': self.hypertension_history,
            'blood_type': self.blood_type,
            'heart_rate': self.heart_rate,
            'triglyceride': self.triglyceride,
            'total_cholesterol': self.total_cholesterol,
            'hdl_cholesterol': self.hdl_cholesterol,
            'ldl_cholesterol': self.ldl_cholesterol,
            'left_ventricular_ejection_fraction': self.left_ventricular_ejection_fraction,
            'serum_creatinine': self.serum_creatinine,
            'troponin': self.troponin,
            'diagnosis_name_code': self.diagnosis_name_code,
            'planned_operation_code': self.planned_operation_code,
            'transfusion_method': self.transfusion_method,
            'drug_name': self.drug_name,
            'medication_guidance': self.medication_guidance,
            'lifestyle_guidance': self.lifestyle_guidance,
            'cost': self.cost,
            'smoking_start_age': self.smoking_start_age,
            'smoking_quit_age': self.smoking_quit_age,
            'occupational_dust_exposure': self.occupational_dust_exposure,
            'environmental_risk_factors': self.environmental_risk_factors,
            'fev1': self.fev1,
            'fev1_fvc_ratio': self.fev1_fvc_ratio,
            'tlc': self.tlc,
            'frc': self.frc,
            'dlco': self.dlco,
            'dlco_va_ratio': self.dlco_va_ratio,
            'pef': self.pef,
            'cat_score': self.cat_score,
            'mmrc_score': self.mmrc_score,
            'spo2': self.spo2,
            'family_history': self.family_history,
            'medication_history': self.medication_history,
            'past_history': self.past_history,
            'daily_staple_food': self.daily_staple_food,
            'exercise_method': self.exercise_method,
            'exercise_duration': self.exercise_duration,
            'fasting_blood_glucose': self.fasting_blood_glucose,
            'postprandial_blood_glucose': self.postprandial_blood_glucose,
            'hypoglycemia_code': self.hypoglycemia_code,
            'hba1c': self.hba1c,
            'insulin': self.insulin,
            'c_peptide': self.c_peptide,
            'abdominal_ultrasound': self.abdominal_ultrasound,
            'fundus_examination': self.fundus_examination,
            'lower_limb_vascular_ultrasound': self.lower_limb_vascular_ultrasound,
            'urine_microalbumin_creatinine_ratio': self.urine_microalbumin_creatinine_ratio,
            'arterial_stiffness': self.arterial_stiffness,
            'bmi': self.bmi,
            'waist_circumference': self.waist_circumference,
            'sitting_standing_blood_pressure': self.sitting_standing_blood_pressure,
            'ambulatory_blood_pressure_24h': self.ambulatory_blood_pressure_24h,
            'blood_uric_acid': self.blood_uric_acid,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------------- 医生-病历表 -----------------------
class ins2_doctor_record(db.Model):
    __tablename__ = 'ins2_doctor_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_name = db.Column(db.String(100), nullable=False)  # 姓名字段
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    patient_name = db.Column(db.String(18), unique=False, nullable=False)
    patient_id_num = db.Column(db.String(18), unique=False, nullable=False)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_name': self.doctor_name,
            'doctor_code': self.doctor_code,
            'patient_name': self.patient_name,
            'patient_id_num': self.patient_id_num,
            'medical_record_num': self.medical_record_num,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历表 -----------------------
class ins3_record(db.Model):
    __tablename__ = 'ins3_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 姓名字段
    age = db.Column(db.Integer, nullable=False)  # 年龄字段
    gender = db.Column(db.String(10), nullable=False)  # 性别字段
    id_card = db.Column(db.String(18), unique=False, nullable=False)  # 身份证号码，作为唯一标识
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'id_card': self.id_card,
            'doctor_code': self.doctor_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历-病种表 -----------------------
class ins3_record_disease(db.Model):
    __tablename__ = 'ins3_record_disease'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识
    disease_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'disease_code': self.disease_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历-数据项表 -----------------------
class ins3_record_data(db.Model):
    __tablename__ = 'ins3_record_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识

    # 基础健康信息
    smoking_history = db.Column(db.String(50), nullable=False, comment='吸烟史')
    drinking_history = db.Column(db.String(50), nullable=False, comment='饮酒史')
    hypertension_history = db.Column(db.String(50), nullable=False, comment='高血压史')
    blood_type = db.Column(db.String(50), nullable=False, comment='血型')
    heart_rate = db.Column(db.String(50), nullable=False, comment='心率')
    triglyceride = db.Column(db.String(50), nullable=False, comment='甘油三酯')
    total_cholesterol = db.Column(db.String(50), nullable=False, comment='总胆固醇')
    hdl_cholesterol = db.Column(db.String(50), nullable=False, comment='高密度脂蛋白胆固醇')
    ldl_cholesterol = db.Column(db.String(50), nullable=False, comment='低密度脂蛋白胆固醇')
    left_ventricular_ejection_fraction = db.Column(db.String(50), nullable=False, comment='左心室射血分数')
    serum_creatinine = db.Column(db.String(50), nullable=False, comment='血清肌酐')
    troponin = db.Column(db.String(50), nullable=False, comment='肌钙蛋白')

    # 诊断与治疗相关
    diagnosis_name_code = db.Column(db.String(50), nullable=False, comment='诊断名称及代码')
    planned_operation_code = db.Column(db.String(50), nullable=False, comment='拟实施手术及操作编码')
    transfusion_method = db.Column(db.String(50), nullable=False, comment='输血方式')
    drug_name = db.Column(db.String(50), nullable=False, comment='药物名称')
    medication_guidance = db.Column(db.String(50), nullable=False, comment='用药指导')
    lifestyle_guidance = db.Column(db.String(50), nullable=False, comment='生活方式指导')
    cost = db.Column(db.String(50), nullable=False, comment='费用')

    # 吸烟相关信息
    smoking_start_age = db.Column(db.String(50), nullable=False, comment='开始吸烟年龄(岁)')
    smoking_quit_age = db.Column(db.String(50), nullable=False, comment='戒烟年龄(岁)')
    occupational_dust_exposure = db.Column(db.String(50), nullable=False, comment='职业性烟尘接触史')
    environmental_risk_factors = db.Column(db.String(50), nullable=False, comment='环境危险因素史')

    # 肺功能检查
    fev1 = db.Column(db.String(50), nullable=False, comment='肺功能检查-第一秒用力呼气容积(FEV1)')
    fev1_fvc_ratio = db.Column(db.String(50), nullable=False, comment='肺功能检查-第一秒用力呼气容积与用力肺活量百分比(FEV1/FVC)')
    tlc = db.Column(db.String(50), nullable=False, comment='肺功能检查-总肺活量(TLC)')
    frc = db.Column(db.String(50), nullable=False, comment='肺功能检查-功能参气量(FRC)')
    dlco = db.Column(db.String(50), nullable=False, comment='肺功能检查-一氧化碳弥散量(DLCO)')
    dlco_va_ratio = db.Column(db.String(50), nullable=False, comment='肺功能检查-一氧化碳弥散量(DLCO)与肺泡通气量(VA)比值(DLCO/VA)')
    pef = db.Column(db.String(50), nullable=False, comment='肺功能检查-峰流速(PEF)')
    cat_score = db.Column(db.String(50), nullable=False, comment='慢阻肺评估测试(CAT)')
    mmrc_score = db.Column(db.String(50), nullable=False, comment='改良版英国医学研究委员会呼吸困难问卷(mMRC)评分')
    spo2 = db.Column(db.String(50), nullable=False, comment='脉搏血氧饱和度（SpO2)')

    # 家族与用药史
    family_history = db.Column(db.String(50), nullable=False, comment='家族史')
    medication_history = db.Column(db.String(50), nullable=False, comment='用药史')
    past_history = db.Column(db.String(50), nullable=False, comment='既往史')

    # 生活方式
    daily_staple_food = db.Column(db.String(50), nullable=False, comment='日主食量(g)')
    exercise_method = db.Column(db.String(50), nullable=False, comment='运动方式')
    exercise_duration = db.Column(db.String(50), nullable=False, comment='运动时长')

    # 血糖相关
    fasting_blood_glucose = db.Column(db.String(50), nullable=False, comment='空腹血糖值(mmol/L)')
    postprandial_blood_glucose = db.Column(db.String(50), nullable=False, comment='餐后两小时血糖值(mmol/L)')
    hypoglycemia_code = db.Column(db.String(50), nullable=False, comment='低血糖反应代码')
    hba1c = db.Column(db.String(50), nullable=False, comment='糖化血红蛋白值(%)')
    insulin = db.Column(db.String(50), nullable=False, comment='胰岛素')
    c_peptide = db.Column(db.String(50), nullable=False, comment='C肽')

    # 检查项目
    abdominal_ultrasound = db.Column(db.String(50), nullable=False, comment='腹部彩超')
    fundus_examination = db.Column(db.String(50), nullable=False, comment='眼底检查')
    lower_limb_vascular_ultrasound = db.Column(db.String(50), nullable=False, comment='下肢血管彩超')
    urine_microalbumin_creatinine_ratio = db.Column(db.String(50), nullable=False, comment='尿微量白蛋白/肌酐比值')
    arterial_stiffness = db.Column(db.String(50), nullable=False, comment='动脉僵硬度')

    # 血压相关
    bmi = db.Column(db.String(50), nullable=False, comment='BMI指数')
    waist_circumference = db.Column(db.String(50), nullable=False, comment='腰围')
    sitting_standing_blood_pressure = db.Column(db.String(50), nullable=False, comment='坐位、立位血压')
    ambulatory_blood_pressure_24h = db.Column(db.String(50), nullable=False, comment='24h动态血压')
    blood_uric_acid = db.Column(db.String(50), nullable=False, comment='血尿酸')

    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'smoking_history': self.smoking_history,
            'drinking_history': self.drinking_history,
            'hypertension_history': self.hypertension_history,
            'blood_type': self.blood_type,
            'heart_rate': self.heart_rate,
            'triglyceride': self.triglyceride,
            'total_cholesterol': self.total_cholesterol,
            'hdl_cholesterol': self.hdl_cholesterol,
            'ldl_cholesterol': self.ldl_cholesterol,
            'left_ventricular_ejection_fraction': self.left_ventricular_ejection_fraction,
            'serum_creatinine': self.serum_creatinine,
            'troponin': self.troponin,
            'diagnosis_name_code': self.diagnosis_name_code,
            'planned_operation_code': self.planned_operation_code,
            'transfusion_method': self.transfusion_method,
            'drug_name': self.drug_name,
            'medication_guidance': self.medication_guidance,
            'lifestyle_guidance': self.lifestyle_guidance,
            'cost': self.cost,
            'smoking_start_age': self.smoking_start_age,
            'smoking_quit_age': self.smoking_quit_age,
            'occupational_dust_exposure': self.occupational_dust_exposure,
            'environmental_risk_factors': self.environmental_risk_factors,
            'fev1': self.fev1,
            'fev1_fvc_ratio': self.fev1_fvc_ratio,
            'tlc': self.tlc,
            'frc': self.frc,
            'dlco': self.dlco,
            'dlco_va_ratio': self.dlco_va_ratio,
            'pef': self.pef,
            'cat_score': self.cat_score,
            'mmrc_score': self.mmrc_score,
            'spo2': self.spo2,
            'family_history': self.family_history,
            'medication_history': self.medication_history,
            'past_history': self.past_history,
            'daily_staple_food': self.daily_staple_food,
            'exercise_method': self.exercise_method,
            'exercise_duration': self.exercise_duration,
            'fasting_blood_glucose': self.fasting_blood_glucose,
            'postprandial_blood_glucose': self.postprandial_blood_glucose,
            'hypoglycemia_code': self.hypoglycemia_code,
            'hba1c': self.hba1c,
            'insulin': self.insulin,
            'c_peptide': self.c_peptide,
            'abdominal_ultrasound': self.abdominal_ultrasound,
            'fundus_examination': self.fundus_examination,
            'lower_limb_vascular_ultrasound': self.lower_limb_vascular_ultrasound,
            'urine_microalbumin_creatinine_ratio': self.urine_microalbumin_creatinine_ratio,
            'arterial_stiffness': self.arterial_stiffness,
            'bmi': self.bmi,
            'waist_circumference': self.waist_circumference,
            'sitting_standing_blood_pressure': self.sitting_standing_blood_pressure,
            'ambulatory_blood_pressure_24h': self.ambulatory_blood_pressure_24h,
            'blood_uric_acid': self.blood_uric_acid,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 医生-病历表 -----------------------
class ins3_doctor_record(db.Model):
    __tablename__ = 'ins3_doctor_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_name = db.Column(db.String(100), nullable=False)  # 姓名字段
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    patient_name = db.Column(db.String(18), unique=False, nullable=False)
    patient_id_num = db.Column(db.String(18), unique=False, nullable=False)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_name': self.doctor_name,
            'doctor_code': self.doctor_code,
            'patient_name': self.patient_name,
            'patient_id_num': self.patient_id_num,
            'medical_record_num': self.medical_record_num,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------- 疾病-数据项关联表 -----------------
class Disease_data(db.Model):
    __tablename__ = 'sys_disease_data'
    id      = db.Column(db.Integer, primary_key=True)
    disease_code = db.Column(db.String(18), unique=False, nullable=False)
    data_code = db.Column(db.String(50), unique=False, nullable=False)
    similar = db.Column(db.String(18), unique=False, nullable=False)
    sensitive = db.Column(db.String(18), unique=False, nullable=False)
    created_time    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_time    = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'disease_code': self.disease_code,
            'data_code': self.data_code,
            'similar': self.similar,
            'sensitive': self.sensitive,
        }