#!/usr/bin/env python3
"""
数据库连接测试与初始化脚本

步骤：
1. 测试数据库连通性
2. 创建全部表 (db.create_all)
3. 遍历 initial_data/*.py，调用 insert_data(db) 插入初始数据
"""

import sys
import os
import importlib.util
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from config import Config        # 你的 Config 类，保持不变

# ---------------------------------------------------------------------------
# 0. 准备工作：将项目根目录放进 sys.path，确保可以 import app / modules / models
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# ---------------------------------------------------------------------------
# 1. 导入 Flask app 工厂与 db，并确保模型全部注册
# ---------------------------------------------------------------------------
try:
    from app import create_app, db           # create_app 内部会实例化 db
    import models                            # <<< 触发 models/__init__.py，完成模型注册
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    print("请确认 app.py / models/__init__.py 路径正确。")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. 初始数据目录
# ---------------------------------------------------------------------------
INITIAL_DATA_DIR = ROOT_DIR / "initial_data"


def load_initial_data(app) -> None:
    """
    加载并插入 initial_data/ 下的所有初始数据。
    每个文件需实现 insert_data(db)。
    """
    if not INITIAL_DATA_DIR.exists():
        print("⚠️  未检测到 initial_data 目录，跳过初始数据插入。")
        return

    print("\n" + "=" * 50)
    print("开始插入初始数据...")
    print("=" * 50)

    with app.app_context():
        for py in sorted(INITIAL_DATA_DIR.glob("*.py")):
            if py.name == "__init__.py":
                continue

            module_name = py.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, py)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)       # type: ignore
                if hasattr(module, "insert_data") and callable(module.insert_data):
                    print(f"→ 正在执行 {py.name} ...")
                    module.insert_data(db)
                    db.session.commit()
                    print(f"✓ {py.name} 数据插入完成")
                else:
                    print(f"⚠️  {py.name} 未定义 insert_data(db) → 跳过")
            except Exception as e:
                db.session.rollback()
                print(f"✗ 处理 {py.name} 时出错，已回滚：{e}")

    print("=" * 50)
    print("初始数据插入流程结束")
    print("=" * 50)


# ---------------------------------------------------------------------------
# 3. 核心函数：连接测试 → 创建表 → 插入数据
# ---------------------------------------------------------------------------
def test_database_connection_and_initialize() -> bool:
    cfg = Config()

    print("=" * 50)
    print("数据库连接测试与初始化")
    print("=" * 50)
    print(f"HOST   : {cfg.DB_HOST}")
    print(f"PORT   : {cfg.DB_PORT}")
    print(f"USER   : {cfg.DB_USER}")
    print(f"DB NAME: {cfg.DB_NAME}")
    print("-" * 50)

    # 单独拿一个变量，方便 finally / except 中使用
    flask_app: Optional["Flask"] = None

    try:
        engine = create_engine(cfg.SQLALCHEMY_DATABASE_URI)

        # 1) 连接测试
        with engine.connect() as conn:
            print("✓ 数据库连接成功")
            mysql_ver = conn.execute(text("SELECT VERSION()")).scalar()
            current_db = conn.execute(text("SELECT DATABASE()")).scalar()
            print(f"   MySQL 版本：{mysql_ver}")
            print(f"   当前库   ：{current_db}")

        # 2) 创建表
        print("\n" + "=" * 50)
        print("开始创建表...")
        print("=" * 50)

        flask_app = create_app("default")
        with flask_app.app_context():
            db.create_all()
            print("✓ 表创建完毕")

        # 3) 插入初始数据
        load_initial_data(flask_app)
        return True

    except SQLAlchemyError as e:
        print(f"✗ SQLAlchemyError: {e}")
    except Exception as e:
        print(f"✗ 未知错误: {e}")
    finally:
        if flask_app:
            with flask_app.app_context():
                db.session.rollback()

    return False


# ---------------------------------------------------------------------------
# 4. CLI 入口
# ---------------------------------------------------------------------------
def main() -> int:
    print("\n" + "=" * 50)
    print("医疗系统数据库初始化工具")
    print("=" * 50)

    ok = test_database_connection_and_initialize()

    print("\n" + "=" * 50)
    if ok:
        print("🎉 全部流程执行完毕，数据库已就绪")
    else:
        print("⚠️  流程失败，请检查上述日志")
    print("=" * 50)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
