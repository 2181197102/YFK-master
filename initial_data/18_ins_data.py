# initial_data/02_users.py
from modules.ins.models import *
from datetime import datetime
import random
import pandas as pd
import numpy as np
import os
import zipfile

def clean_value(value):
    """将NaN、None转换为空字符串，处理其他数据类型"""
    if pd.isna(value) or value is None:
        return ''
    # 处理布尔值（如True/False转换为字符串）
    if isinstance(value, bool):
        return '是' if value else '否'
    # 处理数值类型（避免科学计数法）
    if isinstance(value, (int, float)):
        # 整数转换为字符串，避免出现.0
        return str(value)
    # 其他类型直接转换为字符串
    return str(value).strip()

def get_data_item(ins_record_data, i,medical_record_num):
    chd_row = {k: clean_value(v) for k, v in df_chd.iloc[i].to_dict().items()}
    copd_row = {k: clean_value(v) for k, v in df_copd.iloc[i].to_dict().items()}
    diabetes_row = {k: clean_value(v) for k, v in df_diabetes.iloc[i].to_dict().items()}
    hypertension_row = {k: clean_value(v) for k, v in df_hypertension.iloc[i].to_dict().items()}

    # 4. 实例化患者记录（字段值优先级：取第一个非空值）
    data_record = ins_record_data(
        # 病历号：假设四个表格中至少有一个包含"病历号"字段
        medical_record_num=medical_record_num,

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

doctor1 = [["张伟", "DR-2023001"],
["李娜", "DR-2023002"],
["王芳", "DR-2023003"],
["刘伟", "DR-2023004"],
["陈明", "DR-2023005"],
["杨丽", "DR-2023006"],
["赵静", "DR-2023007"],
["孙颖", "DR-2023008"],
["周强", "DR-2023009"],
["吴敏", "DR-2023010"]]

doctor2 = [["郑华", "DR-2023011"],
["钱磊", "DR-2023012"],
["冯佳", "DR-2023013"],
["陈杰", "DR-2023014"],
["杨琳", "DR-2023015"],
["黄浩", "DR-2023016"],
["朱燕", "DR-2023017"],
["胡军", "DR-2023018"],
["马丽", "DR-2023019"],
["郭明", "DR-2023020"]]

doctor3 = [["林颖", "DR-2023021"],
["高伟", "DR-2023022"],
["罗静", "DR-2023023"],
["梁刚", "DR-2023024"],
["谢芳", "DR-2023025"],
["宋磊", "DR-2023026"],
["唐敏", "DR-2023027"],
["许强", "DR-2023028"],
["邓娜", "DR-2023029"],
["韩华", "DR-2023030"]]

patientlist=[["张明", "男", "110101199001011234", 34],
["李娜", "女", "120101199502156789", 29],
["王强", "男", "130101198503202345", 39],
["刘芳", "女", "140101200004105678", 24],
["赵伟", "男", "150101197805058901", 46],
["孙静", "女", "210101199206182345", 32],
["周杰", "男", "220101198807226789", 36],
["吴敏", "女", "230101199908308901", 25],
["郑华", "男", "310101198309152345", 41],
["钱丽", "女", "320101199310056789", 31],
["孙军", "男", "330101198011128901", 44],
["何颖", "女", "340101199712202345", 27],
["马涛", "男", "350101198601056789", 38],
["朱琳", "女", "360101199102188901", 33],
["胡鹏", "男", "370101197903252345", 45],
["林燕", "女", "410101199404106789", 30],
["高洋", "男", "420101198705158901", 37],
["罗婷", "女", "430101199806222345", 26],
["黄刚", "男", "440101198207306789", 42],
["陈雪", "女", "450101199608108901", 28],
["杨明", "男", "460101198109182345", 43],
["郭佳", "女", "500101199910056789", 25],
["吴浩", "男", "510101198411128901", 40],
["徐静", "女", "520101199212202345", 32],
["孙磊", "男", "530101197701056789", 47],
["宋佳", "女", "540101199502188901", 29],
["韩斌", "男", "610101198903252345", 35],
["曹颖", "女", "620101199304106789", 31],
["冯伟", "男", "630101198505158901", 39],
["田甜", "女", "640101199706222345", 27],
["董强", "男", "650101198307306789", 41],
["袁琳", "女", "110102199108108901", 33],
["潘军", "男", "120102198009182345", 44],
["于娜", "女", "130102199410056789", 30],
["蒋峰", "男", "140102198611128901", 38],
["蔡琴", "女", "150102199812202345", 26],
["丁浩", "男", "210102198701056789", 37],
["魏芳", "女", "220102199202188901", 32],
["薛刚", "男", "230102198103252345", 43],
["叶静", "女", "310102199604108901", 28],
["程伟", "男", "320102198405152345", 40],
["戴丽", "女", "330102199306226789", 31],
["陆鹏", "男", "340102197907308901", 45],
["苏燕", "女", "350102199508102345", 29],
["吕明", "男", "360102198809186789", 36],
["任娜", "女", "370102200010058901", 24],
["姜浩", "男", "410102198211122345", 42],
["范静", "女", "420102199712206789", 27],
["方强", "男", "430102198501058901", 39],
["石琳", "女", "440102199102182345", 33],
["姚军", "男", "450102197803256789", 46],
["谭佳", "女", "460102199404108901", 30],
["廖洋", "男", "500102198605152345", 38],
["邹颖", "女", "510102199806226789", 26],
["熊刚", "男", "520102198307308901", 41],
["金雪", "女", "530102199208102345", 32],
["陆明", "男", "540102198109186789", 43],
["郝佳", "女", "610102199910058901", 25],
["孔浩", "男", "620102198411122345", 40],
["白静", "女", "630102199312206789", 31],
["崔磊", "男", "650102197701058901", 47],
["康佳", "女", "110103199502182345", 29],
["毛斌", "男", "120103198903256789", 35],
["邱颖", "女", "130103199304108901", 31],
["秦伟", "男", "140103198505152345", 39],
["江甜", "女", "150103199706226789", 27],
["史强", "男", "210103198307308901", 41],
["顾琳", "女", "220103199108102345", 33],
["侯军", "男", "230103198009186789", 44],
["邵娜", "女", "310103199410058901", 30],
["孟峰", "男", "320103198611122345", 38],
["龙琴", "女", "330103199812206789", 26],
["万浩", "男", "340103198701058901", 37],
["段芳", "女", "350103199202182345", 32],
["钱刚", "男", "360103198103256789", 43],
["汤静", "女", "370103199604108901", 28],
["尹伟", "男", "410103198405152345", 40],
["黎丽", "女", "420103199306226789", 31],
["易鹏", "男", "430103197907308901", 45],
["常燕", "女", "440103199508102345", 29],
["武明", "男", "450103198809186789", 36],
["乔娜", "女", "460103200010058901", 24],
["贺浩", "男", "500103198211122345", 42],
["赖静", "女", "510103199712206789", 27],
["龚强", "男", "520103198501058901", 39],
["文琳", "女", "530103199102182345", 33],
["严军", "男", "540103197803256789", 46],
["牛佳", "女", "610103199404108901", 30],
["温洋", "男", "620103198605152345", 38],
["芦颖", "女", "630103199806226789", 26],
["季刚", "男", "650103198307308901", 41],
["殷雪", "女", "110104199208102345", 32],
["施明", "男", "120104198109186789", 43],
["欧佳", "女", "130104199910058901", 25],
["耿浩", "男", "140104198411122345", 40],
["关静", "女", "150104199312206789", 31],
["兰磊", "男", "210104197701058901", 47],
["焦佳", "女", "220104199502182345", 29],
["岳斌", "男", "230104198903256789", 35],
["祝颖", "女", "310104199304108901", 31],
["屈伟", "男", "320104198505152345", 39],
["鲍甜", "女", "330104199706226789", 27],
["肖强", "男", "340104198307308901", 41],
["柳琳", "女", "350104199108102345", 33],
["史军", "男", "360104198009186789", 44],
["岳娜", "女", "370104199410058901", 30],
["齐峰", "男", "410104198611122345", 38],
["秦琴", "女", "420104199812206789", 26],
["左浩", "男", "430104198701058901", 37],
["石芳", "女", "440104199202182345", 32],
["谭刚", "男", "450104198103256789", 43],
["贾静", "女", "460104199604108901", 28],
["阎伟", "男", "500104198405152345", 40],
["樊丽", "女", "510104199306226789", 31],
["胡鹏", "男", "520104197907308901", 45],
["凌燕", "女", "530104199508102345", 29],
["霍明", "男", "540104198809186789", 36],
["虞娜", "女", "610104200010058901", 24],
["万浩", "男", "620104198211122345", 42],
["支静", "女", "630104199712206789", 27],
["柯强", "男", "650104198501058901", 39],
["昝琳", "女", "110105199102182345", 33],
["管军", "男", "120105197803256789", 46],
["卢佳", "女", "130105199404108901", 30],
["莫洋", "男", "140105198605152345", 38],
["经颖", "女", "150105199806226789", 26],
["房刚", "男", "210105198307308901", 41],
["裘雪", "女", "220105199208102345", 32],
["缪明", "男", "230105198109186789", 43],
["干佳", "女", "310105199910058901", 25],
["解浩", "男", "320105198411122345", 40],
["应静", "女", "330105199312206789", 31],
["宗磊", "男", "340105197701058901", 47],
["丁佳", "女", "350105199502182345", 29],
["单斌", "男", "360105198903256789", 35],
["杭颖", "女", "370105199304108901", 31],
["裴伟", "男", "410105198505152345", 39],
["席甜", "女", "420105199706226789", 27],
["卫强", "男", "430105198307308901", 41],
["查琳", "女", "440105199108102345", 33],
["屈军", "男", "450105198009186789", 44],
["鲍娜", "女", "460105199410058901", 30],
["史峰", "男", "500105198611122345", 38],
["翟琴", "女", "510105199812206789", 26],
["覃浩", "男", "520105198701058901", 37],
["饶芳", "女", "530105199202182345", 32],
["曾刚", "男", "540105198103256789", 43],
["沙静", "女", "610105199604108901", 28],
["关伟", "男", "620105198405152345", 40],
["项丽", "女", "630105199306226789", 31],
["苏鹏", "男", "650105197907308901", 45],
["顾燕", "女", "110106199508102345", 29],
["常明", "男", "120106198809186789", 36],
["文娜", "女", "130106200010058901", 24],
["颜浩", "男", "140106198211122345", 42],
["倪静", "女", "150106199712206789", 27],
["严强", "男", "210106198501058901", 39],
["牛琳", "女", "220106199102182345", 33],
["温军", "男", "230106197803256789", 46],
["芦佳", "女", "310106199404108901", 30],
["季洋", "男", "320106198605152345", 38],
["俞颖", "女", "330106199806226789", 26],
["章刚", "男", "340106198307308901", 41],
["鲁雪", "女", "350106199208102345", 32],
["葛明", "男", "360106198109186789", 43],
["伍佳", "女", "370106199910058901", 25],
["韦浩", "男", "410106198411122345", 40],
["申静", "女", "420106199312206789", 31],
["欧阳磊", "男", "430106197701058901", 47],
["司马佳", "女", "440106199502182345", 29],
["上官斌", "男", "450106198903256789", 35],
["端木颖", "女", "460106199304108901", 31],
["呼延伟", "男", "500106198505152345", 39],
["东方甜", "女", "510106199706226789", 27],
["尉迟强", "男", "520106198307308901", 41],
["皇甫琳", "女", "530106199108102345", 33],
["公冶军", "男", "540106198009186789", 44],
["长孙娜", "女", "610106199410058901", 30],
["慕容峰", "男", "620106198611122345", 38],
["司徒琴", "女", "630106199812206789", 26],
["司空浩", "男", "650106198701058901", 37],
["佟芳", "女", "110107199202182345", 32],
["应刚", "男", "120107198103256789", 43],
["臧静", "女", "130107199604108901", 28],
["闵伟", "男", "140107198405152345", 40],
["邬丽", "女", "150107199306226789", 31],
["边鹏", "男", "210107197907308901", 45],
["卞燕", "女", "220107199508102345", 29],
["姬明", "男", "230107198809186789", 36],
["师娜", "女", "310107200010058901", 24],
["和浩", "男", "320107198211122345", 42],
["仇静", "女", "330107199712206789", 27],
["栾强", "男", "340107198501058901", 39],
["隋琳", "女", "350107199102182345", 33],
["商军", "男", "360107197803256789", 46],
["刁佳", "女", "370107199404108901", 30],
["沙洋", "男", "410107198605152345", 38],
["荣颖", "女", "420107199806226789", 26],
["巫刚", "男", "430107198307308901", 41],
["寇雪", "女", "440107199208102345", 32],
["桑明", "男", "450107198109186789", 43],
["郎佳", "女", "460107199910058901", 25],
["甄浩", "男", "500107198411122345", 40],
["丛静", "女", "510107199312206789", 31],
["仲磊", "男", "520107197701058901", 47],
["虞佳", "女", "530107199502182345", 29],
["封斌", "男", "540107198903256789", 35],
["芮颖", "女", "610107199304108901", 31]]

MEDICAL_RECORD_EXAMPLES = [
    "I10", "I25.1", "E10", "J44"
]

# columns_to_select =['HYP_HX',
#                         'CRP',
#                         'BIO_FBG',
#                         'BIO_PBG',
#                         'SHS_EXP',
#                         'HR',
#                         'BP',
#                         'BG',
#                         'BL_LIPID',
#                         'EXE_FREQ_WK',
#                         'INS_DOS_PER',
#                         'O2_DUR',
#                         'DRUNK_MARK',
#                         'STAP_INTAKE_D',
#                         'SMK_START_AGE',
#                         'SMK_QUIT_AGE',
#                         'PFT_TLC',
#                         'PFT_FRC',
#                         'PFT_DLCO'
#                         ]
#
# MEDICAL_RECORD_EXAMPLES = [
#     "I10", "I25.1", "E10", "J44"
# ]
# data_list = read_xlsx_file(excel_path, columns_to_select)

idxlist = [1,1,1]
df_chd = pd.read_csv(
    'initial_data/data/revised_chd_data.csv',  # 替换为你的文件路径
    usecols=lambda col: col != '患者ID'  # 排除名为"序号"的第一列
)
# chd_record = df_chd.to_dict('records')

df_copd = pd.read_csv(
    'initial_data/data/revised_copd_data.csv',  # 替换为你的文件路径
    usecols=lambda col: col != '患者ID'  # 排除名为"序号"的第一列
)
# copd_record = df_copd.to_dict('records')

df_diabetes = pd.read_csv(
    'initial_data/data/revised_diabetes_data.csv',  # 替换为你的文件路径
    usecols=lambda col: col != '患者ID'  # 排除名为"序号"的第一列
)
# diabetes_record = df_diabetes.to_dict('records')

df_hypertension = pd.read_csv(
    'initial_data/data/revised_hypertension_data.csv',  # 替换为你的文件路径
    usecols=lambda col: col != '患者ID'  # 排除名为"序号"的第一列
)
# hypertension_record = df_hypertension.to_dict('records')
print(1)
def insert_data(db):
    for id in range(5000):
        patient = random.choice(patientlist)
        i = random.randint(1, 3)
        if i == 1:
            idx = idxlist[i-1]
            idxlist[i-1] = idxlist[i-1] + 1
            ins_record = ins1_record
            ins_record_disease = ins1_record_disease
            ins_record_data = ins1_record_data
            ins_doctor_record = ins1_doctor_record
            doctor = random.choice(doctor1)

        if i ==2:
            idx = idxlist[i-1]
            idxlist[i-1] = idxlist[i-1] + 1
            ins_record = ins2_record
            ins_record_disease = ins2_record_disease
            ins_record_data = ins2_record_data
            ins_doctor_record = ins2_doctor_record
            doctor = random.choice(doctor2)

        if i ==3:
            idx = idxlist[i-1]
            idxlist[i-1] = idxlist[i-1] + 1
            ins_record = ins3_record
            ins_record_disease = ins3_record_disease
            ins_record_data = ins3_record_data
            ins_doctor_record = ins3_doctor_record
            doctor = random.choice(doctor3)


        existing = db.session.query(ins_record).filter_by(id=idx).first()
        if existing:
            print(f"    病历 '{idx}' 已存在，跳过。")
            continue

        record = ins_record(
            name=patient[0],
            age=patient[3],
            gender=patient[1],
            id_card=patient[2],
            doctor_code=doctor[1],
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(record)
        medical_record_num = idx

        random_disease_code = random.choice(MEDICAL_RECORD_EXAMPLES)
        disease_record = ins_record_disease(
            medical_record_num=medical_record_num,
            disease_code=random_disease_code,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(disease_record)
        data_record = get_data_item(ins_record_data, id, medical_record_num)
        db.session.add(data_record)

        doctor_record = ins_doctor_record(
            doctor_name=doctor[0],
            doctor_code=doctor[1],
            patient_name=record.name,
            patient_id_num=record.id_card,
            medical_record_num=medical_record_num,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(doctor_record)
