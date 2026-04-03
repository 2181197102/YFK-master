from modules.emergency.models import HealthRecord24h
from modules.auth.models import User
from datetime import datetime, date
import random

# ------------------- 24小时健康记录随机数据（10个用户） -------------------
# 格式：(user_username, 记录日期, 各时间点心率/收缩压/舒张压)
# 心率范围：60-100 bpm，收缩压：90-140 mmHg，舒张压：60-90 mmHg（含少量异常值）
HEALTH_RECORDS_TO_ADD = [
    # 用户patient_alice（ID对应之前的用户表）
    (
        "zenggang",
        '540105198103256789',
        # 0,2,4,6,8,10,12,14,16,18,20,22时的(hr, sys, dia)
[        (65, 110, 70), (62, 105, 68), (60, 100, 65), (63, 108, 66),
        (75, 115, 72), (80, 120, 75), (85, 125, 78), (105, 145, 92),  # 14时异常（心率高、血压高）
        (82, 122, 76), (78, 118, 73), (70, 112, 71), (68, 108, 69)]
    ),
    # 用户patient_bob
    (
        "chenxue",
        "450101199608108901",
[        (70, 115, 72), (68, 110, 70), (65, 105, 67), (66, 108, 68),
        (78, 120, 75), (82, 123, 76), (88, 128, 79), (85, 126, 77),
        (83, 124, 78), (80, 121, 75), (75, 116, 73), (72, 112, 71)]
    ),
    # 用户wumin
    (
        "sangming",
        '450107198109186789',
[        (68, 120, 75), (66, 115, 73), (64, 110, 70), (65, 112, 71),
        (76, 125, 78), (80, 128, 80), (83, 130, 81), (81, 127, 79),
        (79, 126, 78), (77, 123, 76), (72, 118, 74), (70, 116, 72)]
    ),
    # 用户admin
    (
        "wuhao",
        '510101198411128901',
[        (72, 118, 74), (70, 113, 72), (68, 109, 69), (69, 111, 70),
        (80, 122, 76), (84, 125, 77), (86, 127, 79), (84, 125, 78),
        (82, 123, 77), (79, 120, 75), (75, 115, 73), (73, 112, 71)]
    ),
]

def insert_data(db):
    """插入随机健康记录和异常告警数据"""
    print("  - 正在插入24小时健康记录和异常告警数据…")

    # 插入健康记录
    for username, id_card, time_points in HEALTH_RECORDS_TO_ADD:

        # 检查是否已存在该日期的记录
        existing = db.session.query(HealthRecord24h).filter_by(
            id_card=id_card
        ).first()
        if existing:
            print(f"    用户 '{username}' {id_card} 的健康记录已存在，跳过。")
            continue
        # 构造记录数据（按时间点赋值）
        hour_list = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
        record_data = {
            "user_name": username,
            "id_card": id_card,
            "created_time": datetime.utcnow(),
            "updated_time": datetime.utcnow()
        }

        for i, hour in enumerate(hour_list):
            hr, sys, dia = time_points[i]
            # 生成血氧饱和度值（符合实际范围）
            if random.random() < 0.1:  # 10%概率设为0（空值）
                spo2 = 0
                hr=0
                sys=0
                dia=0
            else:
                if random.random() < 0.05:  # 5%概率偏低（异常值：90-94%）
                    spo2 = random.randint(90, 94)
                else:  # 85%概率正常范围（95-100%）
                    spo2 = random.randint(95, 100)

            record_data[f"hr_{hour}"] = hr
            record_data[f"sys_{hour}"] = sys
            record_data[f"dia_{hour}"] = dia
            record_data[f"spo2_{hour}"] = spo2

        # 创建并插入记录
        record = HealthRecord24h(**record_data)
        db.session.add(record)
        db.session.flush()  # 刷新获取record.id，用于关联告警
        print(f"    已添加用户 '{username}' 的健康记录（ID：{record.id}）")

    db.session.commit()
    print("  - 健康记录和异常告警数据插入完成！")