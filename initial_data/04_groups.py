# initial_data/04_groups.py
from modules.auth.models import Group
from datetime import datetime

GROUPS_TO_ADD = [
    "第一人民医院",
    "市中心医院",
    "大学附属医院",
    "管理员测试医院"
]

def insert_data(db):
    """插入初始分组（医院）数据。"""
    print("  - 正在插入初始分组…")
    for gname in GROUPS_TO_ADD:
        existing = db.session.query(Group).filter_by(group_name=gname).first()
        if existing:
            print(f"    分组 '{gname}' 已存在，跳过。")
            continue

        grp = Group(
            group_name=gname,
            enable=True,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )
        db.session.add(grp)
        print(f"    已添加分组: {gname}")
