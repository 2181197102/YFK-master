#!/usr/bin/env python3
"""
数据库连接测试与初始化文件
"""

import sys
import os
import importlib
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import Config

# 确保在 db_test_and_init.py 中可以正确导入 app 和 db 对象
# 如果你的 models.py 在 models/ 目录下，确保 db 对象已正确定义
try:
    from app import create_app, db
    # 导入所有的模型，确保 db.create_all() 能够发现它们
    # 根据你的 models 结构，可能需要调整导入方式
    # 例如，如果所有模型都在 models/models.py 中:
    import models.models
except ImportError:
    print("错误：无法从 'app.py' 或 'models/models.py' 导入必要的模块。")
    print("请确保你的主 Flask 应用文件名为 'app.py' 且与此脚本在同一级目录，")
    print("并且 'models/models.py' 存在且包含所有模型定义。")
    sys.exit(1)

# 定义初始数据文件夹的路径
INITIAL_DATA_DIR = os.path.join(os.path.dirname(__file__), 'initial_data')


def load_initial_data(app):
    """
    加载并插入初始数据。
    它会遍历 initial_data 目录下的所有 Python 文件，并尝试执行其中的 insert_data 函数。
    """
    print("\n" + "=" * 50)
    print("开始插入初始数据...")
    print("=" * 50)

    # 确保在 Flask 应用上下文中执行数据库操作
    with app.app_context():
        # 遍历 initial_data 目录
        for filename in os.listdir(INITIAL_DATA_DIR):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]  # 移除 .py 后缀
                module_path = os.path.join(INITIAL_DATA_DIR, filename)

                try:
                    # 动态导入模块
                    # 注意：为了避免冲突，最好确保 initial_data 目录不是一个 Python 包
                    # 或者使用更复杂的导入方式（如 importlib.util.spec_from_file_location）
                    # 对于简单情况，直接修改 sys.path 可能更方便，但通常不推荐
                    # 这里为了简化，我们假设模块名不会与现有包冲突
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # 尝试调用模块中的 insert_data 函数
                    if hasattr(module, 'insert_data') and callable(module.insert_data):
                        print(f"正在插入来自 '{filename}' 的数据...")
                        module.insert_data(db)  # 将 db 对象传递给插入函数
                        db.session.commit()
                        print(f"✓ 成功插入来自 '{filename}' 的数据。")
                    else:
                        print(f"警告：文件 '{filename}' 中未找到 'insert_data' 函数，跳过。")

                except Exception as e:
                    db.session.rollback() # 发生错误时回滚
                    print(f"✗ 插入来自 '{filename}' 的数据时发生错误: {str(e)}")
                    print("数据插入已回滚。")
        print("=" * 50)
        print("初始数据插入完成。")
        print("=" * 50)


def test_database_connection_and_initialize():
    """
    测试数据库连接，并在成功后初始化数据库（创建表），然后插入初始数据。
    """
    config = Config()

    print("=" * 50)
    print("开始数据库连接测试与初始化...")
    print("=" * 50)
    print(f"数据库主机: {config.DB_HOST}")
    print(f"数据库端口: {config.DB_PORT}")
    print(f"数据库用户: {config.DB_USER}")
    print(f"数据库名称: {config.DB_NAME}")
    print("-" * 50)

    flask_app = None # 定义在 try 块外，以便在 except 块中访问

    try:
        # 创建数据库引擎
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

        # 测试连接
        with engine.connect() as connection:
            print("✓ 数据库连接成功！")

            # 测试基本查询，例如获取MySQL版本
            result = connection.execute(text("SELECT VERSION() as version"))
            version = result.fetchone()
            print(f"✓ MySQL版本: {version[0]}")

            # 确认当前连接的数据库
            result = connection.execute(text("SELECT DATABASE() as db_name"))
            db_name_result = result.fetchone()
            print(f"✓ 当前连接的数据库: {db_name_result[0]}")

            # 检查数据库编码（可选，但有助于调试编码问题）
            result = connection.execute(
                text(
                    "SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME "
                    "FROM information_schema.SCHEMATA "
                    "WHERE SCHEMA_NAME = :db_name"
                ),
                {"db_name": config.DB_NAME}
            )
            charset_info = result.fetchone()
            if charset_info:
                print(f"✓ 数据库编码: {charset_info[0]}")
                print(f"✓ 数据库排序规则: {charset_info[1]}")

            print("-" * 50)
            print("✓ 数据库连接测试通过！")

            # --- 数据库初始化（创建表）部分 ---
            print("\n" + "=" * 50)
            print("开始执行数据库初始化（创建表）...")
            print("=" * 50)

            # 创建 Flask 应用上下文来执行 db.create_all()
            # 'default' 是 create_app 函数的 config_name 参数，请确保与你的 config.py 配置相符
            flask_app = create_app('default')
            with flask_app.app_context():
                db.create_all()
                print("✓ 数据库表创建成功！")
            print("=" * 50)

            # --- 插入初始数据部分 ---
            load_initial_data(flask_app) # 调用新的函数来加载并插入数据

    except SQLAlchemyError as e:
        print(f"✗ 数据库操作失败: {str(e)}")
        # 如果在插入数据时出错，确保回滚
        if flask_app:
            with flask_app.app_context():
                db.session.rollback()
        return False
    except Exception as e:
        print(f"✗ 发生未知错误: {str(e)}")
        # 如果在插入数据时出错，确保回滚
        if flask_app:
            with flask_app.app_context():
                db.session.rollback()
        return False

    return True


def main():
    """主函数，用于执行数据库测试和初始化流程"""
    print("\n" + "=" * 50)
    print("医疗系统数据库测试与初始化工具")
    print("=" * 50)

    success = test_database_connection_and_initialize()

    print("\n" + "=" * 50)
    if success:
        print("✓ 所有测试和初始化任务已成功完成！数据库已准备就绪。")
    else:
        print("✗ 任务失败！请检查上述错误信息，并确保数据库配置正确。")
    print("=" * 50)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())