# modules/user_management/routes.py
from datetime import datetime

from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash

from modules.auth.models import (
    db,
    User,
    Role,
    UserRoleRelation,
    Group,
    UserGroupRelation,
)
from modules.auth.decorators import admin_required

from utils.response import (
    success_response,
    error_response,
    not_found_response,
    server_error_response,
)

user_mgmt_bp = Blueprint("user_management", __name__)

# ─────────────────────────── 用户列表 ───────────────────────────
@user_mgmt_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        role_filter = request.args.get("role")
        group_filter = request.args.get("group")
        search = request.args.get("search")

        query = User.query

        if search:
            query = query.filter(
                db.or_(User.username.contains(search), User.name.contains(search))
            )

        if role_filter:
            query = (
                query.join(UserRoleRelation)
                .join(Role)
                .filter(Role.role_name == role_filter)
            )

        if group_filter:
            query = (
                query.join(UserGroupRelation)
                .join(Group)
                .filter(Group.group_name == group_filter)
            )

        users = query.paginate(page=page, per_page=per_page, error_out=False)

        users_list = []
        for user in users.items:
            user_roles = (
                db.session.query(Role)
                .join(UserRoleRelation)
                .filter(UserRoleRelation.user_id == user.id)
                .all()
            )
            roles = [
                {"id": r.id, "role_code": r.role_code, "role_name": r.role_name}
                for r in user_roles
            ]

            user_groups = (
                db.session.query(
                    Group, UserGroupRelation.type, UserGroupRelation.enable
                )
                .join(UserGroupRelation)
                .filter(UserGroupRelation.user_id == user.id)
                .all()
            )
            groups = [
                {
                    "id": g.id,
                    "group_name": g.group_name,
                    "type": t,
                    "enable": e,
                }
                for g, t, e in user_groups
            ]

            u_dict = user.to_dict()
            u_dict["roles"] = roles
            u_dict["groups"] = groups
            users_list.append(u_dict)

        result = {
            "users": users_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": users.total,
                "pages": users.pages,
                "has_next": users.has_next,
                "has_prev": users.has_prev,
            },
        }
        return success_response(result)

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get users error")
        return server_error_response("获取用户列表失败")


# ─────────────────────────── 单个用户 ───────────────────────────
@user_mgmt_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        user_roles = (
            db.session.query(Role)
            .join(UserRoleRelation)
            .filter(UserRoleRelation.user_id == user.id)
            .all()
        )
        roles = [
            {"id": r.id, "role_code": r.role_code, "role_name": r.role_name}
            for r in user_roles
        ]

        user_groups = (
            db.session.query(Group, UserGroupRelation.type, UserGroupRelation.enable)
            .join(UserGroupRelation)
            .filter(UserGroupRelation.user_id == user.id)
            .all()
        )
        groups = [
            {"id": g.id, "group_name": g.group_name, "type": t, "enable": e}
            for g, t, e in user_groups
        ]

        u_dict = user.to_dict()
        u_dict["roles"] = roles
        u_dict["groups"] = groups

        return success_response({"user": u_dict})

    except Exception:
        current_app.logger.exception("Get user error")
        return server_error_response("获取用户信息失败")


