# initial_data/09_access_time_tracker.py

from modules.data_management.models import UserAccessTimeTracker
from modules.auth.models import User
from datetime import datetime
import json

def insert_data(db):
    """
    插入模拟的用户访问时间统计数据。
    """
    print("  - 正在插入初始追踪器数据 (UserAccessTimeTracker)...")

    # 获取要关联的用户
    admin_user = db.session.query(User).filter_by(username="admin").first()
    patient_alice = db.session.query(User).filter_by(username="patient_alice").first()
    dr_smith = db.session.query(User).filter_by(username="dr_smith").first()
    researcher_eve = db.session.query(User).filter_by(username="researcher_eve").first()

    if not any([admin_user, patient_alice, dr_smith, researcher_eve]):
        print("    警告: 未找到可关联追踪器数据的用户。跳过 UserAccessTimeTracker 数据插入。")
        return

    # 定义工作时间模板
    work_time_template = [
        {
            "type": "workday",
            "start_time": "08:00:00",
            "end_time": "18:00:00",
            "days": [1, 2, 3, 4, 5],  # 周一到周五
            "description": "工作日正常时间"
        },
        {
            "type": "weekend",
            "start_time": "09:00:00", 
            "end_time": "12:00:00",
            "days": [6],  # 周六
            "description": "周末时间"
        }
    ]

    # 管理员用户访问时间
    if admin_user:
        existing_tracker = db.session.query(UserAccessTimeTracker).filter_by(
            id_num=admin_user.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessTimeTracker(
                id=f"time_{admin_user.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=admin_user.id_card,
                ap_num_ni=95,  # 正常时间访问次数
                ap_num_ui=5,   # 异常时间访问次数
                work_time=json.dumps(work_time_template, ensure_ascii=False),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加管理员用户 {admin_user.id_card} 的访问时间追踪数据。")
        else:
            print(f"    管理员用户 {admin_user.id_card} 的访问时间追踪数据已存在，跳过。")

    # 患者用户访问时间
    if patient_alice:
        existing_tracker = db.session.query(UserAccessTimeTracker).filter_by(
            id_num=patient_alice.id_card
        ).first()
        if not existing_tracker:
            # 患者可能在任何时间访问
            patient_work_time = [
                {
                    "type": "flexible",
                    "start_time": "06:00:00",
                    "end_time": "23:00:00",
                    "days": [1, 2, 3, 4, 5, 6, 7],
                    "description": "灵活访问时间"
                }
            ]
            new_tracker = UserAccessTimeTracker(
                id=f"time_{patient_alice.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=patient_alice.id_card,
                ap_num_ni=45,  # 正常时间访问次数
                ap_num_ui=5,   # 异常时间访问次数
                work_time=json.dumps(patient_work_time, ensure_ascii=False),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 patient_alice 用户 {patient_alice.id_card} 的访问时间追踪数据。")
        else:
            print(f"    patient_alice 用户 {patient_alice.id_card} 的访问时间追踪数据已存在，跳过。")

    # 医生用户访问时间
    if dr_smith:
        existing_tracker = db.session.query(UserAccessTimeTracker).filter_by(
            id_num=dr_smith.id_card
        ).first()
        if not existing_tracker:
            # 医生可能有夜班
            doctor_work_time = [
                {
                    "type": "day_shift",
                    "start_time": "07:00:00",
                    "end_time": "19:00:00",
                    "days": [1, 2, 3, 4, 5],
                    "description": "日班时间"
                },
                {
                    "type": "night_shift",
                    "start_time": "19:00:00",
                    "end_time": "07:00:00",
                    "days": [6, 7],
                    "description": "夜班时间"
                }
            ]
            new_tracker = UserAccessTimeTracker(
                id=f"time_{dr_smith.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=dr_smith.id_card,
                ap_num_ni=120,  # 正常时间访问次数
                ap_num_ui=15,   # 异常时间访问次数
                work_time=json.dumps(doctor_work_time, ensure_ascii=False),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 dr_smith 用户 {dr_smith.id_card} 的访问时间追踪数据。")
        else:
            print(f"    dr_smith 用户 {dr_smith.id_card} 的访问时间追踪数据已存在，跳过。")

    # 科研人员访问时间
    if researcher_eve:
        existing_tracker = db.session.query(UserAccessTimeTracker).filter_by(
            id_num=researcher_eve.id_card
        ).first()
        if not existing_tracker:
            new_tracker = UserAccessTimeTracker(
                id=f"time_{researcher_eve.id_card}_{datetime.utcnow().strftime('%Y%m%d')}",
                id_num=researcher_eve.id_card,
                ap_num_ni=80,  # 正常时间访问次数
                ap_num_ui=20,  # 异常时间访问次数（科研人员可能经常加班）
                work_time=json.dumps(work_time_template, ensure_ascii=False),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 researcher_eve 用户 {researcher_eve.id_card} 的访问时间追踪数据。")
        else:
            print(f"    researcher_eve 用户 {researcher_eve.id_card} 的访问时间追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理