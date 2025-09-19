# initial_data/09_access_time_tracker.py

from modules.data_management.models import AccessLocationTracker
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
        print("    警告: 未找到可关联追踪器数据的用户角色关系。跳过 AccessLocationTracker 数据插入。")
        return

    today = date.today()
    # 处理每个用户的角色数据
    for user, role_id in users_with_roles:
        existing_tracker = db.session.query(AccessLocationTracker).filter_by(
            user_id=user.id
        ).first()

        i = random.randint(1, 3)
        record_date = today - timedelta(days=i)

        if not existing_tracker:
            if role_id == 1:  # 患者
                at_num_nd = 20 + random.randint(0, 5)
                at_num_ad = random.randint(0, 2)
            elif 2 <= role_id <= 5:
                at_num_nd = 10 + random.randint(0, 3)
                at_num_ad = random.randint(0, 1),
            elif role_id == 6:
                at_num_nd = 15 + random.randint(0, 5)
                at_num_ad = 1 + random.randint(2, 3)
            else:
                at_num_nd = 20 + random.randint(0, 5)
                at_num_ad = random.randint(0, 2)

            new_tracker = AccessLocationTracker(
                user_id=user.id,
                at_num_nd=at_num_nd,
                at_num_ad=at_num_ad,
                date_recorded=record_date,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)
            print(f"    已添加 dr_smith 用户在 {record_date} AccessLocationTracker。")
        else:
            print(f"    dr_smith 用户在 {record_date} AccessLocationTracker，跳过。")
    # 事务提交由 db_test_and_init.py 处理