# ─────────────────────────── 创建用户 ───────────────────────────
@user_mgmt_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        required = ["username", "password", "name", "age", "gender"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return error_response(f"字段缺失: {', '.join(missing)}", 400)

        if User.query.filter_by(username=data["username"]).first():
            return error_response("用户名已存在", 400)

        user = User(
            username=data["username"],
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            enable=data.get("enable", True),
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        # 角色
        for r in data.get("roles", []):
            role_id = r.get("role_id") if isinstance(r, dict) else r
            role = Role.query.get(role_id)
            if role:
                db.session.add(UserRoleRelation(user_id=user.id, role_id=role.id))

        # 组
        for g in data.get("groups", []):
            if isinstance(g, dict):
                group_id = g.get("group_id")
                g_type = g.get("type", "base")
                g_enable = g.get("enable", True)
            else:
                group_id, g_type, g_enable = g, "base", True

            group = Group.query.get(group_id)
            if group:
                db.session.add(
                    UserGroupRelation(
                        user_id=user.id,
                        group_id=group.id,
                        type=g_type,
                        enable=g_enable,
                    )
                )

        db.session.commit()
        return success_response(
            {"user": user.to_dict()}, "用户创建成功", code=201
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Create user error")
        return server_error_response("创建用户失败")


# ─────────────────────────── 更新用户 ───────────────────────────
@user_mgmt_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        if "username" in data:
            if (
                User.query.filter(
                    User.username == data["username"], User.id != user_id
                ).first()
            ):
                return error_response("用户名已存在", 400)
            user.username = data["username"]

        user.name = data.get("name", user.name)
        user.age = data.get("age", user.age)
        user.gender = data.get("gender", user.gender)
        user.enable = data.get("enable", user.enable)

        if data.get("password"):
            user.set_password(data["password"])

        # 角色
        if "roles" in data:
            UserRoleRelation.query.filter_by(user_id=user_id).delete()
            for r in data["roles"]:
                role_id = r.get("role_id") if isinstance(r, dict) else r
                role = Role.query.get(role_id)
                if role:
                    db.session.add(
                        UserRoleRelation(user_id=user_id, role_id=role.id)
                    )

        # 组
        if "groups" in data:
            UserGroupRelation.query.filter_by(user_id=user_id).delete()
            for g in data["groups"]:
                if isinstance(g, dict):
                    group_id = g.get("group_id")
                    g_type = g.get("type", "base")
                    g_enable = g.get("enable", True)
                else:
                    group_id, g_type, g_enable = g, "base", True
                group = Group.query.get(group_id)
                if group:
                    db.session.add(
                        UserGroupRelation(
                            user_id=user_id,
                            group_id=group.id,
                            type=g_type,
                            enable=g_enable,
                        )
                    )

        user.updated_time = datetime.utcnow()
        db.session.commit()

        return success_response({"user": user.to_dict()}, "用户更新成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Update user error")
        return server_error_response("更新用户失败")


# ─────────────────────────── 删除用户 ───────────────────────────
@user_mgmt_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        UserRoleRelation.query.filter_by(user_id=user_id).delete()
        UserGroupRelation.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()

        return success_response(message="用户删除成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Delete user error")
        return server_error_response("删除用户失败")


# ======================= 角色管理 =======================
@user_mgmt_bp.route("/roles", methods=["GET"])
@admin_required
def get_roles():
    try:
        roles = Role.query.all()
        return success_response({"roles": [r.to_dict() for r in roles]})
    except Exception:
        current_app.logger.exception("Get roles error")
        return server_error_response("获取角色列表失败")


@user_mgmt_bp.route("/roles", methods=["POST"])
@admin_required
def create_role():
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        if not data.get("role_code") or not data.get("role_name"):
            return error_response("role_code 和 role_name 不能为空", 400)

        if Role.query.filter_by(role_code=data["role_code"]).first():
            return error_response("角色编码已存在", 400)

        role = Role(
            role_code=data["role_code"],
            role_name=data["role_name"],
            description=data.get("description", ""),
        )
        db.session.add(role)
        db.session.commit()

        return success_response({"role": role.to_dict()}, "角色创建成功", code=201)

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Create role error")
        return server_error_response("创建角色失败")


@user_mgmt_bp.route("/roles/<int:role_id>", methods=["PUT"])
@admin_required
def update_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            return not_found_response("角色不存在")

        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        if "role_code" in data:
            if (
                Role.query.filter(
                    Role.role_code == data["role_code"], Role.id != role_id
                ).first()
            ):
                return error_response("角色编码已存在", 400)
            role.role_code = data["role_code"]

        role.role_name = data.get("role_name", role.role_name)
        role.description = data.get("description", role.description)
        role.updated_time = datetime.utcnow()
        db.session.commit()

        return success_response({"role": role.to_dict()}, "角色更新成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Update role error")
        return server_error_response("更新角色失败")


@user_mgmt_bp.route("/roles/<int:role_id>", methods=["DELETE"])
@admin_required
def delete_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            return not_found_response("角色不存在")

        if UserRoleRelation.query.filter_by(role_id=role_id).count() > 0:
            return error_response("该角色下还有用户，无法删除", 400)

        db.session.delete(role)
        db.session.commit()
        return success_response(message="角色删除成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Delete role error")
        return server_error_response("删除角色失败")


# ======================= 组管理 =======================
@user_mgmt_bp.route("/groups", methods=["GET"])
@admin_required
def get_groups():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search")

        query = Group.query
        if search:
            query = query.filter(Group.group_name.contains(search))

        groups = query.paginate(page=page, per_page=per_page, error_out=False)

        groups_list = []
        for g in groups.items:
            g_dict = g.to_dict()
            g_dict["user_count"] = UserGroupRelation.query.filter_by(
                group_id=g.id, enable=True
            ).count()
            groups_list.append(g_dict)

        result = {
            "groups": groups_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": groups.total,
                "pages": groups.pages,
                "has_next": groups.has_next,
                "has_prev": groups.has_prev,
            },
        }
        return success_response(result)

    except Exception:
        current_app.logger.exception("Get groups error")
        return server_error_response("获取组列表失败")


@user_mgmt_bp.route("/groups", methods=["POST"])
@admin_required
def create_group():
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        if not data.get("group_name"):
            return error_response("group_name 不能为空", 400)

        if Group.query.filter_by(group_name=data["group_name"]).first():
            return error_response("组名已存在", 400)

        group = Group(group_name=data["group_name"], enable=data.get("enable", True))
        db.session.add(group)
        db.session.commit()

        return success_response({"group": group.to_dict()}, "组创建成功", code=201)

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Create group error")
        return server_error_response("创建组失败")


@user_mgmt_bp.route("/groups/<int:group_id>", methods=["PUT"])
@admin_required
def update_group(group_id):
    try:
        group = Group.query.get(group_id)
        if not group:
            return not_found_response("组不存在")

        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        if "group_name" in data:
            if (
                Group.query.filter(
                    Group.group_name == data["group_name"], Group.id != group_id
                ).first()
            ):
                return error_response("组名已存在", 400)
            group.group_name = data["group_name"]

        group.enable = data.get("enable", group.enable)
        group.updated_time = datetime.utcnow()
        db.session.commit()

        return success_response({"group": group.to_dict()}, "组更新成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Update group error")
        return server_error_response("更新组失败")


@user_mgmt_bp.route("/groups/<int:group_id>", methods=["DELETE"])
@admin_required
def delete_group(group_id):
    try:
        group = Group.query.get(group_id)
        if not group:
            return not_found_response("组不存在")

        if UserGroupRelation.query.filter_by(group_id=group_id).count() > 0:
            return error_response("该组下还有用户，无法删除", 400)

        db.session.delete(group)
        db.session.commit()
        return success_response(message="组删除成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Delete group error")
        return server_error_response("删除组失败")


@user_mgmt_bp.route("/groups/<int:group_id>/users", methods=["GET"])
@admin_required
def get_group_users(group_id):
    try:
        group = Group.query.get(group_id)
        if not group:
            return not_found_response("组不存在")

        relations = (
            db.session.query(User, UserGroupRelation.type, UserGroupRelation.enable)
            .join(UserGroupRelation)
            .filter(UserGroupRelation.group_id == group_id)
            .all()
        )

        users_list = []
        for user, r_type, r_enable in relations:
            u_dict = user.to_dict()
            u_dict["relation_type"] = r_type
            u_dict["relation_enable"] = r_enable
            users_list.append(u_dict)

        result = {"group": group.to_dict(), "users": users_list}
        return success_response(result)

    except Exception:
        current_app.logger.exception("Get group users error")
        return server_error_response("获取组用户失败")


# ======================= 用户角色关系 =======================
@user_mgmt_bp.route("/users/<int:user_id>/roles", methods=["POST"])
@admin_required
def assign_role(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        data = request.get_json()
        if not data or "role_id" not in data:
            return error_response("role_id 不能为空", 400)

        role = Role.query.get(data["role_id"])
        if not role:
            return not_found_response("角色不存在")

        if UserRoleRelation.query.filter_by(
            user_id=user_id, role_id=role.id
        ).first():
            return error_response("用户已拥有该角色", 400)

        db.session.add(UserRoleRelation(user_id=user_id, role_id=role.id))
        db.session.commit()
        return success_response(message="角色分配成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Assign role error")
        return server_error_response("角色分配失败")


@user_mgmt_bp.route("/users/<int:user_id>/roles/<int:role_id>", methods=["DELETE"])
@admin_required
def remove_role(user_id, role_id):
    try:
        relation = UserRoleRelation.query.filter_by(
            user_id=user_id, role_id=role_id
        ).first()
        if not relation:
            return not_found_response("用户角色关联不存在")

        db.session.delete(relation)
        db.session.commit()
        return success_response(message="角色移除成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Remove role error")
        return server_error_response("角色移除失败")


# ======================= 用户组关系 =======================
@user_mgmt_bp.route("/users/<int:user_id>/groups", methods=["POST"])
@admin_required
def assign_group(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return not_found_response("用户不存在")

        data = request.get_json()
        if not data or "group_id" not in data:
            return error_response("group_id 不能为空", 400)

        group = Group.query.get(data["group_id"])
        if not group:
            return not_found_response("组不存在")

        if UserGroupRelation.query.filter_by(
            user_id=user_id, group_id=group.id
        ).first():
            return error_response("用户已在该组中", 400)

        relation = UserGroupRelation(
            user_id=user_id,
            group_id=group.id,
            type=data.get("type", "base"),
            enable=data.get("enable", True),
        )
        db.session.add(relation)
        db.session.commit()
        return success_response(message="组分配成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Assign group error")
        return server_error_response("组分配失败")


@user_mgmt_bp.route("/users/<int:user_id>/groups/<int:group_id>", methods=["PUT"])
@admin_required
def update_user_group_relation(user_id, group_id):
    try:
        relation = UserGroupRelation.query.filter_by(
            user_id=user_id, group_id=group_id
        ).first()
        if not relation:
            return not_found_response("用户组关联不存在")

        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        relation.type = data.get("type", relation.type)
        relation.enable = data.get("enable", relation.enable)
        relation.updated_time = datetime.utcnow()
        db.session.commit()

        return success_response(message="用户组关系更新成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Update user group relation error")
        return server_error_response("用户组关系更新失败")


@user_mgmt_bp.route("/users/<int:user_id>/groups/<int:group_id>", methods=["DELETE"])
@admin_required
def remove_group(user_id, group_id):
    try:
        relation = UserGroupRelation.query.filter_by(
            user_id=user_id, group_id=group_id
        ).first()
        if not relation:
            return not_found_response("用户组关联不存在")

        db.session.delete(relation)
        db.session.commit()
        return success_response(message="组移除成功")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Remove group error")
        return server_error_response("组移除失败")
