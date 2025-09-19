import pandas as pd
from datetime import datetime
from modules.ins.models import db, ins3_record_data

# 1. 读取四个疾病数据表格（确保顺序一致，均为同一批患者）
df_chd = pd.read_csv(
    'revised_chd_data.csv',
    usecols=lambda col: col != '患者ID'
)
df_copd = pd.read_csv(
    'revised_copd_data.csv',
    usecols=lambda col: col != '患者ID'
)
df_diabetes = pd.read_csv(
    'revised_diabetes_data.csv',
    usecols=lambda col: col != '患者ID'
)
df_hypertension = pd.read_csv(
    'revised_hypertension_data.csv',
    usecols=lambda col: col != '患者ID'
)

# 2. 验证数据行数是否一致（确保都是5000行同一批患者）
if not (len(df_chd) == len(df_copd) == len(df_diabetes) == len(df_hypertension) == 5000):
    raise ValueError("四个数据集的行数不一致，请检查数据匹配性")

# 3. 批量处理每一行（每位患者）
batch_size = 100  # 批量提交大小，避免内存占用过高
records_count = 0

def get_data_item(i):
    chd_row = df_chd.iloc[i].to_dict()
    copd_row = df_copd.iloc[i].to_dict()
    diabetes_row = df_diabetes.iloc[i].to_dict()
    hypertension_row = df_hypertension.iloc[i].to_dict()

    # 4. 实例化患者记录（字段值优先级：取第一个非空值）
    data_record = ins3_record_data(
        # 病历号：假设四个表格中至少有一个包含"病历号"字段
        medical_record_num=chd_row.get('病历号') or copd_row.get('病历号') or
                           diabetes_row.get('病历号') or hypertension_row.get('病历号') or f"PATIENT_{i + 1}",

        # 基础健康信息
        smoking_history=chd_row.get('吸烟史', '') or copd_row.get('吸烟史', '') or diabetes_row.get('吸烟史',
                                                                                              '') or hypertension_row.get(
            '吸烟史', ''),
        drinking_history=chd_row.get('饮酒史', '') or copd_row.get('饮酒史', '') or diabetes_row.get('饮酒史',
                                                                                               '') or hypertension_row.get(
            '饮酒史', ''),
        hypertension_history=chd_row.get('高血压史', '') or copd_row.get('高血压史', '') or diabetes_row.get('高血压史',
                                                                                                     '') or hypertension_row.get(
            '高血压史', ''),
        blood_type=chd_row.get('血型', '') or copd_row.get('血型', '') or diabetes_row.get('血型',
                                                                                       '') or hypertension_row.get('血型',
                                                                                                                   ''),
        heart_rate=chd_row.get('心率', '') or copd_row.get('心率', '') or diabetes_row.get('心率',
                                                                                       '') or hypertension_row.get('心率',
                                                                                                                   ''),
        triglyceride=chd_row.get('甘油三酯', '') or copd_row.get('甘油三酯', '') or diabetes_row.get('甘油三酯',
                                                                                             '') or hypertension_row.get(
            '甘油三酯', ''),
        total_cholesterol=chd_row.get('总胆固醇', '') or copd_row.get('总胆固醇', '') or diabetes_row.get('总胆固醇',
                                                                                                  '') or hypertension_row.get(
            '总胆固醇', ''),
        hdl_cholesterol=chd_row.get('高密度脂蛋白胆固醇', '') or copd_row.get('高密度脂蛋白胆固醇', '') or diabetes_row.get('高密度脂蛋白胆固醇',
                                                                                                          '') or hypertension_row.get(
            '高密度脂蛋白胆固醇', ''),
        ldl_cholesterol=chd_row.get('低密度脂蛋白胆固醇', '') or copd_row.get('低密度脂蛋白胆固醇', '') or diabetes_row.get('低密度脂蛋白胆固醇',
                                                                                                          '') or hypertension_row.get(
            '低密度脂蛋白胆固醇', ''),
        left_ventricular_ejection_fraction=chd_row.get('左心室射血分数', '') or copd_row.get('左心室射血分数',
                                                                                      '') or diabetes_row.get('左心室射血分数',
                                                                                                              '') or hypertension_row.get(
            '左心室射血分数', ''),
        serum_creatinine=chd_row.get('血清肌酐', '') or copd_row.get('血清肌酐', '') or diabetes_row.get('血清肌酐',
                                                                                                 '') or hypertension_row.get(
            '血清肌酐', ''),
        troponin=chd_row.get('肌钙蛋白', '') or copd_row.get('肌钙蛋白', '') or diabetes_row.get('肌钙蛋白',
                                                                                         '') or hypertension_row.get(
            '肌钙蛋白', ''),

        # 诊断与治疗相关
        diagnosis_name_code=chd_row.get('诊断名称及代码', '') or copd_row.get('诊断名称及代码', '') or diabetes_row.get('诊断名称及代码',
                                                                                                          '') or hypertension_row.get(
            '诊断名称及代码', ''),
        planned_operation_code=chd_row.get('拟实施手术及操作编码', '') or copd_row.get('拟实施手术及操作编码', '') or diabetes_row.get(
            '拟实施手术及操作编码', '') or hypertension_row.get('拟实施手术及操作编码', ''),
        transfusion_method=chd_row.get('输血方式', '') or copd_row.get('输血方式', '') or diabetes_row.get('输血方式',
                                                                                                   '') or hypertension_row.get(
            '输血方式', ''),
        drug_name=chd_row.get('药物名称', '') or copd_row.get('药物名称', '') or diabetes_row.get('药物名称',
                                                                                          '') or hypertension_row.get(
            '药物名称', ''),
        medication_guidance=chd_row.get('用药指导', '') or copd_row.get('用药指导', '') or diabetes_row.get('用药指导',
                                                                                                    '') or hypertension_row.get(
            '用药指导', ''),
        lifestyle_guidance=chd_row.get('生活方式指导', '') or copd_row.get('生活方式指导', '') or diabetes_row.get('生活方式指导',
                                                                                                       '') or hypertension_row.get(
            '生活方式指导', ''),
        cost=chd_row.get('费用', '') or copd_row.get('费用', '') or diabetes_row.get('费用', '') or hypertension_row.get('费用',
                                                                                                                   ''),

        # 吸烟相关信息
        smoking_start_age=chd_row.get('开始吸烟年龄(岁)', '') or copd_row.get('开始吸烟年龄(岁)', '') or diabetes_row.get('开始吸烟年龄(岁)',
                                                                                                            '') or hypertension_row.get(
            '开始吸烟年龄(岁)', ''),
        smoking_quit_age=chd_row.get('戒烟年龄(岁)', '') or copd_row.get('戒烟年龄(岁)', '') or diabetes_row.get('戒烟年龄(岁)',
                                                                                                       '') or hypertension_row.get(
            '戒烟年龄(岁)', ''),
        occupational_dust_exposure=chd_row.get('职业性烟尘接触史', '') or copd_row.get('职业性烟尘接触史', '') or diabetes_row.get(
            '职业性烟尘接触史', '') or hypertension_row.get('职业性烟尘接触史', ''),
        environmental_risk_factors=chd_row.get('环境危险因素史', '') or copd_row.get('环境危险因素史', '') or diabetes_row.get(
            '环境危险因素史', '') or hypertension_row.get('环境危险因素史', ''),

        # 肺功能检查
        fev1=chd_row.get('肺功能检查-第一秒用力呼气容积(FEV1)', '') or copd_row.get('肺功能检查-第一秒用力呼气容积(FEV1)', '') or diabetes_row.get(
            '肺功能检查-第一秒用力呼气容积(FEV1)', '') or hypertension_row.get('肺功能检查-第一秒用力呼气容积(FEV1)', ''),
        fev1_fvc_ratio=chd_row.get('肺功能检查-第一秒用力呼气容积与用力肺活量百分比(FEV1/FVC)', '') or copd_row.get(
            '肺功能检查-第一秒用力呼气容积与用力肺活量百分比(FEV1/FVC)', '') or diabetes_row.get('肺功能检查-第一秒用力呼气容积与用力肺活量百分比(FEV1/FVC)',
                                                                          '') or hypertension_row.get(
            '肺功能检查-第一秒用力呼气容积与用力肺活量百分比(FEV1/FVC)', ''),
        tlc=chd_row.get('肺功能检查-总肺活量(TLC)', '') or copd_row.get('肺功能检查-总肺活量(TLC)', '') or diabetes_row.get(
            '肺功能检查-总肺活量(TLC)', '') or hypertension_row.get('肺功能检查-总肺活量(TLC)', ''),
        frc=chd_row.get('肺功能检查-功能参气量(FRC)', '') or copd_row.get('肺功能检查-功能参气量(FRC)', '') or diabetes_row.get(
            '肺功能检查-功能参气量(FRC)', '') or hypertension_row.get('肺功能检查-功能参气量(FRC)', ''),
        dlco=chd_row.get('肺功能检查-一氧化碳弥散量(DLCO)', '') or copd_row.get('肺功能检查-一氧化碳弥散量(DLCO)', '') or diabetes_row.get(
            '肺功能检查-一氧化碳弥散量(DLCO)', '') or hypertension_row.get('肺功能检查-一氧化碳弥散量(DLCO)', ''),
        dlco_va_ratio=chd_row.get('肺功能检查-一氧化碳弥散量(DLCO)与肺泡通气量(VA)比值(DLCO/VA)', '') or copd_row.get(
            '肺功能检查-一氧化碳弥散量(DLCO)与肺泡通气量(VA)比值(DLCO/VA)', '') or diabetes_row.get(
            '肺功能检查-一氧化碳弥散量(DLCO)与肺泡通气量(VA)比值(DLCO/VA)', '') or hypertension_row.get(
            '肺功能检查-一氧化碳弥散量(DLCO)与肺泡通气量(VA)比值(DLCO/VA)', ''),
        pef=chd_row.get('肺功能检查-峰流速(PEF)', '') or copd_row.get('肺功能检查-峰流速(PEF)', '') or diabetes_row.get(
            '肺功能检查-峰流速(PEF)', '') or hypertension_row.get('肺功能检查-峰流速(PEF)', ''),
        cat_score=chd_row.get('慢阻肺评估测试(CAT)', '') or copd_row.get('慢阻肺评估测试(CAT)', '') or diabetes_row.get(
            '慢阻肺评估测试(CAT)', '') or hypertension_row.get('慢阻肺评估测试(CAT)', ''),
        mmrc_score=chd_row.get('改良版英国医学研究委员会呼吸困难问卷(mMRC)评分', '') or copd_row.get('改良版英国医学研究委员会呼吸困难问卷(mMRC)评分',
                                                                                 '') or diabetes_row.get(
            '改良版英国医学研究委员会呼吸困难问卷(mMRC)评分', '') or hypertension_row.get('改良版英国医学研究委员会呼吸困难问卷(mMRC)评分', ''),
        spo2=chd_row.get('脉搏血氧饱和度（SpO2)', '') or copd_row.get('脉搏血氧饱和度（SpO2)', '') or diabetes_row.get('脉搏血氧饱和度（SpO2)',
                                                                                                       '') or hypertension_row.get(
            '脉搏血氧饱和度（SpO2)', ''),

        # 家族与用药史
        family_history=chd_row.get('家族史', '') or copd_row.get('家族史', '') or diabetes_row.get('家族史',
                                                                                             '') or hypertension_row.get(
            '家族史', ''),
        medication_history=chd_row.get('用药史', '') or copd_row.get('用药史', '') or diabetes_row.get('用药史',
                                                                                                 '') or hypertension_row.get(
            '用药史', ''),
        past_history=chd_row.get('既往史', '') or copd_row.get('既往史', '') or diabetes_row.get('既往史',
                                                                                           '') or hypertension_row.get(
            '既往史', ''),

        # 生活方式
        daily_staple_food=chd_row.get('日主食量(g)', '') or copd_row.get('日主食量(g)', '') or diabetes_row.get('日主食量(g)',
                                                                                                        '') or hypertension_row.get(
            '日主食量(g)', ''),
        exercise_method=chd_row.get('运动方式', '') or copd_row.get('运动方式', '') or diabetes_row.get('运动方式',
                                                                                                '') or hypertension_row.get(
            '运动方式', ''),
        exercise_duration=chd_row.get('运动时长', '') or copd_row.get('运动时长', '') or diabetes_row.get('运动时长',
                                                                                                  '') or hypertension_row.get(
            '运动时长', ''),

        # 血糖相关
        fasting_blood_glucose=chd_row.get('空腹血糖值(mmol/L)', '') or copd_row.get('空腹血糖值(mmol/L)', '') or diabetes_row.get(
            '空腹血糖值(mmol/L)', '') or hypertension_row.get('空腹血糖值(mmol/L)', ''),
        postprandial_blood_glucose=chd_row.get('餐后两小时血糖值(mmol/L)', '') or copd_row.get('餐后两小时血糖值(mmol/L)',
                                                                                       '') or diabetes_row.get(
            '餐后两小时血糖值(mmol/L)', '') or hypertension_row.get('餐后两小时血糖值(mmol/L)', ''),
        hypoglycemia_code=chd_row.get('低血糖反应代码', '') or copd_row.get('低血糖反应代码', '') or diabetes_row.get('低血糖反应代码',
                                                                                                        '') or hypertension_row.get(
            '低血糖反应代码', ''),
        hba1c=chd_row.get('糖化血红蛋白值(%)', '') or copd_row.get('糖化血红蛋白值(%)', '') or diabetes_row.get('糖化血红蛋白值(%)',
                                                                                                  '') or hypertension_row.get(
            '糖化血红蛋白值(%)', ''),
        insulin=chd_row.get('胰岛素', '') or copd_row.get('胰岛素', '') or diabetes_row.get('胰岛素',
                                                                                      '') or hypertension_row.get('胰岛素',
                                                                                                                  ''),
        c_peptide=chd_row.get('C肽', '') or copd_row.get('C肽', '') or diabetes_row.get('C肽', '') or hypertension_row.get(
            'C肽', ''),

        # 检查项目
        abdominal_ultrasound=chd_row.get('腹部彩超', '') or copd_row.get('腹部彩超', '') or diabetes_row.get('腹部彩超',
                                                                                                     '') or hypertension_row.get(
            '腹部彩超', ''),
        fundus_examination=chd_row.get('眼底检查', '') or copd_row.get('眼底检查', '') or diabetes_row.get('眼底检查',
                                                                                                   '') or hypertension_row.get(
            '眼底检查', ''),
        lower_limb_vascular_ultrasound=chd_row.get('下肢血管彩超', '') or copd_row.get('下肢血管彩超', '') or diabetes_row.get(
            '下肢血管彩超', '') or hypertension_row.get('下肢血管彩超', ''),
        urine_microalbumin_creatinine_ratio=chd_row.get('尿微量白蛋白/肌酐比值', '') or copd_row.get('尿微量白蛋白/肌酐比值',
                                                                                           '') or diabetes_row.get(
            '尿微量白蛋白/肌酐比值', '') or hypertension_row.get('尿微量白蛋白/肌酐比值', ''),
        arterial_stiffness=chd_row.get('动脉僵硬度', '') or copd_row.get('动脉僵硬度', '') or diabetes_row.get('动脉僵硬度',
                                                                                                     '') or hypertension_row.get(
            '动脉僵硬度', ''),

        # 血压相关
        bmi=chd_row.get('BMI指数', '') or copd_row.get('BMI指数', '') or diabetes_row.get('BMI指数',
                                                                                      '') or hypertension_row.get(
            'BMI指数', ''),
        waist_circumference=chd_row.get('腰围', '') or copd_row.get('腰围', '') or diabetes_row.get('腰围',
                                                                                                '') or hypertension_row.get(
            '腰围', ''),
        sitting_standing_blood_pressure=chd_row.get('坐位、立位血压', '') or copd_row.get('坐位、立位血压', '') or diabetes_row.get(
            '坐位、立位血压', '') or hypertension_row.get('坐位、立位血压', ''),
        ambulatory_blood_pressure_24h=chd_row.get('24h动态血压', '') or copd_row.get('24h动态血压', '') or diabetes_row.get(
            '24h动态血压', '') or hypertension_row.get('24h动态血压', ''),
        blood_uric_acid=chd_row.get('血尿酸', '') or copd_row.get('血尿酸', '') or diabetes_row.get('血尿酸',
                                                                                              '') or hypertension_row.get(
            '血尿酸', ''),

        created_time=datetime.utcnow(),
        updated_time=datetime.utcnow(),
    )
    return data_record