# initial_data/08_access_location_tracker.py

from models.models import AccessLocationTracker, User
from datetime import datetime, date, timedelta
import random
import json

def insert_data(db):
    """
    插入模拟的访问IP/地点追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (AccessLocationTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()

    if not any([admin_user, patient_alice, dr_smith]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 AccessLocationTracker 数据插入。")
        return

    today = date.today()
    # 模拟过去 5 天的数据
    for i in range(5):
        record_date = today - timedelta(days=i)

        # 模拟IP地址
        normal_ips = [f"192.168.1.{random.randint(1, 254)}" for _ in range(3)]
        abnormal_ips = [f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(1)]

        # 管理员用户访问地点
        if admin_user:
            existing_tracker = db.session.query(AccessLocationTracker).filter_by(
                user_id=admin_user.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                tracker = AccessLocationTracker(
                    user_id=admin_user.id,
                    at_num_nd=10 + random.randint(0, 5), # 正常地点访问次数
                    at_num_ad=random.randint(0, 1),     # 异常地点访问次数
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                # 动态添加 IP 历史
                for ip in normal_ips:
                    tracker.add_ip_to_history(ip)
                if random.random() < 0.3: # 有30%的概率添加异常IP
                     tracker.add_ip_to_history(random.choice(abnormal_ips))

                db.session.add(tracker)
                print(f"    已添加管理员用户在 {record_date} 的访问地点追踪数据。")
            else:
                print(f"    管理员用户在 {record_date} 的访问地点追踪数据已存在，跳过。")

        # 患者用户访问地点
        if patient_alice:
            existing_tracker = db.session.query(AccessLocationTracker).filter_by(
                user_id=patient_alice.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                tracker = AccessLocationTracker(
                    user_id=patient_alice.id,
                    at_num_nd=5 + random.randint(0, 3),
                    at_num_ad=0,
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                for ip in normal_ips:
                    tracker.add_ip_to_history(ip)
                db.session.add(tracker)
                print(f"    已添加 patient_alice 用户在 {record_date} 的访问地点追踪数据。")
            else:
                print(f"    patient_alice 用户在 {record_date} 的访问地点追踪数据已存在，跳过。")

        # 医生用户访问地点
        if dr_smith:
            existing_tracker = db.session.query(AccessLocationTracker).filter_by(
                user_id=dr_smith.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                tracker = AccessLocationTracker(
                    user_id=dr_smith.id,
                    at_num_nd=15 + random.randint(0, 7),
                    at_num_ad=random.randint(0, 2),
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                for ip in normal_ips:
                    tracker.add_ip_to_history(ip)
                if random.random() < 0.5: # 有50%的概率添加异常IP
                     tracker.add_ip_to_history(random.choice(abnormal_ips))
                db.session.add(tracker)
                print(f"    已添加 dr_smith 用户在 {record_date} 的访问地点追踪数据。")
            else:
                print(f"    dr_smith 用户在 {record_date} 的访问地点追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理