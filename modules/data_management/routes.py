# modules/data_management/routes.py
from datetime import datetime
import uuid

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from modules.data_management.models import (
    UserLogs,
    UserAccessSensitiveData,
    UserAccessLocationTracker,
    UserIps,
    UserAccessSuccessTracker,
    UserAccessTimeTracker,
    UserOperationBehaviorTracker,
    ICD10Code,
    DiseaseDataItem,
)
from modules.data_management.trust_calculator import TrustCalculator
from utils.extensions import db
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
@data_mgmt_bp.route("/access-success/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_access_success(id_num):
    """获取用户的访问成功率数据"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 查询用户的访问成功率数据
        record = UserAccessSuccessTracker.query.filter_by(id_num=id_num).first()
        
        if not record:
            return success_response({
                "access_success_data": {
                    "id_num": id_num,
                    "success_count": 0,
                    "failure_count": 0,
                    "success_rate": 0.0,
                    "created_time": None,
                    "updated_time": None
                }
            })

        data = {
            "id": record.id,
            "id_num": record.id_num,
            "success_count": record.ast_num_as,
            "failure_count": record.ast_num_af,
            "success_rate": record.calculate_success_rate(),
            "created_time": record.created_time.isoformat() if record.created_time else None,
            "updated_time": record.updated_time.isoformat() if record.updated_time else None,
        }

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

        # 获取当前用户的身份证号
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        id_num = data.get("id_num", current_user.id_card)
        success_count = data.get("success_count", 0)
        failure_count = data.get("failure_count", 0)

        # 验证目标用户是否存在
        target_user = User.query.filter_by(id_card=id_num).first()
        if not target_user:
            return error_response("目标用户不存在", 400)

        # 查找现有记录
        record = UserAccessSuccessTracker.query.filter_by(id_num=id_num).first()

        if record:
            # 更新现有记录
            record.ast_num_as += success_count
            record.ast_num_af += failure_count
            record.updated_time = datetime.utcnow()
        else:
            # 创建新记录
            record = UserAccessSuccessTracker(
                id=f"succ_{id_num}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                id_num=id_num,
                ast_num_as=success_count,
                ast_num_af=failure_count,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(record)

        db.session.commit()
        return success_response(
            result={
                "id_num": id_num,
                "success_count": record.ast_num_as,
                "failure_count": record.ast_num_af,
                "success_rate": record.calculate_success_rate()
            },
            message="访问成功率数据更新成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update access success error")
        return server_error_response("更新访问成功率数据失败")


# ─────────────────────────── 操作行为 ───────────────────────────
@data_mgmt_bp.route("/operation-behavior/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_operation_behavior(id_num):
    """获取用户的操作行为数据"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 查询用户的操作行为数据
        record = UserOperationBehaviorTracker.query.filter_by(id_num=id_num).first()
        
        if not record:
            return success_response({
                "operation_behavior_data": {
                    "id_num": id_num,
                    "view_count": 0,
                    "copy_count": 0,
                    "download_count": 0,
                    "add_count": 0,
                    "revise_count": 0,
                    "delete_count": 0,
                    "behavior_score": 0.0,
                    "created_time": None,
                    "updated_time": None
                }
            })

        data = {
            "id": record.id,
            "id_num": record.id_num,
            "view_count": record.ob_num_view,
            "copy_count": record.ob_num_copy,
            "download_count": record.ob_num_download,
            "add_count": record.ob_num_add,
            "revise_count": record.ob_num_revise,
            "delete_count": record.ob_num_delet,
            "behavior_score": record.calculate_behavior_score(),
            "created_time": record.created_time.isoformat() if record.created_time else None,
            "updated_time": record.updated_time.isoformat() if record.updated_time else None,
        }

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

        # 获取当前用户的身份证号
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        id_num = data.get("id_num", current_user.id_card)

        # 验证目标用户是否存在
        target_user = User.query.filter_by(id_card=id_num).first()
        if not target_user:
            return error_response("目标用户不存在", 400)

        # 查找现有记录
        record = UserOperationBehaviorTracker.query.filter_by(id_num=id_num).first()

        if record:
            # 更新现有记录
            record.ob_num_view += data.get("view_count", 0)
            record.ob_num_copy += data.get("copy_count", 0)
            record.ob_num_download += data.get("download_count", 0)
            record.ob_num_add += data.get("add_count", 0)
            record.ob_num_revise += data.get("revise_count", 0)
            record.ob_num_delet += data.get("delete_count", 0)
            record.updated_time = datetime.utcnow()
        else:
            # 创建新记录
            record = UserOperationBehaviorTracker(
                id=f"behav_{id_num}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                id_num=id_num,
                ob_num_view=data.get("view_count", 0),
                ob_num_copy=data.get("copy_count", 0),
                ob_num_download=data.get("download_count", 0),
                ob_num_add=data.get("add_count", 0),
                ob_num_revise=data.get("revise_count", 0),
                ob_num_delet=data.get("delete_count", 0),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(record)

        db.session.commit()
        return success_response(
            result={
                "id_num": id_num,
                "view_count": record.ob_num_view,
                "copy_count": record.ob_num_copy,
                "download_count": record.ob_num_download,
                "add_count": record.ob_num_add,
                "revise_count": record.ob_num_revise,
                "delete_count": record.ob_num_delet,
                "behavior_score": record.calculate_behavior_score()
            },
            message="操作行为数据更新成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update operation behavior error")
        return server_error_response("更新操作行为数据失败")


# ─────────────────────────── 数据敏感度 ───────────────────────────
@data_mgmt_bp.route("/data-sensitivity/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_data_sensitivity(id_num):
    """获取用户的数据敏感度数据"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 查询用户的数据敏感度数据
        record = UserAccessSensitiveData.query.filter_by(id_num=id_num).first()
        
        if not record:
            return success_response({
                "data_sensitivity_data": {
                    "id_num": id_num,
                    "quasi_identifier_count": 0,
                    "explicit_identifier_count": 0,
                    "low_sensitivity_count": 0,
                    "high_sensitivity_count": 0,
                    "sensitivity_score": 0.0,
                    "created_time": None,
                    "updated_time": None
                }
            })

        data = {
            "id": record.id,
            "id_num": record.id_num,
            "quasi_identifier_count": record.ds_num1,
            "explicit_identifier_count": record.ds_num2,
            "low_sensitivity_count": record.ds_num3,
            "high_sensitivity_count": record.ds_num4,
            "sensitivity_score": record.calculate_sensitivity_score(),
            "created_time": record.created_time.isoformat() if record.created_time else None,
            "updated_time": record.updated_time.isoformat() if record.updated_time else None,
        }

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

        # 获取当前用户的身份证号
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        id_num = data.get("id_num", current_user.id_card)

        # 验证目标用户是否存在
        target_user = User.query.filter_by(id_card=id_num).first()
        if not target_user:
            return error_response("目标用户不存在", 400)

        # 查找现有记录
        record = UserAccessSensitiveData.query.filter_by(id_num=id_num).first()

        if record:
            # 更新现有记录
            record.ds_num1 += data.get("quasi_identifier_count", 0)
            record.ds_num2 += data.get("explicit_identifier_count", 0)
            record.ds_num3 += data.get("low_sensitivity_count", 0)
            record.ds_num4 += data.get("high_sensitivity_count", 0)
            record.updated_time = datetime.utcnow()
        else:
            # 创建新记录
            record = UserAccessSensitiveData(
                id=f"sens_{id_num}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                id_num=id_num,
                ds_num1=data.get("quasi_identifier_count", 0),
                ds_num2=data.get("explicit_identifier_count", 0),
                ds_num3=data.get("low_sensitivity_count", 0),
                ds_num4=data.get("high_sensitivity_count", 0),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(record)

        db.session.commit()
        return success_response(
            result={
                "id_num": id_num,
                "quasi_identifier_count": record.ds_num1,
                "explicit_identifier_count": record.ds_num2,
                "low_sensitivity_count": record.ds_num3,
                "high_sensitivity_count": record.ds_num4,
                "sensitivity_score": record.calculate_sensitivity_score()
            },
            message="数据敏感度数据更新成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update data sensitivity error")
        return server_error_response("更新数据敏感度数据失败")


# ─────────────────────────── 访问时间段 ───────────────────────────
@data_mgmt_bp.route("/access-time/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_access_time(id_num):
    """获取用户的访问时间数据"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 查询用户的访问时间数据
        record = UserAccessTimeTracker.query.filter_by(id_num=id_num).first()
        
        if not record:
            return success_response({
                "access_time_data": {
                    "id_num": id_num,
                    "normal_time_count": 0,
                    "unusual_time_count": 0,
                    "normal_time_ratio": 0.0,
                    "work_time": [],
                    "created_time": None,
                    "updated_time": None
                }
            })

        data = {
            "id": record.id,
            "id_num": record.id_num,
            "normal_time_count": record.ap_num_ni,
            "unusual_time_count": record.ap_num_ui,
            "normal_time_ratio": record.calculate_normal_time_ratio(),
            "work_time": record.get_work_time_list(),
            "created_time": record.created_time.isoformat() if record.created_time else None,
            "updated_time": record.updated_time.isoformat() if record.updated_time else None,
        }

        return success_response({"access_time_data": data})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get access time error")
        return server_error_response("获取访问时间数据失败")


@data_mgmt_bp.route("/access-time", methods=["POST"])
@jwt_required()
def update_access_time():
    """更新访问时间数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        # 获取当前用户的身份证号
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        id_num = data.get("id_num", current_user.id_card)

        # 验证目标用户是否存在
        target_user = User.query.filter_by(id_card=id_num).first()
        if not target_user:
            return error_response("目标用户不存在", 400)

        # 查找现有记录
        record = UserAccessTimeTracker.query.filter_by(id_num=id_num).first()

        if record:
            # 更新现有记录
            record.ap_num_ni += data.get("normal_time_count", 0)
            record.ap_num_ui += data.get("unusual_time_count", 0)
            if "work_time" in data:
                record.set_work_time_list(data["work_time"])
            record.updated_time = datetime.utcnow()
        else:
            # 创建新记录
            record = UserAccessTimeTracker(
                id=f"time_{id_num}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                id_num=id_num,
                ap_num_ni=data.get("normal_time_count", 0),
                ap_num_ui=data.get("unusual_time_count", 0),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            if "work_time" in data:
                record.set_work_time_list(data["work_time"])
            db.session.add(record)

        db.session.commit()
        return success_response(
            result={
                "id_num": id_num,
                "normal_time_count": record.ap_num_ni,
                "unusual_time_count": record.ap_num_ui,
                "normal_time_ratio": record.calculate_normal_time_ratio(),
                "work_time": record.get_work_time_list()
            },
            message="访问时间数据更新成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update access time error")
        return server_error_response("更新访问时间数据失败")


# ─────────────────────────── 访问地点 ───────────────────────────
@data_mgmt_bp.route("/access-location/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_access_location(id_num):
    """获取用户的访问地点数据"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 查询用户的访问地点数据
        record = UserAccessLocationTracker.query.filter_by(id_num=id_num).first()
        
        if not record:
            return success_response({
                "access_location_data": {
                    "id_num": id_num,
                    "normal_location_count": 0,
                    "abnormal_location_count": 0,
                    "normal_location_ratio": 0.0,
                    "created_time": None,
                    "updated_time": None
                }
            })

        data = {
            "id": record.id,
            "id_num": record.id_num,
            "normal_location_count": record.at_num_nd,
            "abnormal_location_count": record.at_num_ad,
            "normal_location_ratio": record.calculate_normal_location_ratio(),
            "created_time": record.created_time.isoformat() if record.created_time else None,
            "updated_time": record.updated_time.isoformat() if record.updated_time else None,
        }

        return success_response({"access_location_data": data})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get access location error")
        return server_error_response("获取访问地点数据失败")


@data_mgmt_bp.route("/access-location", methods=["POST"])
@jwt_required()
def update_access_location():
    """更新访问地点数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        # 获取当前用户的身份证号
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        id_num = data.get("id_num", current_user.id_card)

        # 验证目标用户是否存在
        target_user = User.query.filter_by(id_card=id_num).first()
        if not target_user:
            return error_response("目标用户不存在", 400)

        # 查找现有记录
        record = UserAccessLocationTracker.query.filter_by(id_num=id_num).first()

        if record:
            # 更新现有记录
            record.at_num_nd += data.get("normal_location_count", 0)
            record.at_num_ad += data.get("abnormal_location_count", 0)
            record.updated_time = datetime.utcnow()
        else:
            # 创建新记录
            record = UserAccessLocationTracker(
                id=f"loc_{id_num}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                id_num=id_num,
                at_num_nd=data.get("normal_location_count", 0),
                at_num_ad=data.get("abnormal_location_count", 0),
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow()
            )
            db.session.add(record)

        db.session.commit()
        return success_response(
            result={
                "id_num": id_num,
                "normal_location_count": record.at_num_nd,
                "abnormal_location_count": record.at_num_ad,
                "normal_location_ratio": record.calculate_normal_location_ratio()
            },
            message="访问地点数据更新成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update access location error")
        return server_error_response("更新访问地点数据失败")


# ─────────────────────────── 用户日志 ───────────────────────────
@data_mgmt_bp.route("/user-logs/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_logs(id_num):
    """获取用户访问日志"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 获取分页参数
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        operation_type = request.args.get("operation_type")
        access_status = request.args.get("access_status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        # 构建查询
        query = UserLogs.query.filter_by(id_num=id_num)

        if operation_type:
            query = query.filter(UserLogs.operation_type == operation_type)
        if access_status:
            query = query.filter(UserLogs.access_status == access_status)
        if start_date:
            query = query.filter(UserLogs.access_timestamp >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(UserLogs.access_timestamp <= datetime.fromisoformat(end_date))

        # 分页查询
        pagination = query.order_by(UserLogs.access_timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        logs = [log.to_dict() for log in pagination.items]

        return success_response({
            "logs": logs,
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
        current_app.logger.exception("Get user logs error")
        return server_error_response("获取用户日志失败")


@data_mgmt_bp.route("/user-logs", methods=["POST"])
@jwt_required()
def create_user_log():
    """创建用户访问日志"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空", 400)

        # 获取当前用户的身份证号
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        # 必需字段验证
        required_fields = ["operation_type", "target_data_sensitivity", "access_status"]
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必需字段: {field}", 400)

        id_num = data.get("id_num", current_user.id_card)
        
        # 验证目标用户是否存在
        target_user = User.query.filter_by(id_card=id_num).first()
        if not target_user:
            return error_response("目标用户不存在", 400)

        # 创建新的访问日志
        log = UserLogs(
            id=f"log_{id_num}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            id_num=id_num,
            access_timestamp=datetime.utcnow(),
            access_ip=request.remote_addr or data.get("access_ip", "127.0.0.1"),
            operation_type=data["operation_type"],
            target_data_sensitivity=data["target_data_sensitivity"],
            access_status=data["access_status"],
            created_time=datetime.utcnow()
        )

        # 设置疾病编码
        if "target_disease_codes" in data:
            log.set_disease_codes_list(data["target_disease_codes"])

        db.session.add(log)
        db.session.commit()

        return success_response(
            result=log.to_dict(),
            message="访问日志创建成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create user log error")
        return server_error_response("创建访问日志失败")


# ─────────────────────────── 用户常用IP ───────────────────────────
@data_mgmt_bp.route("/user-ips/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_ips(id_num):
    """获取用户常用IP列表"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 查询用户常用IP
        user_ips = UserIps.query.filter_by(id_num=id_num).order_by(
            UserIps.access_count.desc()
        ).all()

        ips = [ip.to_dict() for ip in user_ips]

        return success_response({"user_ips": ips})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get user IPs error")
        return server_error_response("获取用户常用IP失败")


# ─────────────────────────── 病种数据项 ───────────────────────────
@data_mgmt_bp.route("/disease-data-items", methods=["GET"])
@jwt_required()
def get_disease_data_items():
    """获取病种数据项列表"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        disease_code = request.args.get("disease_code")

        query = DiseaseDataItem.query

        if disease_code:
            query = query.filter(DiseaseDataItem.disease_code.like(f"%{disease_code}%"))

        pagination = query.order_by(DiseaseDataItem.created_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        items = [item.to_dict() for item in pagination.items]

        return success_response({
            "disease_data_items": items,
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
        current_app.logger.exception("Get disease data items error")
        return server_error_response("获取病种数据项失败")


@data_mgmt_bp.route("/disease-data-items/<disease_code>", methods=["GET"])
@jwt_required()
def get_disease_data_item(disease_code):
    """获取指定病种的数据项"""
    try:
        item = DiseaseDataItem.query.filter_by(disease_code=disease_code).first()
        if not item:
            return not_found_response("病种数据项不存在")

        return success_response({"disease_data_item": item.to_dict()})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get disease data item error")
        return server_error_response("获取病种数据项失败")


# ─────────────────────────── 信任值计算 ───────────────────────────
@data_mgmt_bp.route("/trust-score/user/<id_num>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def get_user_trust_score(id_num):
    """计算用户信任值"""
    try:
        # 验证用户是否存在
        user = User.query.filter_by(id_card=id_num).first()
        if not user:
            return not_found_response("用户不存在")

        # 获取目标疾病编码（可选）
        target_disease_codes = request.args.getlist("disease_codes")

        # 创建信任值计算器
        calculator = TrustCalculator(id_num)
        
        # 计算信任值
        trust_result = calculator.calculate_trust_score(target_disease_codes)

        return success_response({"trust_result": trust_result})

    except Exception:  # pragma: no cover
        current_app.logger.exception("Calculate trust score error")
        return server_error_response("计算信任值失败")


@data_mgmt_bp.route("/trust-evaluation", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")
def evaluate_trust():
    """评估用户信任度（批量）"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        id_nums = data.get("id_nums", [])
        target_disease_codes = data.get("target_disease_codes", [])
        threshold = data.get("threshold", 0.7)

        if not id_nums:
            return error_response("用户身份证号列表不能为空", 400)

        results = []
        for id_num in id_nums:
            # 验证用户是否存在
            user = User.query.filter_by(id_card=id_num).first()
            if not user:
                results.append({
                    "id_num": id_num,
                    "error": "用户不存在"
                })
                continue

            try:
                # 计算信任值
                calculator = TrustCalculator(id_num)
                trust_result = calculator.calculate_trust_score(target_disease_codes)
                
                # 判断是否可信
                is_trusted = TrustCalculator.is_trusted(trust_result["trust_score"], threshold)
                
                results.append({
                    "id_num": id_num,
                    "trust_score": trust_result["trust_score"],
                    "is_trusted": is_trusted,
                    "components": trust_result["components"],
                    "calculated_at": trust_result["calculated_at"]
                })
            except Exception as e:
                results.append({
                    "id_num": id_num,
                    "error": str(e)
                })

        return success_response({
            "evaluation_results": results,
            "threshold": threshold,
            "total_users": len(id_nums),
            "trusted_users": sum(1 for r in results if r.get("is_trusted", False))
        })

    except Exception:  # pragma: no cover
        current_app.logger.exception("Evaluate trust error")
        return server_error_response("评估信任度失败")
