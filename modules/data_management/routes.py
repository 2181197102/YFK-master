# modules/data_management/routes.py
from datetime import datetime
import uuid

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from modules.data_management.models import (
    db,
    AccessSuccessTracker,
    OperationBehaviorTracker,
    DataSensitivityTracker,
    AccessTimeTracker,
    AccessLocationTracker,
)
from modules.auth.models import User
from modules.auth.decorators import role_required

from utils.response import (
    success_response,
    error_response,
    not_found_response,
    server_error_response,
)

data_mgmt_bp = Blueprint("data_management", __name__)


# ─────────────────────────── 访问成功率 ───────────────────────────
@data_mgmt_bp.route("/access-success/user/<user_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_access_success(user_id):
    """获取用户的访问成功率数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = AccessSuccessTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(
                AccessSuccessTracker.created_time >= datetime.fromisoformat(start_date)
            )
        if end_date:
            query = query.filter(
                AccessSuccessTracker.created_time <= datetime.fromisoformat(end_date)
            )

        records = query.order_by(AccessSuccessTracker.created_time.desc()).all()

        data = [
            {
                "id": r.id,
                "num_as": r.ast_num_as,
                "num_af": r.ast_num_af,
                "success_rate": r.ast_num_as
                / (r.ast_num_as + r.ast_num_af)
                if (r.ast_num_as + r.ast_num_af) > 0
                else 0,
                "created_time": r.created_time.isoformat(),
                "updated_time": r.updated_time.isoformat() if r.updated_time else None,
            }
            for r in records
        ]

        return success_response({"access_success_data": data})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get access success error")
        return server_error_response("获取访问成功率数据失败")


@data_mgmt_bp.route("/access-success", methods=["POST"])
@jwt_required()
def update_access_success():
    """更新访问成功率数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        user_id = data.get("user_id", current_user_id)
        num_as = data.get("num_as", 0)
        num_af = data.get("num_af", 0)

        today = datetime.utcnow().date()
        record = AccessSuccessTracker.query.filter(
            AccessSuccessTracker.user_id == user_id,
            func.date(AccessSuccessTracker.created_time) == today,
        ).first()

        if record:
            record.ast_num_as += num_as
            record.ast_num_af += num_af
            record.updated_time = datetime.utcnow()
        else:
            record = AccessSuccessTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                ast_num_as=num_as,
                ast_num_af=num_af,
            )
            db.session.add(record)

        db.session.commit()
        return success_response(message="访问成功率数据更新成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update access success error")
        return server_error_response("更新访问成功率数据失败")


# ─────────────────────────── 操作行为 ───────────────────────────
@data_mgmt_bp.route("/operation-behavior/user/<user_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_operation_behavior(user_id):
    """获取用户的操作行为数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = OperationBehaviorTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(
                OperationBehaviorTracker.created_time >= datetime.fromisoformat(
                    start_date
                )
            )
        if end_date:
            query = query.filter(
                OperationBehaviorTracker.created_time <= datetime.fromisoformat(end_date)
            )

        records = query.order_by(OperationBehaviorTracker.created_time.desc()).all()

        data = [
            {
                "id": r.id,
                "num_view": r.num_view,
                "num_copy": r.num_copy,
                "num_download": r.num_download,
                "num_add": r.num_add,
                "num_revise": r.num_revise,
                "num_delete": r.num_delete,
                "ob_a": r.ob_a,
                "ob_b": r.ob_b,
                "ob_c": r.ob_c,
                "created_time": r.created_time.isoformat(),
                "updated_time": r.updated_time.isoformat() if r.updated_time else None,
            }
            for r in records
        ]

        return success_response({"operation_behavior_data": data})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get operation behavior error")
        return server_error_response("获取操作行为数据失败")


@data_mgmt_bp.route("/operation-behavior", methods=["POST"])
@jwt_required()
def update_operation_behavior():
    """更新操作行为数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        user_id = data.get("user_id", current_user_id)

        today = datetime.utcnow().date()
        record = OperationBehaviorTracker.query.filter(
            OperationBehaviorTracker.user_id == user_id,
            func.date(OperationBehaviorTracker.created_time) == today,
        ).first()

        if record:
            record.num_view += data.get("num_view", 0)
            record.num_copy += data.get("num_copy", 0)
            record.num_download += data.get("num_download", 0)
            record.num_add += data.get("num_add", 0)
            record.num_revise += data.get("num_revise", 0)
            record.num_delete += data.get("num_delete", 0)
            record.updated_time = datetime.utcnow()
        else:
            record = OperationBehaviorTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_view=data.get("num_view", 0),
                num_copy=data.get("num_copy", 0),
                num_download=data.get("num_download", 0),
                num_add=data.get("num_add", 0),
                num_revise=data.get("num_revise", 0),
                num_delete=data.get("num_delete", 0),
                ob_a=data.get("ob_a", 0.3),
                ob_b=data.get("ob_b", 0.3),
                ob_c=data.get("ob_c", 0.4),
            )
            db.session.add(record)

        db.session.commit()
        return success_response(message="操作行为数据更新成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update operation behavior error")
        return server_error_response("更新操作行为数据失败")


