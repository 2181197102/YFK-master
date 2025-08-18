# modules/medical_institutions/routes.py
"""
医疗机构相关API路由
提供患者病历、医生病历等相关数据的管理接口
"""

from flask import Blueprint

medical_inst_bp = Blueprint("medical_institutions", __name__)

@medical_inst_bp.route("/health", methods=["GET"])
def health_check():
    """医疗机构模块健康检查"""
    return {"message": "Medical Institutions module is running"}, 200
