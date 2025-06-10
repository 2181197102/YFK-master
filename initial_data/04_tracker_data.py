# initial_data/04_tracker_data.py

from models.models import AccessSuccessTracker, User
from datetime import datetime, date, timedelta

def insert_data(db):
    """
    插入模拟的访问成功率追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (AccessSuccessTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()

    if not admin_user and not patient_alice:
        print("    警告: 未找到可关联追踪器数据的用户。跳过追踪器数据插入。")
        return

    # 模拟过去几天的每日数据
    today = date.today()
    for i in range(3): # 过去 3 天
        record_date = today - timedelta(days=i)

        if admin_user:
            existing_tracker = db.session.query(AccessSuccessTracker).filter_by(
                user_id=admin_user.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = AccessSuccessTracker(
                    user_id=admin_user.id,
                    ast_num_as=10 + i * 2,  # 示例: 10, 12, 14 成功访问
                    ast_num_af=1 + i,      # 示例: 1, 2, 3 失败访问
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加管理员用户在 {record_date} 的追踪器数据。")
            else:
                print(f"    管理员用户在 {record_date} 的追踪器数据已存在，跳过。")

        if patient_alice:
            existing_tracker = db.session.query(AccessSuccessTracker).filter_by(
                user_id=patient_alice.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = AccessSuccessTracker(
                    user_id=patient_alice.id,
                    ast_num_as=5 + i,      # 示例: 5, 6, 7 成功访问
                    ast_num_af=0,          # 示例: 0, 0, 0 失败访问
                    date_recorded=record_date,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 patient_alice 用户在 {record_date} 的追踪器数据。")
            else:
                print(f"    patient_alice 用户在 {record_date} 的追踪器数据已存在，跳过。")
    # No commit here; it's handled by db_test_and_init.py