# ─────────────────────────── 数据敏感度 ───────────────────────────
@data_mgmt_bp.route("/data-sensitivity/user/<user_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_data_sensitivity(user_id):
    """获取用户的数据敏感度数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = DataSensitivityTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(
                DataSensitivityTracker.created_time >= datetime.fromisoformat(
                    start_date
                )
            )
        if end_date:
            query = query.filter(
                DataSensitivityTracker.created_time <= datetime.fromisoformat(end_date)
            )

        records = query.order_by(DataSensitivityTracker.created_time.desc()).all()

        data = [
            {
                "id": r.id,
                "num1": r.num1,
                "num2": r.num2,
                "num3": r.num3,
                "num4": r.num4,
                "ds_a": r.ds_a,
                "ds_b": r.ds_b,
                "ds_c": r.ds_c,
                "ds_d": r.ds_d,
                "created_time": r.created_time.isoformat(),
                "updated_time": r.updated_time.isoformat() if r.updated_time else None,
            }
            for r in records
        ]

        return success_response({"data_sensitivity_data": data})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get data sensitivity error")
        return server_error_response("获取数据敏感度数据失败")


@data_mgmt_bp.route("/data-sensitivity", methods=["POST"])
@jwt_required()
def update_data_sensitivity():
    """更新数据敏感度数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        user_id = data.get("user_id", current_user_id)

        today = datetime.utcnow().date()
        record = DataSensitivityTracker.query.filter(
            DataSensitivityTracker.user_id == user_id,
            func.date(DataSensitivityTracker.created_time) == today,
        ).first()

        if record:
            record.num1 += data.get("num1", 0)
            record.num2 += data.get("num2", 0)
            record.num3 += data.get("num3", 0)
            record.num4 += data.get("num4", 0)
            record.updated_time = datetime.utcnow()
        else:
            record = DataSensitivityTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num1=data.get("num1", 0),
                num2=data.get("num2", 0),
                num3=data.get("num3", 0),
                num4=data.get("num4", 0),
                ds_a=data.get("ds_a", 1.0),
                ds_b=data.get("ds_b", 1.0),
                ds_c=data.get("ds_c", 1.0),
                ds_d=data.get("ds_d", 1.0),
            )
            db.session.add(record)

        db.session.commit()
        return success_response(message="数据敏感度数据更新成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update data sensitivity error")
        return server_error_response("更新数据敏感度数据失败")


# ─────────────────────────── 访问时间段 ───────────────────────────
@data_mgmt_bp.route("/access-period/user/<user_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_access_period(user_id):
    """获取用户的访问时间数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = AccessTimeTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(
                AccessTimeTracker.created_time >= datetime.fromisoformat(start_date)
            )
        if end_date:
            query = query.filter(
                AccessTimeTracker.created_time <= datetime.fromisoformat(end_date)
            )

        records = query.order_by(AccessTimeTracker.created_time.desc()).all()

        data = [
            {
                "id": r.id,
                "num_ni": r.num_ni,
                "num_ui": r.num_ui,
                "created_time": r.created_time.isoformat(),
                "updated_time": r.updated_time.isoformat() if r.updated_time else None,
            }
            for r in records
        ]

        return success_response({"access_period_data": data})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get access period error")
        return server_error_response("获取访问时间数据失败")


@data_mgmt_bp.route("/access-period", methods=["POST"])
@jwt_required()
def update_access_period():
    """更新访问时间数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        user_id = data.get("user_id", current_user_id)

        today = datetime.utcnow().date()
        record = AccessTimeTracker.query.filter(
            AccessTimeTracker.user_id == user_id,
            func.date(AccessTimeTracker.created_time) == today,
        ).first()

        if record:
            record.num_ni += data.get("num_ni", 0)
            record.num_ui += data.get("num_ui", 0)
            record.updated_time = datetime.utcnow()
        else:
            record = AccessTimeTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_ni=data.get("num_ni", 0),
                num_ui=data.get("num_ui", 0),
            )
            db.session.add(record)

        db.session.commit()
        return success_response(message="访问时间数据更新成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update access period error")
        return server_error_response("更新访问时间数据失败")


# ─────────────────────────── 访问 IP ───────────────────────────
@data_mgmt_bp.route("/access-location/user/<user_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_access_location(user_id):
    """获取用户的访问 IP 数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = AccessLocationTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(
                AccessLocationTracker.created_time >= datetime.fromisoformat(start_date)
            )
        if end_date:
            query = query.filter(
                AccessLocationTracker.created_time <= datetime.fromisoformat(end_date)
            )

        records = query.order_by(AccessLocationTracker.created_time.desc()).all()

        data = [
            {
                "id": r.id,
                "num_nd": r.num_nd,
                "num_ad": r.num_ad,
                "created_time": r.created_time.isoformat(),
                "updated_time": r.updated_time.isoformat() if r.updated_time else None,
            }
            for r in records
        ]

        return success_response({"access_location_data": data})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get access location error")
        return server_error_response("获取访问 IP 数据失败")


@data_mgmt_bp.route("/access-location", methods=["POST"])
@jwt_required()
def update_access_location():
    """更新访问 IP 数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        user_id = data.get("user_id", current_user_id)

        today = datetime.utcnow().date()
        record = AccessLocationTracker.query.filter(
            AccessLocationTracker.user_id == user_id,
            func.date(AccessLocationTracker.created_time) == today,
        ).first()

        if record:
            record.num_nd += data.get("num_nd", 0)
            record.num_ad += data.get("num_ad", 0)
            record.updated_time = datetime.utcnow()
        else:
            record = AccessLocationTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_nd=data.get("num_nd", 0),
                num_ad=data.get("num_ad", 0),
            )
            db.session.add(record)

        db.session.commit()
        return success_response(message="访问 IP 数据更新成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update access location error")
        return server_error_response("更新访问 IP 数据失败")
