# initial_data/09_access_time_tracker.py

from modules.data_management.models import AccessTimeTracker
from modules.auth.models import User, UserRoleRelation
from datetime import datetime, date, timedelta
import random


def insert_data(db):
    """
    插入模拟的访问时间追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (AccessTimeTracker)...")

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
        existing_tracker = db.session.query(AccessTimeTracker).filter_by(
            user_id=user.id
        ).first()

        i = random.randint(1, 3)
        record_date = today - timedelta(days=i)

        if not existing_tracker:
            if role_id == 1:  # 患者
                ap_num_ni = 20 + random.randint(0, 5)
                ap_num_ui = random.randint(0, 2)
            elif 2 <= role_id <= 5:
                ap_num_ni = 10 + random.randint(0, 3)
                ap_num_ui = random.randint(0, 1),
            elif role_id == 6:
                ap_num_ni = 15 + random.randint(0, 5)
                ap_num_ui = 1 + random.randint(2, 3)
            else:
                ap_num_ni = 20 + random.randint(0, 5)
                ap_num_ui = random.randint(0, 2)

            new_tracker = AccessTimeTracker(
                user_id=user.id,
                ap_num_ni=ap_num_ni,
                ap_num_ui=ap_num_ui,
                date_recorded=record_date,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 dr_smith 用户在 {record_date} 的访问时间追踪数据。")
        else:
            print(f"    dr_smith 用户在 {record_date} 的访问时间追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理
