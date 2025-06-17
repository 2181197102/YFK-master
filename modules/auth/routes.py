"""
用户认证相关接口（JWT）
--------------------------------
依赖：
    - Flask‑JWT‑Extended
    - utils.extensions.db  (SQLAlchemy 实例)
模型：
    - User               (password 字段保存哈希)
    - Role               (role_code / role_name)
    - UserRoleRelation   (一对一；每名用户只应有 0‑1 条记录)
    - Group              (医院/机构)
    - UserGroupRelation  (一对一；可选)
"""

from datetime import timedelta
from functools import wraps

from flask import Blueprint, current_app, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from utils.extensions import db
from utils.response import (
    success_response,
    error_response,
    unauthorized_response,
    forbidden_response,
    not_found_response,
    server_error_response,
)

from modules.auth.models import User, Role, UserRoleRelation

# ────────────────────────────── Blueprint ──────────────────────────────
auth_bp = Blueprint("auth", __name__)

# ────────────────────────────── 角色常量 ──────────────────────────────
ADMIN = "ADMIN"
PATIENT = "PATIENT"
FAMILY_DOCTOR = "FAMILY_DOCTOR"
ATTENDING_DOCTOR = "ATTENDING_DOCTOR"
CROSS_HOSPITAL_DOCTOR = "CROSS_HOSPITAL_DOCTOR"
EMERGENCY_DOCTOR = "EMERGENCY_DOCTOR"
RESEARCHER = "RESEARCHER"

DOCTOR_ROLES = {
    FAMILY_DOCTOR,
    ATTENDING_DOCTOR,
    CROSS_HOSPITAL_DOCTOR,
    EMERGENCY_DOCTOR,
}
PATIENT_OR_DOCTOR_ROLES = DOCTOR_ROLES | {PATIENT}
RESEARCHER_OR_ADMIN_ROLES = {RESEARCHER, ADMIN}

# ────────────────────────────── 通用角色装饰器 ──────────────────────────────
def role_required(*allowed_roles: str):
    """
    角色权限装饰器，只检查 JWT.claims 中的 ``role_code``。
    用法:
        @role_required(ADMIN, RESEARCHER)
        def some_view(): ...
    """
    allowed_set = set(allowed_roles)

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                role = get_jwt().get("role_code")
                current_app.logger.debug(
                    f"访问者角色: {role}, 允许角色: {allowed_set}"
                )

                if role not in allowed_set:
                    return forbidden_response("权限不足")

                return fn(*args, **kwargs)

            except Exception:  # pragma: no cover
                current_app.logger.exception("权限验证失败")
                return server_error_response("权限验证失败")

        return wrapper

    return decorator


# 语义化别名
def admin_required(fn):
    return role_required(ADMIN)(fn)


def doctor_only(fn):
    return role_required(*DOCTOR_ROLES)(fn)


def patient_or_doctor(fn):
    return role_required(*PATIENT_OR_DOCTOR_ROLES)(fn)


def researcher_or_admin(fn):
    return role_required(*RESEARCHER_OR_ADMIN_ROLES)(fn)


# ────────────────────────────── 内部辅助函数 ──────────────────────────────
def _get_user_role(user_id: int):
    """返回 (role_code, role_name) 或 (None, None)"""
    rel = UserRoleRelation.query.filter_by(user_id=user_id).first()
    if not rel:
        return None, None
    role = Role.query.get(rel.role_id)
    return (role.role_code, role.role_name) if role else (None, None)


def _get_user_group(user_id: int):
    """返回 group_name 或 None"""
    from modules.auth.models import Group, UserGroupRelation

    rel = UserGroupRelation.query.filter_by(user_id=user_id).first()
    if not rel:
        return None
    group = Group.query.get(rel.group_id)
    return group.group_name if group else None


# ────────────────────────────── 登录 ──────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录，成功后签发 24 h JWT"""
    try:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        current_app.logger.info("用户 %s 尝试登录", username)

        if not username or not password:
            return error_response("用户名和密码不能为空", 400)

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return unauthorized_response("用户名或密码错误")

        if not user.enable:
            return forbidden_response("用户已被禁用")

        role_code, role_name = _get_user_role(user.id)
        group_name = _get_user_group(user.id)

        additional_claims = {
            "user_id": user.id,
            "username": user.username,
            "role_code": role_code,
            "group_name": group_name,
        }
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24),
            additional_claims=additional_claims,
        )

        result = {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "age": user.age,
                "gender": user.gender,
                "role_code": role_code,
                "role_name": role_name,
                "group_name": group_name,
            },
        }
        return success_response(result, "登录成功")

    except Exception:  # pragma: no cover
        current_app.logger.exception("Login error")
        return server_error_response("登录失败")


# ────────────────────────────── 注册 ──────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    用户注册
    前端需提交：username / password / name / age / gender / role
    其中 role 可填角色代码 (PATIENT 等) 或角色名称 (患者 等)。
    """
    try:
        data = request.get_json(silent=True) or {}

        required = ["username", "password", "name", "age", "gender", "role"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return error_response(f"字段缺失: {', '.join(missing)}", 400)

        username = data["username"].strip()
        password = data["password"].strip()
        name = data["name"].strip()
        age = int(data["age"])
        gender = data["gender"].strip()
        role_input = data["role"].strip()  # 可能是中文或代码

        if User.query.filter_by(username=username).first():
            return error_response("用户名已存在", 400)

        # 禁止注册管理员
        admin_aliases = {"ADMIN", "管理员"}
        if role_input.upper() in admin_aliases or role_input in admin_aliases:
            return forbidden_response("禁止注册管理员账号")

        # 查找角色（兼容 role_code / role_name）
        role = Role.query.filter(
            (Role.role_code == role_input) | (Role.role_name == role_input)
        ).first()
        if not role:
            return error_response("无效的角色", 400)

        # 创建用户
        user = User(
            username=username,
            name=name,
            age=age,
            gender=gender,
            enable=True,
        )
        user.password = generate_password_hash(password)
        db.session.add(user)
        db.session.flush()  # 获取 user.id

        # 绑定唯一角色
        rel = UserRoleRelation(user_id=user.id, role_id=role.id)
        db.session.add(rel)

        db.session.commit()

        result = {"user": {"id": user.id, "username": user.username}}
        return success_response(result, "注册成功", code=201)

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Register error")
        return server_error_response("注册失败")


# ────────────────────────────── 获取个人信息 ──────────────────────────────
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """已登录用户查询自己的资料"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        role_code, role_name = _get_user_role(user.id)

        result = {
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "age": user.age,
                "gender": user.gender,
                "enable": user.enable,
                "role_code": role_code,
                "role_name": role_name,
                "created_time": user.created_time.isoformat()
                if user.created_time
                else None,
            }
        }
        return success_response(result, "获取成功")

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get profile error")
        return server_error_response("获取用户信息失败")


# ────────────────────────────── 修改密码 ──────────────────────────────
@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        old_pwd = data.get("old_password", "").strip()
        new_pwd = data.get("new_password", "").strip()

        if not old_pwd or not new_pwd:
            return error_response("旧密码和新密码不能为空", 400)

        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        if not check_password_hash(user.password, old_pwd):
            return error_response("旧密码错误", 400)

        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        return success_response(message="密码修改成功")

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Change password error")
        return server_error_response("密码修改失败")


# ────────────────────────────── 登出 ──────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    占位登出接口
    若后续实现 Token 拉黑，可在此处插入黑名单逻辑。
    """
    return success_response(message="登出成功")
