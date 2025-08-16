# initial_data/08_data_sensitivity_tracker.py

from modules.data_management.models import UserAccessSensitiveData
from modules.auth.models import User
from datetime import datetime

def insert_data(db):
    """
    插入模拟的用户访问敏感数据统计数据。
    """
    print("  - 正在插入初始追踪器数据 (UserAccessSensitiveData)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 UserAccessSensitiveData 数据插入。")
        return

    # 管理员用户敏感度访问
    if admin_user:
        existing_tracker = db.session.query(UserAccessSensitiveData).filter_by(
            id_num=admin_user.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSensitiveData(
                id=f"sens_{admin_user.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=admin_user.id_card,
                ds_num1=100,  # 准标识符访问次数
                ds_num2=50,   # 显示标识符访问次数
                ds_num3=200,  # 低敏感数据访问次数
                ds_num4=25,   # 高敏感数据访问次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加管理员用户 {admin_user.id_card} 的敏感度访问追踪数据。")
        else:
            print(f"    管理员用户 {admin_user.id_card} 的敏感度访问追踪数据已存在，跳过。")

    # 患者用户敏感度访问
    if patient_alice:
        existing_tracker = db.session.query(UserAccessSensitiveData).filter_by(
            id_num=patient_alice.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSensitiveData(
                id=f"sens_{patient_alice.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=patient_alice.id_card,
                ds_num1=30,   # 准标识符访问次数
                ds_num2=10,   # 显示标识符访问次数
                ds_num3=50,   # 低敏感数据访问次数
                ds_num4=0,    # 高敏感数据访问次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 patient_alice 用户 {patient_alice.id_card} 的敏感度访问追踪数据。")
        else:
            print(f"    patient_alice 用户 {patient_alice.id_card} 的敏感度访问追踪数据已存在，跳过。")

    # 医生用户敏感度访问
    if dr_smith:
        existing_tracker = db.session.query(UserAccessSensitiveData).filter_by(
            id_num=dr_smith.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSensitiveData(
                id=f"sens_{dr_smith.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=dr_smith.id_card,
                ds_num1=80,   # 准标识符访问次数
                ds_num2=60,   # 显示标识符访问次数
                ds_num3=150,  # 低敏感数据访问次数
                ds_num4=40,   # 高敏感数据访问次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 dr_smith 用户 {dr_smith.id_card} 的敏感度访问追踪数据。")
        else:
            print(f"    dr_smith 用户 {dr_smith.id_card} 的敏感度访问追踪数据已存在，跳过。")

    # 科研人员敏感度访问
    if researcher_eve:
        existing_tracker = db.session.query(UserAccessSensitiveData).filter_by(
            id_num=researcher_eve.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessSensitiveData(
                id=f"sens_{researcher_eve.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=researcher_eve.id_card,
                ds_num1=150,  # 准标识符访问次数
                ds_num2=80,   # 显示标识符访问次数
                ds_num3=300,  # 低敏感数据访问次数
                ds_num4=60,   # 高敏感数据访问次数
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 researcher_eve 用户 {researcher_eve.id_card} 的敏感度访问追踪数据。")
        else:
            print(f"    researcher_eve 用户 {researcher_eve.id_card} 的敏感度访问追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理