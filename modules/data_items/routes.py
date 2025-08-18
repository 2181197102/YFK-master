# modules/data_items/routes.py
"""
数据项管理相关API路由
提供数据项和敏感等级管理的接口
"""

from flask import Blueprint

data_items_bp = Blueprint("data_items", __name__)

@data_items_bp.route("/health", methods=["GET"])
def health_check():
    """数据项管理模块健康检查"""
    return {"message": "Data Items module is running"}, 200
