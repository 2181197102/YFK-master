# initial_data/05_user_groups.py
from modules.auth.models import User, Group, UserGroupRelation
from datetime import datetime

# 用户‑组映射（username, group_name, 关系类型）
USER_GROUP_MAP = [
    ("patient_alice",  "第一人民医院",  "base"),
    ("patient_bob",    "第一人民医院",  "base"),
    ("dr_smith",       "市中心医院",   "base"),
    ("researcher_eve", "大学附属医院", "base"),
    ("admin", "管理员测试医院", "base"),
]

def insert_data(db):
    """插入用户‑组关联数据。"""
    print("  - 正在插入用户‑组关联…")
    for uname, gname, rel_type in USER_GROUP_MAP:
        user = db.session.query(User).filter_by(username=uname).first()
        group = db.session.query(Group).filter_by(group_name=gname).first()

        if not user:
            print(f"    警告: 未找到用户 '{uname}'。")
            continue
        if not group:
            print(f"    警告: 未找到分组 '{gname}'。")
            continue

        exists = db.session.query(UserGroupRelation).filter_by(
            user_id=user.id, group_id=group.id
        ).first()
        if exists:
            print(f"    用户 '{uname}' 已在分组 '{gname}' 中，跳过。")
            continue

        rel = UserGroupRelation(
            user_id=user.id,
            group_id=group.id,
            type=rel_type,
            enable=True,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(rel)
        print(f"    已关联用户 '{uname}' ↔ 分组 '{gname}'（{rel_type}）")
