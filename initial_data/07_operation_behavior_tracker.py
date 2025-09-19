# initial_data/07_operation_behavior_tracker.py

from modules.data_management.models import OperationBehaviorTracker
from modules.auth.models import  User, UserRoleRelation
from datetime import datetime, date, timedelta
import random


def insert_data(db):
    """
    插入模拟的访问操作行为追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (OperationBehaviorTracker)...")

    # 获取要关联的用户
    users_with_roles = db.session.query(User, UserRoleRelation.role_id). \
        join(UserRoleRelation, User.id == UserRoleRelation.user_id). \
        filter(UserRoleRelation.role_id.between(1, 7)). \
        all()

    if not users_with_roles:
        print("    警告: 未找到可关联追踪器数据的用户角色关系。跳过 UserAccessSuccessTracker 数据插入。")
        return

    today = date.today()
    # 处理每个用户的角色数据
    for user, role_id in users_with_roles:
        existing_tracker = db.session.query(OperationBehaviorTracker).filter_by(
            user_id=user.id
        ).first()

        i = random.randint(1, 3)
        record_date = today - timedelta(days=i)

        if not existing_tracker:
           if role_id == 1:  # 患者
                ob_num_view = 10 + i
                ob_num_copy = 0
                ob_num_download = 0
                ob_num_add = 0
                ob_num_revise = 0
                ob_num_delete = 0
           elif 2 <= role_id <= 5:  # 医生（角色2-5）
                ob_num_view = 20 + i * 3
                ob_num_copy = 2 + i
                ob_num_download = 1 + i
                ob_num_add = 5 + i
                ob_num_revise = 3 + i
                ob_num_delete = 0
           elif role_id == 6:
                ob_num_view = 20 + i * 3
                ob_num_copy = 2 + i
                ob_num_download = 1 + i
                ob_num_add = 5 + i
                ob_num_revise = 3 + i
                ob_num_delete = 0
           else:
                ob_num_view = 10 + i
                ob_num_copy = 0
                ob_num_download = 0
                ob_num_add = 0
                ob_num_revise = 0
                ob_num_delete = 0
           new_tracker = OperationBehaviorTracker(
                user_id=user.id,
                ob_num_view=ob_num_view,
                ob_num_copy=ob_num_copy,
                ob_num_download=ob_num_download,
                ob_num_add=ob_num_add,
                ob_num_revise=ob_num_revise,
                ob_num_delete=ob_num_delete,
                date_recorded=record_date,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
           db.session.add(new_tracker)
           print(f"    已添加 patient_alice 用户在 {record_date} 的操作行为追踪数据。")
        else:
           print(f"    patient_alice 用户在 {record_date} 的操作行为追踪数据已存在，跳过。")

