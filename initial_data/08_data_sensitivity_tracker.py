# initial_data/08_data_sensitivity_tracker.py

from modules.data_management.models import DataSensitivityTracker
from modules.auth.models import  User
from datetime import datetime, date, timedelta

def insert_data(db):
    """
    插入模拟的访问数据敏感度追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (DataSensitivityTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 DataSensitivityTracker 数据插入。")
        return

    today = date.today()
    # 模拟过去 5 天的数据
    for i in range(5):
        record_date = today - timedelta(days=i)

        # 管理员用户敏感度访问
        if admin_user:
            existing_tracker = db.session.query(DataSensitivityTracker).filter_by(
                user_id=admin_user.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = DataSensitivityTracker(
                    user_id=admin_user.id,
                    ds_num1=20 + i * 3, # 敏感度级别1（最低）
                    ds_num2=10 + i * 2,
                    ds_num3=5 + i,
                    ds_num4=2, # 敏感度级别4（最高）
                    # ds_a, ds_b, ds_c, ds_d 保持默认值
                    date_recorded=record_date,
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加管理员用户在 {record_date} 的敏感度访问追踪数据。")
            else:
                print(f"    管理员用户在 {record_date} 的敏感度访问追踪数据已存在，跳过。")

        # 患者用户敏感度访问
        if patient_alice:
            existing_tracker = db.session.query(DataSensitivityTracker).filter_by(
                user_id=patient_alice.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = DataSensitivityTracker(
                    user_id=patient_alice.id,
                    ds_num1=10 + i,
                    ds_num2=2 + i,
                    ds_num3=0,
                    ds_num4=0,
                    date_recorded=record_date,
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 patient_alice 用户在 {record_date} 的敏感度访问追踪数据。")
            else:
                print(f"    patient_alice 用户在 {record_date} 的敏感度访问追踪数据已存在，跳过。")

        # 医生用户敏感度访问
        if dr_smith:
            existing_tracker = db.session.query(DataSensitivityTracker).filter_by(
                user_id=dr_smith.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = DataSensitivityTracker(
                    user_id=dr_smith.id,
                    ds_num1=18 + i * 2,
                    ds_num2=12 + i,
                    ds_num3=7 + i,
                    ds_num4=1 + i,
                    date_recorded=record_date,
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 dr_smith 用户在 {record_date} 的敏感度访问追踪数据。")
            else:
                print(f"    dr_smith 用户在 {record_date} 的敏感度访问追踪数据已存在，跳过。")

        # 科研人员敏感度访问
        if researcher_eve:
            existing_tracker = db.session.query(DataSensitivityTracker).filter_by(
                user_id=researcher_eve.id,
                date_recorded=record_date
            ).first()
            if not existing_tracker:
                new_tracker = DataSensitivityTracker(
                    user_id=researcher_eve.id,
                    ds_num1=25 + i * 4,
                    ds_num2=15 + i * 2,
                    ds_num3=10 + i,
                    ds_num4=3,
                    date_recorded=record_date,
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow()
                )
                db.session.add(new_tracker)
                print(f"    已添加 researcher_eve 用户在 {record_date} 的敏感度访问追踪数据。")
            else:
                print(f"    researcher_eve 用户在 {record_date} 的敏感度访问追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理