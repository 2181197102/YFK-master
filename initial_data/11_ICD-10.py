# initial_data/11_ICD-10.py
"""
将 ICD‑10.csv 中的编码导入数据库。
"""

import csv
import os
from datetime import datetime

from modules.data_management.models import ICD10Code


def insert_data(db):
    """
    把 initial_data/ICD-10.csv 的内容插入 icd10_codes 表。
    不重复插入已存在的编码。
    """
    print("  - 正在导入初始 ICD‑10 编码数据 (ICD10Code)...")

    # CSV 路径：与本脚本同目录
    csv_path = os.path.join(os.path.dirname(__file__), "ICD-10.csv")
    if not os.path.exists(csv_path):
        print(f"    错误: 未找到 {csv_path}，跳过 ICD‑10 导入。")
        return

    total, inserted, skipped = 0, 0, 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            total += 1

            # 行列数校验
            if len(row) != 6:
                print(f"    警告: 第 {total} 行列数不匹配，已跳过。")
                skipped += 1
                continue

            chapter, subcat, code, desc, alt_desc, short_desc = row

            # 若编码已存在则跳过
            if db.session.query(ICD10Code).filter_by(code=code).first():
                skipped += 1
                continue

            db.session.add(
                ICD10Code(
                    chapter=chapter,
                    subcategory=subcat,
                    code=code,
                    description=desc,
                    alt_desc=alt_desc,
                    short_desc=short_desc,
                    created_time=datetime.utcnow(),
                    updated_time=datetime.utcnow(),
                )
            )
            inserted += 1

            # 每成功插入 5 000 条即打印一次进度
            if inserted and inserted % 5000 == 0:
                print(f"    -> 已成功插入 {inserted} 条（已处理 {total} 条）")

    print(
        f"    已扫描 {total} 条记录；"
        f"成功插入 {inserted} 条；"
        f"跳过 {skipped} 条（已存在或格式错误）。"
    )
    # 事务提交由 db_test_and_init.py 统一处理
