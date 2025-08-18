# initial_data/17_static_sensitivity_levels.py

from modules.data_items.models import StaticSensitivityLevel
from datetime import datetime

def insert_data(db):
    """
    插入静态敏感等级初始数据
    """
    print("  - 正在插入初始数据 (StaticSensitivityLevel)...")

    # 定义不同敏感等级的数据项
    sensitivity_levels = [
        # 准标识符 (Level 1)
        {
            "data_name": "年龄",
            "description": "患者年龄信息，属于准标识符，结合其他信息可能识别个人身份",
            "sensitivity_level": 1
        },
        {
            "data_name": "性别",
            "description": "患者性别信息，属于准标识符，单独无法识别个人但可缩小范围",
            "sensitivity_level": 1
        },
        {
            "data_name": "职业",
            "description": "患者职业信息，属于准标识符，可能用于身份推断",
            "sensitivity_level": 1
        },
        {
            "data_name": "地区编码",
            "description": "患者所在地区的编码信息，属于准标识符",
            "sensitivity_level": 1
        },
        
        # 显示标识符 (Level 2)
        {
            "data_name": "身份证号",
            "description": "患者身份证号码，属于显示标识符，直接标识个人身份",
            "sensitivity_level": 2
        },
        {
            "data_name": "姓名",
            "description": "患者真实姓名，属于显示标识符，直接标识个人身份",
            "sensitivity_level": 2
        },
        {
            "data_name": "手机号码",
            "description": "患者手机号码，属于显示标识符，可直接联系到个人",
            "sensitivity_level": 2
        },
        {
            "data_name": "家庭地址",
            "description": "患者详细家庭地址，属于显示标识符，可直接定位到个人",
            "sensitivity_level": 2
        },
        {
            "data_name": "邮箱地址",
            "description": "患者邮箱地址，属于显示标识符，可直接联系到个人",
            "sensitivity_level": 2
        },
        
        # 低敏感数据 (Level 3)
        {
            "data_name": "血型",
            "description": "患者血型信息，属于低敏感数据，医疗必需但敏感度较低",
            "sensitivity_level": 3
        },
        {
            "data_name": "身高体重",
            "description": "患者身高体重等基本体征，属于低敏感数据",
            "sensitivity_level": 3
        },
        {
            "data_name": "血压心率",
            "description": "患者血压心率等生命体征，属于低敏感数据",
            "sensitivity_level": 3
        },
        {
            "data_name": "常规检验结果",
            "description": "血常规、尿常规等基础检验结果，属于低敏感数据",
            "sensitivity_level": 3
        },
        {
            "data_name": "影像学检查",
            "description": "X光、CT等影像学检查结果，属于低敏感数据",
            "sensitivity_level": 3
        },
        
        # 高敏感数据 (Level 4)
        {
            "data_name": "精神疾病诊断",
            "description": "精神疾病相关诊断信息，属于高敏感数据，涉及患者隐私和社会偏见",
            "sensitivity_level": 4
        },
        {
            "data_name": "性病检查结果",
            "description": "性传播疾病检查结果，属于高敏感数据，涉及患者隐私",
            "sensitivity_level": 4
        },
        {
            "data_name": "HIV检测结果",
            "description": "HIV病毒检测结果，属于高敏感数据，涉及严重社会歧视风险",
            "sensitivity_level": 4
        },
        {
            "data_name": "遗传疾病信息",
            "description": "遗传性疾病相关信息，属于高敏感数据，可能影响家族成员",
            "sensitivity_level": 4
        },
        {
            "data_name": "药物滥用史",
            "description": "药物滥用或成瘾相关病史，属于高敏感数据，涉及法律和社会问题",
            "sensitivity_level": 4
        },
        {
            "data_name": "妊娠终止记录",
            "description": "人工流产等妊娠终止记录，属于高敏感数据，涉及个人隐私",
            "sensitivity_level": 4
        },
        {
            "data_name": "家族病史",
            "description": "患者家族遗传病史信息，属于高敏感数据，可能影响多人隐私",
            "sensitivity_level": 4
        },
        {
            "data_name": "基因检测结果",
            "description": "基因检测和分析结果，属于高敏感数据，涉及遗传隐私",
            "sensitivity_level": 4
        }
    ]

    level_id_counter = 1

    for level_data in sensitivity_levels:
        # 检查是否已存在相同的敏感等级记录
        existing_level = db.session.query(StaticSensitivityLevel).filter_by(
            data_name=level_data["data_name"]
        ).first()
        
        if not existing_level:
            level_id = f"ssl_{level_id_counter:03d}"
            
            new_level = StaticSensitivityLevel(
                id=level_id,
                data_name=level_data["data_name"],
                description=level_data["description"],
                sensitivity_level=level_data["sensitivity_level"],
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            
            db.session.add(new_level)
            print(f"    已添加敏感等级: Level {level_data['sensitivity_level']} - {level_data['data_name']}")
            
        else:
            print(f"    敏感等级记录 {level_data['data_name']} 已存在，跳过。")
            
        level_id_counter += 1

    print("  - StaticSensitivityLevel 数据插入完成。")
    # 事务提交由 db_test_and_init.py 处理
