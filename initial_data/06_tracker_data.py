# initial_data/06_tracker_data.py

from modules.data_management.models import UserAccessSuccessTracker
from modules.auth.models import User
from datetime import datetime

def insert_data(db):
    """
    插入模拟的用户访问成功率统计数据。
    """
    print("  - 正在插入初始追踪器数据 (UserAccessSuccessTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 UserAccessSuccessTracker 数据插入。")
        return

    # 管理员用户访问成功率
    if admin_user:
        existing_tracker = db.session.query(UserAccessSuccessTracker).filter_by(
            id_num=admin_user.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSuccessTracker(
                id=f"succ_{admin_user.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=admin_user.id_card,
                ast_num_as=95,  # 访问成功次数
                ast_num_af=5,   # 访问失败次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加管理员用户 {admin_user.id_card} 的访问成功率追踪数据。")
        else:
            print(f"    管理员用户 {admin_user.id_card} 的访问成功率追踪数据已存在，跳过。")

    # 患者用户访问成功率
    if patient_alice:
        existing_tracker = db.session.query(UserAccessSuccessTracker).filter_by(
            id_num=patient_alice.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSuccessTracker(
                id=f"succ_{patient_alice.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=patient_alice.id_card,
                ast_num_as=48,  # 访问成功次数
                ast_num_af=2,   # 访问失败次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 patient_alice 用户 {patient_alice.id_card} 的访问成功率追踪数据。")
        else:
            print(f"    patient_alice 用户 {patient_alice.id_card} 的访问成功率追踪数据已存在，跳过。")

    # 医生用户访问成功率
    if dr_smith:
        existing_tracker = db.session.query(UserAccessSuccessTracker).filter_by(
            id_num=dr_smith.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSuccessTracker(
                id=f"succ_{dr_smith.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=dr_smith.id_card,
                ast_num_as=130,  # 访问成功次数
                ast_num_af=5,    # 访问失败次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 dr_smith 用户 {dr_smith.id_card} 的访问成功率追踪数据。")
        else:
            print(f"    dr_smith 用户 {dr_smith.id_card} 的访问成功率追踪数据已存在，跳过。")

    # 科研人员访问成功率
    if researcher_eve:
        existing_tracker = db.session.query(UserAccessSuccessTracker).filter_by(
            id_num=researcher_eve.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSuccessTracker(
                id=f"succ_{researcher_eve.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=researcher_eve.id_card,
                ast_num_as=90,  # 访问成功次数
                ast_num_af=10,  # 访问失败次数（科研人员可能遇到更多权限问题）
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 researcher_eve 用户 {researcher_eve.id_card} 的访问成功率追踪数据。")
        else:
            print(f"    researcher_eve 用户 {researcher_eve.id_card} 的访问成功率追踪数据已存在，跳过。")
    # No commit here; it's handled by db_test_and_init.py