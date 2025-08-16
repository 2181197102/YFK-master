# initial_data/13_user_logs.py

from modules.data_management.models import UserLogs
from modules.auth.models import User
from datetime import datetime, timedelta
import json
import random

def insert_data(db):
    """
    插入模拟的用户访问日志数据。
    """
    print("  - 正在插入初始数据 (UserLogs)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联的用户。跳过 UserLogs 数据插入。")
        return

    # 定义常用的疾病编码
    common_disease_codes = [
        ["A00.0", "A00.1"],  # 霍乱
        ["B15.9", "B16.9"],  # 病毒性肝炎
        ["I10", "I11.9"],    # 高血压
        ["E11.9", "E10.9"],  # 糖尿病
        ["J44.1", "J44.0"],  # 慢性阻塞性肺病
        ["N18.9", "N18.6"],  # 慢性肾病
        ["K59.0", "K59.1"],  # 便秘
        ["M79.3", "M79.1"]   # 肌肉骨骼疾病
    ]

    # 定义IP地址池
    ip_pools = {
        "normal": ["192.168.1.100", "192.168.1.101", "192.168.1.102"],
        "hospital": ["10.0.1.50", "10.0.1.51", "10.0.1.52"],
        "remote": ["203.0.113.10", "203.0.113.11", "198.51.100.5"]
    }

    # 为每个用户生成访问日志
    users_data = [
        {
            "user": admin_user,
            "log_count": 20,
            "operations": ["VIEW", "ADD", "REVISE", "DELETE"],
            "sensitivities": ["LOW_SENSITIVITY", "HIGH_SENSITIVITY", "EXPLICIT_IDENTIFIER"],
            "ips": ip_pools["normal"] + ip_pools["hospital"]
        },
        {
            "user": patient_alice,
            "log_count": 10,
            "operations": ["VIEW"],
            "sensitivities": ["LOW_SENSITIVITY", "QUASI_IDENTIFIER"],
            "ips": ip_pools["normal"]
        },
        {
            "user": dr_smith,
            "log_count": 25,
            "operations": ["VIEW", "ADD", "REVISE", "COPY"],
            "sensitivities": ["LOW_SENSITIVITY", "HIGH_SENSITIVITY", "EXPLICIT_IDENTIFIER"],
            "ips": ip_pools["hospital"]
        },
        {
            "user": researcher_eve,
            "log_count": 30,
            "operations": ["VIEW", "COPY", "DOWNLOAD"],
            "sensitivities": ["QUASI_IDENTIFIER", "LOW_SENSITIVITY", "HIGH_SENSITIVITY"],
            "ips": ip_pools["remote"] + ip_pools["hospital"]
        }
    ]

    log_id_counter = 1
    
    for user_data in users_data:
        user = user_data["user"]
        if not user:
            continue
            
        print(f"    为用户 {user.username} ({user.id_card}) 生成 {user_data['log_count']} 条访问日志...")
        
        for i in range(user_data["log_count"]):
            # 生成时间戳（过去30天内的随机时间）
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            access_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # 随机选择操作类型和敏感度
            operation = random.choice(user_data["operations"])
            sensitivity = random.choice(user_data["sensitivities"])
            ip_address = random.choice(user_data["ips"])
            disease_codes = random.choice(common_disease_codes)
            
            # 根据用户类型和操作类型确定访问状态
            if user.username == "patient_alice" and operation == "VIEW":
                status = "SUCCESS"  # 患者查看自己的数据通常成功
            elif user.username == "researcher_eve" and sensitivity == "HIGH_SENSITIVITY":
                status = random.choices(["SUCCESS", "DENIED"], weights=[0.7, 0.3])[0]  # 科研人员访问高敏感数据可能被拒绝
            else:
                status = random.choices(["SUCCESS", "FAILURE"], weights=[0.9, 0.1])[0]  # 大部分访问成功
            
            # 检查是否已存在相同的日志
            log_id = f"log_{user.id_card}_{log_id_counter:03d}"
            existing_log = db.session.query(UserLogs).filter_by(id=log_id).first()
            
            if not existing_log:
                new_log = UserLogs(
                    id=log_id,
                    id_num=user.id_card,
                    access_timestamp=access_time,
                    access_ip=ip_address,
                    operation_type=operation,
                    target_data_sensitivity=sensitivity,
                    target_disease_codes=json.dumps(disease_codes),
                    access_status=status,
                    created_time=datetime.utcnow()
                )
                db.session.add(new_log)
                
            log_id_counter += 1
        
        print(f"    已为用户 {user.username} 添加访问日志数据。")

    print("  - UserLogs 数据插入完成。")
    # 事务提交由 db_test_and_init.py 处理
