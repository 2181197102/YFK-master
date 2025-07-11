"""
系统常量配置接口
--------------------------------
依赖：
    - flask_jwt_extended
    - utils.extensions.db
    - utils.response         (统一响应)
    - modules.auth.routes    (role_required / admin_required 等装饰器)

模型：
    - SystemConfig
"""
# ────────────────────────────── 导入依赖 ──────────────────────────────
from datetime import datetime
import json

from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from utils.extensions import db
from utils.response import (
    success_response,
    error_response,
    forbidden_response,
    not_found_response,
    server_error_response,
)

# 角色装饰器可直接复用 auth 模块里的
from modules.auth.routes import admin_required, role_required
from modules.system_config.models import SystemConfig

# ────────────────────────────── Blueprint ──────────────────────────────
sys_cfg_bp = Blueprint("system_config", __name__)


# ────────────────────────────── 工具函数 ──────────────────────────────
def _mask_value(cfg: SystemConfig, show_sensitive: bool = False):
    """
    根据敏感标志决定是否返回真实 value。
    若 value_type == password 且非管理员，则返回 '******'。
    管理员（show_sensitive=True）时显示真实密码。
    """
    if cfg.value_type == "password":
        if show_sensitive:
            return cfg.value or ""
        else:
            return "******"
    return cfg.value if (show_sensitive or not cfg.is_sensitive) else "******"



def _config_to_dict(cfg: SystemConfig, *, show_sensitive=False):
    return {
        "id": cfg.id,
        "key": cfg.key,
        "value": _mask_value(cfg, show_sensitive),
        "value_type": cfg.value_type,
        "is_sensitive": cfg.is_sensitive,
        "read_only": cfg.read_only,
        "description": cfg.description,
        "created_time": cfg.created_time.isoformat() if cfg.created_time else None,
        "updated_time": cfg.updated_time.isoformat() if cfg.updated_time else None,
    }


def _find_config(identifier: str | int):
    """支持 id (int) 或 key (str)"""
    if isinstance(identifier, int) or identifier.isdigit():
        return SystemConfig.query.get(int(identifier))
    return SystemConfig.query.filter_by(key=str(identifier)).first()


# ────────────────────────────── 列表 & 详情 ──────────────────────────────
@sys_cfg_bp.route("/configs", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")  # 仅管理员/研究员可查看全部配置
def list_configs():
    try:
        # 分页参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        pagination = (
            SystemConfig.query
            .order_by(SystemConfig.id.asc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        result = {
            "items": [
                _config_to_dict(cfg, show_sensitive=False) for cfg in pagination.items
            ],
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
        }
        return success_response(result, "获取成功")
    except Exception:  # pragma: no cover
        current_app.logger.exception("List configs error")
        return server_error_response("获取配置失败")


@sys_cfg_bp.route("/configs/<identifier>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "RESEARCHER")  # 仅管理员/研究员可查看具体某一个详细配置
def get_config(identifier):
    cfg = _find_config(identifier)
    if not cfg:
        return not_found_response("配置不存在")
    show_sensitive = False if cfg.is_sensitive else True
    return success_response(
        result={"config": _config_to_dict(cfg, show_sensitive=show_sensitive)},
        message="获取成功",
    )


# ────────────────────────────── 新增 ──────────────────────────────
@sys_cfg_bp.route("/configs", methods=["POST"])
@jwt_required()
@admin_required
def create_config():
    try:
        data = request.get_json(silent=True) or {}
        key = data.get("key", "").strip()
        value = data.get("value")
        value_type = data.get("value_type", "string")
        description = data.get("description", "")
        is_sensitive = bool(data.get("is_sensitive", False))
        read_only = bool(data.get("read_only", False))

        if not key or value is None:
            return error_response("key 和 value 不能为空", 400)

        cfg = SystemConfig(
            key=key,
            description=description,
            is_sensitive=is_sensitive,
            read_only=read_only,
            created_time=datetime.utcnow(),
            updated_time=datetime.utcnow(),
        )

        if value_type == "password":
            cfg.set_password(str(value))
        else:
            cfg.value = json.dumps(value) if value_type == "json" else str(value)
            cfg.value_type = value_type

        db.session.add(cfg)
        db.session.commit()

        return success_response(
            result={"config": _config_to_dict(cfg, show_sensitive=False)},
            message="创建成功",
            code=201,
        )

    except IntegrityError:
        db.session.rollback()
        return error_response("key 已存在，请使用其他 key", 400)
    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create config error")
        return server_error_response("创建配置失败")


# ────────────────────────────── 更新 (POST /configs/update) ──────────────────────────────
@sys_cfg_bp.route("/configs/update", methods=["POST"])
@jwt_required()
@admin_required
def update_config():
    """
    请求体必须包含 identifier：可以是 id (int) 或 key (str)
    其他可选字段：value / description / is_sensitive / read_only
    示例:
    {
        "id": 3,
        "value": "new_value",
        "description": "修改描述",
        "is_sensitive": false,
        "read_only": false
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        # ① 解析 identifier（id 优先，其次 key）
        identifier = data.get("id") if "id" in data else data.get("key")
        if identifier is None:
            return error_response("缺少 id 或 key 标识符", 400)

        cfg = _find_config(identifier)
        if not cfg:
            return not_found_response("配置不存在")

        if cfg.read_only:
            return forbidden_response("该配置为只读，禁止修改")

        # ② 更新字段
        for field in ("description", "is_sensitive", "read_only"):
            if field in data:
                setattr(cfg, field, data[field])

        if "value" in data:
            new_val = data["value"]
            if cfg.value_type == "password":
                cfg.set_password(str(new_val))
            elif cfg.value_type == "json":
                cfg.value = json.dumps(new_val)
            else:
                cfg.value = str(new_val)

        cfg.updated_time = datetime.utcnow()
        db.session.commit()

        return success_response(
            result={"config": _config_to_dict(cfg, show_sensitive=False)},
            message="更新成功",
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Update config error")
        return server_error_response("更新配置失败")



# ────────────────────────────── 删除 ──────────────────────────────
@sys_cfg_bp.route("/configs/<identifier>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_config(identifier):
    try:
        cfg = _find_config(identifier)
        if not cfg:
            return not_found_response("配置不存在")
        if cfg.read_only:
            return forbidden_response("该配置为只读，禁止删除")

        db.session.delete(cfg)
        db.session.commit()
        return success_response(message="删除成功")
    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Delete config error")
        return server_error_response("删除配置失败")


# ────────────────────────────── 密码校验 ──────────────────────────────
@sys_cfg_bp.route("/verify-auth-password", methods=["POST"])
def verify_auth_password():
    """
    校验授权密码。仅检查 SystemConfig.key == 'AUTH_PASSWORD' 的记录。
    不要求登录，以便游客/前端在登录前进行授权。
    """
    try:
        data = request.get_json(silent=True) or {}
        raw_pwd = str(data.get("password", "")).strip()
        if not raw_pwd:
            return error_response("密码不能为空", 400)

        cfg = SystemConfig.query.filter_by(key="AUTH_PASSWORD").first()
        if not cfg:
            return not_found_response("未初始化授权密码")

        if cfg.check_password(raw_pwd):
            return success_response(message="密码验证通过")
        return error_response("授权密码错误")
    except Exception:  # pragma: no cover
        current_app.logger.exception("Verify auth password error")
        return server_error_response("密码校验失败")
