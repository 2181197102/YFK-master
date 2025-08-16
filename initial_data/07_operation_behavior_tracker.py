# initial_data/07_operation_behavior_tracker.py

from modules.data_management.models import UserOperationBehaviorTracker
from modules.auth.models import User
from datetime import datetime, timedelta

def insert_data(db):
    """
    插入模拟的用户操作行为追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (UserOperationBehaviorTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 UserOperationBehaviorTracker 数据插入。")
        return

    # 管理员用户行为
    if admin_user:
        existing_tracker = db.session.query(UserOperationBehaviorTracker).filter_by(
            id_num=admin_user.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserOperationBehaviorTracker(
                id=f"behav_{admin_user.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=admin_user.id_card,
                ob_num_view=150,
                ob_num_copy=25,
                ob_num_download=15,
                ob_num_add=10,
                ob_num_revise=8,
                ob_num_delet=2,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加管理员用户 {admin_user.id_card} 的操作行为追踪数据。")
        else:
            print(f"    管理员用户 {admin_user.id_card} 的操作行为追踪数据已存在，跳过。")

    # 患者用户行为
    if patient_alice:
        existing_tracker = db.session.query(UserOperationBehaviorTracker).filter_by(
            id_num=patient_alice.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserOperationBehaviorTracker(
                id=f"behav_{patient_alice.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=patient_alice.id_card,
                ob_num_view=50,
                ob_num_copy=0,
                ob_num_download=0,
                ob_num_add=0,
                ob_num_revise=0,
                ob_num_delet=0,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 patient_alice 用户 {patient_alice.id_card} 的操作行为追踪数据。")
        else:
            print(f"    patient_alice 用户 {patient_alice.id_card} 的操作行为追踪数据已存在，跳过。")

    # 医生用户行为
    if dr_smith:
        existing_tracker = db.session.query(UserOperationBehaviorTracker).filter_by(
            id_num=dr_smith.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserOperationBehaviorTracker(
                id=f"behav_{dr_smith.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=dr_smith.id_card,
                ob_num_view=200,
                ob_num_copy=12,
                ob_num_download=8,
                ob_num_add=25,
                ob_num_revise=18,
                ob_num_delet=1,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 dr_smith 用户 {dr_smith.id_card} 的操作行为追踪数据。")
        else:
            print(f"    dr_smith 用户 {dr_smith.id_card} 的操作行为追踪数据已存在，跳过。")

    # 科研人员用户行为
    if researcher_eve:
        existing_tracker = db.session.query(UserOperationBehaviorTracker).filter_by(
            id_num=researcher_eve.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserOperationBehaviorTracker(
                id=f"behav_{researcher_eve.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=researcher_eve.id_card,
                ob_num_view=300,
                ob_num_copy=45,
                ob_num_download=30,
                ob_num_add=5,
                ob_num_revise=3,
                ob_num_delet=0,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 researcher_eve 用户 {researcher_eve.id_card} 的操作行为追踪数据。")
        else:
            print(f"    researcher_eve 用户 {researcher_eve.id_card} 的操作行为追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理