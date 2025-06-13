"""
用户认证相关接口（JWT）
--------------------------------
依赖：
    - Flask‑JWT‑Extended
    - utils.extensions.db  (SQLAlchemy 实例)
模型：
    - User  (password 字段保存哈希)
    - Role  (role_code / role_name)
    - UserRoleRelation (一对一；每名用户只应有 0‑1 条记录)
"""
from datetime import timedelta

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from utils.extensions import db
from modules.auth.models import User, Role, UserRoleRelation

auth_bp = Blueprint("auth", __name__)


# ---------- 内部辅助 ----------
def _get_user_role(user_id: int):
    """返回 (role_code, role_name) 或 (None, None)"""
    rel = UserRoleRelation.query.filter_by(user_id=user_id).first()
    if not rel:
        return None, None
    role = Role.query.get(rel.role_id)
    return (role.role_code, role.role_name) if role else (None, None)

def _get_user_group(user_id: int):
    """返回 group_name 或 None """
    from modules.auth.models import Group, UserGroupRelation

    rel = UserGroupRelation.query.filter_by(user_id=user_id).first()
    if not rel:
        return None
    group = Group.query.get(rel.group_id)
    return group.group_name if group else None



# ---------- 登录 ----------
@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录，成功后签发 24h JWT"""
    try:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "用户名或密码错误"}), 401

        if not user.enable:
            return jsonify({"error": "用户已被禁用"}), 403

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

        return (
            jsonify(
                {
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
            ),
            200,
        )
    except Exception as e:
        current_app.logger.exception("Login error")
        return jsonify({"error": "登录失败"}), 500


# ---------- 注册 ----------
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    用户注册  
    前端需提交：username / password / name / age / gender / role  
    其中 role 可填角色代码 (PATIENT 等) 或角色名称 (患者 等)。
    """
    try:
        data = request.get_json(silent=True) or {}

        # 基本字段校验
        required = ["username", "password", "name", "age", "gender", "role"]
        miss = [f for f in required if not data.get(f)]
        if miss:
            return jsonify({"error": f"字段缺失: {', '.join(miss)}"}), 400

        username = data["username"].strip()
        password = data["password"].strip()
        name = data["name"].strip()
        age = int(data["age"])
        gender = data["gender"].strip()
        role_input = data["role"].strip()  # 可为中文或代码

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "用户名已存在"}), 400

        # 查找角色（兼容 role_code 或 role_name）
        role = Role.query.filter(
            (Role.role_code == role_input) | (Role.role_name == role_input)
        ).first()
        if not role:
            return jsonify({"error": "无效的角色"}), 400

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
        db.session.flush()  # 先拿到 user.id

        # 绑定用户角色（确保唯一）
        rel = UserRoleRelation(user_id=user.id, role_id=role.id)
        db.session.add(rel)

        db.session.commit()
        return (
            jsonify(
                {
                    "message": "注册成功",
                    "user": {"id": user.id, "username": user.username},
                }
            ),
            201,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Register error")
        return jsonify({"error": "注册失败"}), 500


# ---------- 获取个人信息 ----------
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """已登录用户查询自己的资料"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404

        role_code, role_name = _get_user_role(user.id)

        return (
            jsonify(
                {
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
            ),
            200,
        )
    except Exception:
        current_app.logger.exception("Get profile error")
        return jsonify({"error": "获取用户信息失败"}), 500


# ---------- 修改密码 ----------
@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        old_pwd = data.get("old_password", "").strip()
        new_pwd = data.get("new_password", "").strip()

        if not old_pwd or not new_pwd:
            return jsonify({"error": "旧密码和新密码不能为空"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404

        if not check_password_hash(user.password, old_pwd):
            return jsonify({"error": "旧密码错误"}), 400

        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        return jsonify({"message": "密码修改成功"}), 200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Change password error")
        return jsonify({"error": "密码修改失败"}), 500


# ---------- 登出 ----------
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    登出占位接口  
    若后续实现 token 拉黑，可在此处插入黑名单逻辑。
    """
    return jsonify({"message": "登出成功"}), 200
