# initial_data/05_operation_behavior_tracker.py

from modules.data_management.models import OperationBehaviorTracker
from modules.auth.models import  User
from datetime import datetime, date, timedelta

def insert_data(db):
    """
    插入模拟的访问操作行为追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (OperationBehaviorTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()

    if not any([admin_user, patient_alice, dr_smith]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 OperationBehaviorTracker 数据插入。")
        return

    today = date.today()
    # 模拟过去 5 天的数据
    for i in range(5):
        record_date = today - timedelta(days=i)

        # 管理员用户行为
        if admin_user:
            existing_tracker = db.session.query(OperationBehaviorTracker).filter_by(
                user_id=admin_user.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = OperationBehaviorTracker(
                    user_id=admin_user.id,
                    ob_num_view=15 + i * 2,
                    ob_num_copy=5 + i,
                    ob_num_download=3 + i,
                    ob_num_add=2 + i,
                    ob_num_revise=1 + i,
                    ob_num_delete=0,
                    # ob_a, ob_b, ob_c 保持默认值
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加管理员用户在 {record_date} 的操作行为追踪数据。")
            else:
                print(f"    管理员用户在 {record_date} 的操作行为追踪数据已存在，跳过。")

        # 患者用户行为
        if patient_alice:
            existing_tracker = db.session.query(OperationBehaviorTracker).filter_by(
                user_id=patient_alice.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = OperationBehaviorTracker(
                    user_id=patient_alice.id,
                    ob_num_view=10 + i,
                    ob_num_copy=0,
                    ob_num_download=0,
                    ob_num_add=0,
                    ob_num_revise=0,
                    ob_num_delete=0,
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 patient_alice 用户在 {record_date} 的操作行为追踪数据。")
            else:
                print(f"    patient_alice 用户在 {record_date} 的操作行为追踪数据已存在，跳过。")

        # 医生用户行为
        if dr_smith:
            existing_tracker = db.session.query(OperationBehaviorTracker).filter_by(
                user_id=dr_smith.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = OperationBehaviorTracker(
                    user_id=dr_smith.id,
                    ob_num_view=20 + i * 3,
                    ob_num_copy=2 + i,
                    ob_num_download=1 + i,
                    ob_num_add=5 + i,
                    ob_num_revise=3 + i,
                    ob_num_delete=0,
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 dr_smith 用户在 {record_date} 的操作行为追踪数据。")
            else:
                print(f"    dr_smith 用户在 {record_date} 的操作行为追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理