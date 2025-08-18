# modules/data_items/routes.py
"""
数据项管理相关API路由
提供数据项和敏感等级管理的接口
"""

from datetime import datetime, timezone
import uuid

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from modules.data_items.models import DataItem, StaticSensitivityLevel
from utils.extensions import db
from modules.auth.models import User
from modules.auth.decorators import role_required

from utils.response import (
    success_response,
    error_response,
    not_found_response,
    server_error_response,
)

data_items_bp = Blueprint("data_items", __name__)


# ─────────────────────────── 数据项管理 ───────────────────────────
@data_items_bp.route("/data-items", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER", "DOCTOR")
def get_data_items():
    """获取数据项列表"""
    try:
        # 获取查询参数
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search")

        # 构建查询
        query = DataItem.query

        if search:
            query = query.filter(
                db.or_(
                    DataItem.associated_name.like(f"%{search}%"),
                    DataItem.associated_code.like(f"%{search}%")
                )
            )

        # 分页查询
        pagination = query.order_by(DataItem.created_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        items = [item.to_dict() for item in pagination.items]

        return success_response({
            "data_items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next
            }
        })

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get data items error")
        return server_error_response("获取数据项列表失败")


@data_items_bp.route("/data-items", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def create_data_item():
    """创建数据项"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 必需字段验证
        required_fields = ["associated_name", "associated_code"]
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必需字段: {field}", 400)

        # 检查数据项代码是否已存在
        existing = DataItem.query.filter_by(associated_code=data["associated_code"]).first()
        if existing:
            return error_response("数据项代码已存在", 400)

        # 生成ID
        item_id = f"di_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

        # 创建新数据项
        data_item = DataItem(
            id=item_id,
            associated_name=data["associated_name"],
            associated_code=data["associated_code"],
            created_time=datetime.now(timezone.utc),
            updated_time=datetime.now(timezone.utc)
        )

        db.session.add(data_item)
        db.session.commit()

        return success_response(
            result=data_item.to_dict(),
            message="数据项创建成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create data item error")
        return server_error_response("创建数据项失败")


@data_items_bp.route("/data-items/<item_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER", "DOCTOR")
def get_data_item(item_id):
    """获取单个数据项详情"""
    try:
        data_item = DataItem.query.get(item_id)
        if not data_item:
            return not_found_response("数据项不存在")

        return success_response(data_item.to_dict())

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get data item error")
        return server_error_response("获取数据项失败")


@data_items_bp.route("/data-items/<item_id>", methods=["PUT"])
@jwt_required()
@role_required("ADMIN")
def update_data_item(item_id):
    """更新数据项"""
    try:
        data_item = DataItem.query.get(item_id)
        if not data_item:
            return not_found_response("数据项不存在")

        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 更新字段
        if "associated_name" in data:
            data_item.associated_name = data["associated_name"]
        
        if "associated_code" in data:
            # 检查新代码是否与其他数据项冲突
            existing = DataItem.query.filter(
                DataItem.associated_code == data["associated_code"],
                DataItem.id != item_id
            ).first()
            if existing:
                return error_response("数据项代码已存在", 400)
            data_item.associated_code = data["associated_code"]

        data_item.updated_time = datetime.now(timezone.utc)

        db.session.commit()

        return success_response(
            result=data_item.to_dict(),
            message="数据项更新成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update data item error")
        return server_error_response("更新数据项失败")


@data_items_bp.route("/data-items/<item_id>", methods=["DELETE"])
@jwt_required()
@role_required("ADMIN")
def delete_data_item(item_id):
    """删除数据项"""
    try:
        data_item = DataItem.query.get(item_id)
        if not data_item:
            return not_found_response("数据项不存在")

        db.session.delete(data_item)
        db.session.commit()

        return success_response(message="数据项删除成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Delete data item error")
        return server_error_response("删除数据项失败")


# ─────────────────────────── 静态敏感等级管理 ───────────────────────────
@data_items_bp.route("/sensitivity-levels", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER", "DOCTOR")
def get_sensitivity_levels():
    """获取静态敏感等级列表"""
    try:
        # 获取查询参数
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        sensitivity_level = request.args.get("sensitivity_level", type=int)
        search = request.args.get("search")

        # 构建查询
        query = StaticSensitivityLevel.query

        if sensitivity_level:
            query = query.filter(StaticSensitivityLevel.sensitivity_level == sensitivity_level)

        if search:
            query = query.filter(
                db.or_(
                    StaticSensitivityLevel.data_name.like(f"%{search}%"),
                    StaticSensitivityLevel.description.like(f"%{search}%")
                )
            )

        # 分页查询
        pagination = query.order_by(
            StaticSensitivityLevel.sensitivity_level.asc(),
            StaticSensitivityLevel.created_time.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        levels = [level.to_dict() for level in pagination.items]

        return success_response({
            "sensitivity_levels": levels,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next
            }
        })

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get sensitivity levels error")
        return server_error_response("获取敏感等级列表失败")


@data_items_bp.route("/sensitivity-levels", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def create_sensitivity_level():
    """创建静态敏感等级"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 必需字段验证
        required_fields = ["data_name", "description", "sensitivity_level"]
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必需字段: {field}", 400)

        # 验证敏感等级值
        if data["sensitivity_level"] not in [1, 2, 3, 4]:
            return error_response("敏感等级必须是1-4之间的整数", 400)

        # 生成ID
        level_id = f"ssl_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

        # 创建新敏感等级
        sensitivity_level = StaticSensitivityLevel(
            id=level_id,
            data_name=data["data_name"],
            description=data["description"],
            sensitivity_level=data["sensitivity_level"],
            created_time=datetime.now(timezone.utc),
            updated_time=datetime.now(timezone.utc)
        )

        db.session.add(sensitivity_level)
        db.session.commit()

        return success_response(
            result=sensitivity_level.to_dict(),
            message="敏感等级创建成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create sensitivity level error")
        return server_error_response("创建敏感等级失败")


@data_items_bp.route("/sensitivity-levels/<level_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER", "DOCTOR")
def get_sensitivity_level(level_id):
    """获取单个敏感等级详情"""
    try:
        sensitivity_level = StaticSensitivityLevel.query.get(level_id)
        if not sensitivity_level:
            return not_found_response("敏感等级不存在")

        return success_response(sensitivity_level.to_dict())

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get sensitivity level error")
        return server_error_response("获取敏感等级失败")


@data_items_bp.route("/sensitivity-levels/<level_id>", methods=["PUT"])
@jwt_required()
@role_required("ADMIN")
def update_sensitivity_level(level_id):
    """更新敏感等级"""
    try:
        sensitivity_level = StaticSensitivityLevel.query.get(level_id)
        if not sensitivity_level:
            return not_found_response("敏感等级不存在")

        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 更新字段
        if "data_name" in data:
            sensitivity_level.data_name = data["data_name"]
        
        if "description" in data:
            sensitivity_level.description = data["description"]
            
        if "sensitivity_level" in data:
            if data["sensitivity_level"] not in [1, 2, 3, 4]:
                return error_response("敏感等级必须是1-4之间的整数", 400)
            sensitivity_level.sensitivity_level = data["sensitivity_level"]

        sensitivity_level.updated_time = datetime.now(timezone.utc)

        db.session.commit()

        return success_response(
            result=sensitivity_level.to_dict(),
            message="敏感等级更新成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update sensitivity level error")
        return server_error_response("更新敏感等级失败")


@data_items_bp.route("/sensitivity-levels/<level_id>", methods=["DELETE"])
@jwt_required()
@role_required("ADMIN")
def delete_sensitivity_level(level_id):
    """删除敏感等级"""
    try:
        sensitivity_level = StaticSensitivityLevel.query.get(level_id)
        if not sensitivity_level:
            return not_found_response("敏感等级不存在")

        db.session.delete(sensitivity_level)
        db.session.commit()

        return success_response(message="敏感等级删除成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Delete sensitivity level error")
        return server_error_response("删除敏感等级失败")


# ─────────────────────────── 敏感等级统计 ───────────────────────────
@data_items_bp.route("/sensitivity-levels/stats", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_sensitivity_level_stats():
    """获取敏感等级统计信息"""
    try:
        # 按敏感等级分组统计
        stats = db.session.query(
            StaticSensitivityLevel.sensitivity_level,
            func.count(StaticSensitivityLevel.id).label('count')
        ).group_by(StaticSensitivityLevel.sensitivity_level).all()

        level_names = {
            1: '准标识符',
            2: '显示标识符',
            3: '低敏感数据', 
            4: '高敏感数据'
        }

        result = []
        for level, count in stats:
            result.append({
                'sensitivity_level': level,
                'level_name': level_names.get(level, '未知'),
                'count': count
            })

        # 总数统计
        total_count = StaticSensitivityLevel.query.count()

        return success_response({
            'level_stats': result,
            'total_count': total_count
        })

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get sensitivity level stats error")
        return server_error_response("获取敏感等级统计失败")
