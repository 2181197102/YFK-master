# initial_data/14_user_ips.py

from modules.data_management.models import UserIps
from modules.auth.models import User
from datetime import datetime, timedelta
import random

def insert_data(db):
    """
    插入模拟的用户常用IP数据。
    """
    print("  - 正在插入初始数据 (UserIps)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联的用户。跳过 UserIps 数据插入。")
        return

    # 为每个用户定义常用IP地址
    user_ip_data = [
        {
            "user": admin_user,
            "ips": [
                {"ip": "192.168.1.100", "count": 45, "description": "办公室主机"},
                {"ip": "192.168.1.101", "count": 30, "description": "办公室备用机"},
                {"ip": "10.0.1.50", "count": 25, "description": "服务器机房"}
            ]
        },
        {
            "user": patient_alice,
            "ips": [
                {"ip": "192.168.1.200", "count": 35, "description": "家庭网络"},
                {"ip": "192.168.1.201", "count": 15, "description": "家庭WiFi备用"}
            ]
        },
        {
            "user": dr_smith,
            "ips": [
                {"ip": "10.0.1.51", "count": 60, "description": "诊室工作站"},
                {"ip": "10.0.1.52", "count": 40, "description": "病房工作站"},
                {"ip": "10.0.1.53", "count": 35, "description": "急诊科工作站"}
            ]
        },
        {
            "user": researcher_eve,
            "ips": [
                {"ip": "203.0.113.10", "count": 55, "description": "研究室远程连接"},
                {"ip": "198.51.100.5", "count": 25, "description": "家庭办公"},
                {"ip": "10.0.1.60", "count": 20, "description": "实验室工作站"}
            ]
        }
    ]

    ip_id_counter = 1

    for user_data in user_ip_data:
        user = user_data["user"]
        if not user:
            continue
            
        print(f"    为用户 {user.username} ({user.id_card}) 添加常用IP地址...")
        
        for ip_info in user_data["ips"]:
            # 生成最后使用时间（过去7天内的随机时间）
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            last_seen_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            ip_id = f"ip_{user.id_card}_{ip_id_counter:03d}"
            
            # 检查是否已存在相同的IP记录
            existing_ip = db.session.query(UserIps).filter_by(
                id_num=user.id_card,
                ip_address=ip_info["ip"]
            ).first()
            
            if not existing_ip:
                new_user_ip = UserIps(
                    id=ip_id,
                    id_num=user.id_card,
                    ip_address=ip_info["ip"],
                    access_count=ip_info["count"],
                    last_seen=last_seen_time
                )
                db.session.add(new_user_ip)
                print(f"      添加IP: {ip_info['ip']} (使用次数: {ip_info['count']}, {ip_info['description']})")
            else:
                print(f"      IP {ip_info['ip']} 已存在，跳过。")
                
            ip_id_counter += 1
        
        print(f"    已为用户 {user.username} 添加常用IP数据。")

    print("  - UserIps 数据插入完成。")
    # 事务提交由 db_test_and_init.py 处理
