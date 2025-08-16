# initial_data/15_disease_data_item.py

from modules.data_management.models import DiseaseDataItem, ICD10Code
from datetime import datetime
import json

def insert_data(db):
    """
    插入模拟的病种-数据项字段数据。
    """
    print("  - 正在插入初始数据 (DiseaseDataItem)...")

    # 定义病种和对应的数据项
    disease_data_items = [
        {
            "disease_code": "A00.0",
            "disease_name": "霍乱弧菌所致的霍乱",
            "description": "由霍乱弧菌引起的急性肠道传染病，主要症状为严重腹泻和脱水",
            "associated_fields": [
                "患者基本信息", "发病时间", "临床症状", "腹泻次数", "呕吐情况",
                "脱水程度", "体温", "血压", "心率", "大便性状", "大便培养结果",
                "血清学检查", "电解质检查", "肾功能检查", "治疗方案", "用药记录",
                "输液记录", "隔离措施", "接触史", "流行病学调查"
            ]
        },
        {
            "disease_code": "B15.9",
            "disease_name": "甲型病毒性肝炎",
            "description": "由甲型肝炎病毒感染引起的急性肝脏炎症",
            "associated_fields": [
                "患者基本信息", "发病时间", "临床症状", "黄疸程度", "肝脏触诊",
                "脾脏触诊", "肝功能检查", "胆红素水平", "转氨酶水平", "凝血功能",
                "甲肝抗体检测", "甲肝病毒RNA", "腹部超声", "治疗方案", "护肝药物",
                "饮食指导", "休息建议", "复查计划", "接触史", "疫苗接种史"
            ]
        },
        {
            "disease_code": "I10",
            "disease_name": "原发性高血压",
            "description": "以动脉血压持续升高为主要表现的慢性疾病",
            "associated_fields": [
                "患者基本信息", "血压测量记录", "收缩压", "舒张压", "心率",
                "体重指数", "腰围", "家族史", "吸烟史", "饮酒史", "运动习惯",
                "心电图", "心脏超声", "眼底检查", "肾功能检查", "血脂检查",
                "血糖检查", "尿常规", "降压药物", "用药依从性", "生活方式指导",
                "随访计划", "并发症评估"
            ]
        },
        {
            "disease_code": "E11.9",
            "disease_name": "2型糖尿病",
            "description": "以慢性高血糖为特征的代谢性疾病",
            "associated_fields": [
                "患者基本信息", "血糖监测记录", "空腹血糖", "餐后血糖", "糖化血红蛋白",
                "体重指数", "腰臀比", "血压", "家族史", "饮食习惯", "运动情况",
                "胰岛素分泌功能", "胰岛素抵抗指数", "血脂检查", "肾功能检查",
                "眼底检查", "神经系统检查", "足部检查", "降糖药物", "胰岛素治疗",
                "血糖仪使用", "饮食指导", "运动处方", "并发症筛查", "随访记录"
            ]
        },
        {
            "disease_code": "J44.1",
            "disease_name": "慢性阻塞性肺疾病急性加重期",
            "description": "慢性阻塞性肺疾病的急性恶化阶段",
            "associated_fields": [
                "患者基本信息", "症状评估", "呼吸困难程度", "咳嗽情况", "咳痰性状",
                "吸烟史", "职业暴露史", "肺功能检查", "动脉血气分析", "胸部X线",
                "胸部CT", "血常规", "C反应蛋白", "降钙素原", "痰培养", "支气管扩张剂",
                "糖皮质激素", "抗生素", "氧疗", "无创通气", "康复训练", "戒烟指导",
                "疫苗接种", "随访计划"
            ]
        },
        {
            "disease_code": "N18.9",
            "disease_name": "慢性肾脏病",
            "description": "肾脏结构或功能异常持续3个月以上",
            "associated_fields": [
                "患者基本信息", "病程记录", "原发病因", "血压监测", "水肿评估",
                "肾功能检查", "血肌酐", "尿素氮", "肾小球滤过率", "尿常规",
                "24小时尿蛋白", "电解质检查", "血红蛋白", "甲状旁腺激素", "骨代谢指标",
                "肾脏超声", "肾脏病理", "血管通路评估", "透析准备", "药物调整",
                "饮食指导", "并发症预防", "透析教育", "移植评估", "随访计划"
            ]
        },
        {
            "disease_code": "K59.0",
            "disease_name": "便秘",
            "description": "排便困难或排便次数减少的症状",
            "associated_fields": [
                "患者基本信息", "症状描述", "排便频率", "大便性状", "排便困难程度",
                "腹胀情况", "腹痛情况", "饮食习惯", "运动情况", "用药史",
                "既往病史", "腹部检查", "直肠指检", "腹部X线", "结肠镜检查",
                "肛门直肠压力测定", "结肠传输试验", "饮食调整", "纤维素补充",
                "泻药使用", "益生菌", "生活方式指导", "随访计划"
            ]
        },
        {
            "disease_code": "M79.3",
            "disease_name": "脂膜炎",
            "description": "皮下脂肪组织的炎症性疾病",
            "associated_fields": [
                "患者基本信息", "皮损描述", "皮损分布", "疼痛程度", "局部温度",
                "皮肤颜色变化", "皮损大小", "触痛情况", "全身症状", "发热情况",
                "既往病史", "用药史", "皮肤活检", "病理检查", "血常规",
                "炎症指标", "自身抗体", "影像学检查", "抗炎治疗", "免疫抑制剂",
                "局部治疗", "物理治疗", "随访观察", "复发预防"
            ]
        }
    ]

    item_id_counter = 1

    for item_data in disease_data_items:
        # 检查对应的ICD-10编码是否存在
        icd_code = db.session.query(ICD10Code).filter_by(code=item_data["disease_code"]).first()
        if not icd_code:
            print(f"    警告: 未找到ICD-10编码 {item_data['disease_code']}，跳过对应的病种数据项。")
            continue
        
        # 检查是否已存在相同的病种数据项
        existing_item = db.session.query(DiseaseDataItem).filter_by(
            disease_code=item_data["disease_code"]
        ).first()
        
        if not existing_item:
            item_id = f"disease_{item_id_counter:03d}"
            
            new_item = DiseaseDataItem(
                id=item_id,
                disease_code=item_data["disease_code"],
                disease_name=item_data["disease_name"],
                description=item_data["description"],
                associated_fields=json.dumps(item_data["associated_fields"], ensure_ascii=False),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            
            db.session.add(new_item)
            print(f"    已添加病种数据项: {item_data['disease_code']} - {item_data['disease_name']}")
            print(f"      关联数据项数量: {len(item_data['associated_fields'])}")
            
        else:
            print(f"    病种数据项 {item_data['disease_code']} 已存在，跳过。")
            
        item_id_counter += 1

    print("  - DiseaseDataItem 数据插入完成。")
    # 事务提交由 db_test_and_init.py 处理
