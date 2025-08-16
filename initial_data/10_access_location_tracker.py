# initial_data/10_access_location_tracker.py

from modules.data_management.models import UserAccessLocationTracker
from modules.auth.models import User
from datetime import datetime

def insert_data(db):
    """
    插入模拟的用户访问地点统计数据。
    """
    print("  - 正在插入初始追踪器数据 (UserAccessLocationTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 UserAccessLocationTracker 数据插入。")
        return

    # 管理员用户访问地点
    if admin_user:
        existing_tracker = db.session.query(UserAccessLocationTracker).filter_by(
            id_num=admin_user.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessLocationTracker(
                id=f"loc_{admin_user.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=admin_user.id_card,
                at_num_nd=90,  # 正常地点访问次数
                at_num_ad=10,  # 异常地点访问次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加管理员用户 {admin_user.id_card} 的访问地点追踪数据。")
        else:
            print(f"    管理员用户 {admin_user.id_card} 的访问地点追踪数据已存在，跳过。")

    # 患者用户访问地点
    if patient_alice:
        existing_tracker = db.session.query(UserAccessLocationTracker).filter_by(
            id_num=patient_alice.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessLocationTracker(
                id=f"loc_{patient_alice.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=patient_alice.id_card,
                at_num_nd=48,  # 正常地点访问次数
                at_num_ad=2,   # 异常地点访问次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 patient_alice 用户 {patient_alice.id_card} 的访问地点追踪数据。")
        else:
            print(f"    patient_alice 用户 {patient_alice.id_card} 的访问地点追踪数据已存在，跳过。")

    # 医生用户访问地点
    if dr_smith:
        existing_tracker = db.session.query(UserAccessLocationTracker).filter_by(
            id_num=dr_smith.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessLocationTracker(
                id=f"loc_{dr_smith.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=dr_smith.id_card,
                at_num_nd=120,  # 正常地点访问次数
                at_num_ad=15,   # 异常地点访问次数（医生可能在不同科室）
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 dr_smith 用户 {dr_smith.id_card} 的访问地点追踪数据。")
        else:
            print(f"    dr_smith 用户 {dr_smith.id_card} 的访问地点追踪数据已存在，跳过。")

    # 科研人员访问地点
    if researcher_eve:
        existing_tracker = db.session.query(UserAccessLocationTracker).filter_by(
            id_num=researcher_eve.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessLocationTracker(
                id=f"loc_{researcher_eve.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=researcher_eve.id_card,
                at_num_nd=70,  # 正常地点访问次数
                at_num_ad=30,  # 异常地点访问次数（科研人员可能远程访问）
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 researcher_eve 用户 {researcher_eve.id_card} 的访问地点追踪数据。")
        else:
            print(f"    researcher_eve 用户 {researcher_eve.id_card} 的访问地点追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理