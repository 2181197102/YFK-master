# initial_data/06_tracker_data.py

from modules.data_management.models import AccessSuccessTracker
from modules.auth.models import  User, UserRoleRelation
from datetime import datetime, date, timedelta
import random



def insert_data(db):
    """
    插入模拟的访问成功率追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (AccessSuccessTracker)...")

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
        existing_tracker = db.session.query(AccessSuccessTracker).filter_by(
            user_id=user.id
        ).first()

        i = random.randint(1, 3)
        record_date = today - timedelta(days=i)

        if not existing_tracker:
            # 根据角色ID确定访问统计数据
            if role_id == 1:  # 患者
                success = 5 + i
                fail = 1
                role_name = "患者"
            elif 2 <= role_id <= 5:  # 医生（角色2-5）
                success = 10 + i * 2
                fail = 1+i
                role_name = f"医生(角色{role_id})"
            elif role_id == 6:  # 科研人员
                success = 50 + i * 1
                fail = 10 + i * 1
                role_name = "科研人员"
            elif role_id == 7:  # 管理者
                success = 50 + i * 1
                fail = 1
                role_name = "管理者"
            new_tracker = AccessSuccessTracker(
                user_id = user.id,
                ast_num_as=success,  # 访问成功次数
                ast_num_af=fail,  # 访问失败次数
                date_recorded=record_date,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(new_tracker)

            print(f"    已添加用户 {user.id} ({role_name}) 的访问成功率追踪数据。")
        else:
            print(f"    用户 {user.id} 的访问成功率追踪数据已存在，跳过。")
