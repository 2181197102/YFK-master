# initial_data/07_access_time_tracker.py

from modules.data_management.models import AccessTimeTracker
from modules.auth.models import  User
from datetime import datetime, date, timedelta
import random

def insert_data(db):
    """
    插入模拟的访问时间追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (AccessTimeTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()

    if not any([admin_user, patient_alice, dr_smith]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 AccessTimeTracker 数据插入。")
        return

    today = date.today()
    # 模拟过去 5 天的数据
    for i in range(5):
        record_date = today - timedelta(days=i)

        # 管理员用户访问时间
        if admin_user:
            existing_tracker = db.session.query(AccessTimeTracker).filter_by(
                user_id=admin_user.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = AccessTimeTracker(
                    user_id=admin_user.id,
                    ap_num_ni=20 + random.randint(0, 5), # 正常时间访问次数
                    ap_num_ui=random.randint(0, 2),     # 异常时间访问次数
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加管理员用户在 {record_date} 的访问时间追踪数据。")
            else:
                print(f"    管理员用户在 {record_date} 的访问时间追踪数据已存在，跳过。")

        # 患者用户访问时间
        if patient_alice:
            existing_tracker = db.session.query(AccessTimeTracker).filter_by(
                user_id=patient_alice.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = AccessTimeTracker(
                    user_id=patient_alice.id,
                    ap_num_ni=10 + random.randint(0, 3),
                    ap_num_ui=random.randint(0, 1),
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 patient_alice 用户在 {record_date} 的访问时间追踪数据。")
            else:
                print(f"    patient_alice 用户在 {record_date} 的访问时间追踪数据已存在，跳过。")

        # 医生用户访问时间
        if dr_smith:
            existing_tracker = db.session.query(AccessTimeTracker).filter_by(
                user_id=dr_smith.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = AccessTimeTracker(
                    user_id=dr_smith.id,
                    ap_num_ni=25 + random.randint(0, 7),
                    ap_num_ui=random.randint(0, 3),
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 dr_smith 用户在 {record_date} 的访问时间追踪数据。")
            else:
                print(f"    dr_smith 用户在 {record_date} 的访问时间追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理