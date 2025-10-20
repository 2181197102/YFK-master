# initial_data/08_data_sensitivity_tracker.py

from modules.data_management.models import DataSensitivityTracker
from modules.auth.models import  User, UserRoleRelation
from datetime import datetime, date, timedelta
import random

def insert_data(db):
    """
    插入模拟的访问数据敏感度追踪数据。
    """
    print("  - 正在插入初始追踪器数据 (DataSensitivityTracker)...")

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
        existing_tracker = db.session.query(DataSensitivityTracker).filter_by(
            user_id=user.id
        ).first()

        i = random.randint(1, 3)
        record_date = today - timedelta(days=i)

        if not existing_tracker:
           if role_id == 1:  # 患者
               ds_num1 = 10 + i
               ds_num2 = 2 + i

           elif 2 <= role_id <= 5:  # 医生（角色2-5）
               ds_num1 = 18 + i * 2
               ds_num2 = 12 + i

           elif role_id == 6:
               ds_num1 = 25 + i * 4
               ds_num2 = 15 + i * 2

           else:
               ds_num1 = 20 + i * 3  # 敏感度级别1（最低）
               ds_num2 = 10 + i * 2


           new_tracker = DataSensitivityTracker(
                user_id=user.id,
                ds_num1=ds_num1,
                ds_num2=ds_num2,
                date_recorded=record_date,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow())

           db.session.add(new_tracker)
           print(f"    已添加 researcher_eve 用户在 {record_date} 的敏感度访问追踪数据。")
        else:
           print(f"    researcher_eve 用户在 {record_date} 的敏感度访问追踪数据已存在，跳过。")
    # 事务提交由 db_test_and_init.py 处理