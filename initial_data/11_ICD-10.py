from sqlalchemy import inspect
import csv
import os
from datetime import datetime
from modules.data_management.models import ICD10Code


def _count_csv_rows(csv_path: str) -> int:
    """快速统计 CSV 行数（不做列数检查，仅保持与后续读取方式一致）"""
    with open(csv_path, newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.reader(f))


def insert_data(db):
    """
    把 initial_data/ICD-10.csv 的内容插入 icd10_codes 表。
    如果表不存在 → 创建并插入。
    如果表存在 → 行数与 CSV 相同则跳过；否则按需补齐（跳过已存在编码）。
    """
    print("  - 正在导入初始 ICD‑10 编码数据 (ICD10Code)...")

    # CSV 路径：与本脚本同目录
    csv_path = os.path.join(os.path.dirname(__file__), "ICD-10.csv")
    if not os.path.exists(csv_path):
        print(f"    错误: 未找到 {csv_path}，跳过 ICD‑10 导入。")
        return

    inspector = inspect(db.engine)
    table_name = ICD10Code.__tablename__

    # 判断是否需要导入
    need_import = False
    if not inspector.has_table(table_name):
        print(f"    表 {table_name} 不存在，准备创建并导入数据…")
        # 若外部未先执行 db.create_all()，可以在此调用一次
        db.create_all()               # 如已有集中建表脚本，可去除本行
        need_import = True
    else:
        db_count = db.session.query(ICD10Code).count()
        csv_count = _count_csv_rows(csv_path)
        if db_count == csv_count:
            print(f"    表已存在且记录数一致（{db_count} 条），跳过导入。")
            return
        else:
            print(
                f"    表已存在，但记录数不一致（数据库 {db_count} / CSV {csv_count}），"
                "将补充缺失数据…"
            )
            need_import = True

    if not need_import:
        return  # 理论上到不了这行，但为了稳妥留着

    total, inserted, skipped = 0, 0, 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            total += 1

            # 列数校验
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
    # 事务提交由外部统一处理（如 db_test_and_init.py）
