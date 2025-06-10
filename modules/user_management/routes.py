from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from models.models import db, User, Role, UserRole
from modules.auth.decorators import admin_required
import uuid
from datetime import datetime

user_mgmt_bp = Blueprint('user_management', __name__)


@user_mgmt_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """获取所有用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role_filter = request.args.get('role')
        search = request.args.get('search')

        query = User.query

        # 搜索过滤
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search)
                )
            )

        # 角色过滤
        if role_filter:
            query = query.join(UserRole).join(Role).filter(Role.name == role_filter)

        users = query.paginate(page=page, per_page=per_page, error_out=False)

        users_list = []
        for user in users.items:
            # 获取用户角色
            user_roles = db.session.query(Role).join(UserRole).filter(UserRole.user_id == user.id).all()
            roles = [role.name for role in user_roles]

            users_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'roles': roles,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            })

        return jsonify({
            'users': users_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Get users error: {str(e)}')
        return jsonify({'error': '获取用户列表失败'}), 500


@user_mgmt_bp.route('/users/<user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """获取单个用户详情"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取用户角色
        user_roles = db.session.query(Role).join(UserRole).filter(UserRole.user_id == user.id).all()
        roles = [role.name for role in user_roles]

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'roles': roles,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Get user error: {str(e)}')
        return jsonify({'error': '获取用户信息失败'}), 500


@user_mgmt_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """创建用户"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        required_fields = ['username', 'password', 'email', 'roles']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}不能为空'}), 400

        username = data['username']
        password = data['password']
        email = data['email']
        roles = data['roles']
        is_active = data.get('is_active', True)

        # 验证角色
        valid_roles = ['患者', '家庭医生', '主治医生', '跨院医生', '急救医生', '科研人员', '管理员']
        for role_name in roles:
            if role_name not in valid_roles:
                return jsonify({'error': f'无效的角色: {role_name}'}), 400

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': '用户名已存在'}), 400

        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': '邮箱已存在'}), 400

        # 创建用户
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            is_active=is_active
        )

        db.session.add(user)
        db.session.flush()  # 获取用户ID

        # 分配角色
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user_role = UserRole(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    role_id=role.id
                )
                db.session.add(user_role)

        db.session.commit()

        return jsonify({
            'message': '用户创建成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'roles': roles
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Create user error: {str(e)}')
        return jsonify({'error': '创建用户失败'}), 500


@user_mgmt_bp.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """更新用户信息"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        # 更新基本信息
        if 'username' in data:
            username = data['username']
            existing_user = User.query.filter(User.username == username, User.id != user_id).first()
            if existing_user:
                return jsonify({'error': '用户名已存在'}), 400
            user.username = username

        if 'email' in data:
            email = data['email']
            existing_email = User.query.filter(User.email == email, User.id != user_id).first()
            if existing_email:
                return jsonify({'error': '邮箱已存在'}), 400
            user.email = email

        if 'is_active' in data:
            user.is_active = data['is_active']

        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])

        # 更新角色
        if 'roles' in data:
            roles = data['roles']
            valid_roles = ['患者', '家庭医生', '主治医生', '跨院医生', '急救医生', '科研人员', '管理员']
            for role_name in roles:
                if role_name not in valid_roles:
                    return jsonify({'error': f'无效的角色: {role_name}'}), 400

            # 删除现有角色
            UserRole.query.filter_by(user_id=user_id).delete()

            # 添加新角色
            for role_name in roles:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user_role = UserRole(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        role_id=role.id
                    )
                    db.session.add(user_role)

        user.updated_at = datetime.utcnow()
        db.session.commit()

        # 获取更新后的角色
        user_roles = db.session.query(Role).join(UserRole).filter(UserRole.user_id == user.id).all()
        roles = [role.name for role in user_roles]

        return jsonify({
            'message': '用户更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'roles': roles,
                'updated_at': user.updated_at.isoformat()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update user error: {str(e)}')
        return jsonify({'error': '更新用户失败'}), 500


@user_mgmt_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 删除用户角色关联
        UserRole.query.filter_by(user_id=user_id).delete()

        # 删除用户
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': '用户删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete user error: {str(e)}')
        return jsonify({'error': '删除用户失败'}), 500


@user_mgmt_bp.route('/roles', methods=['GET'])
@admin_required
def get_roles():
    """获取所有角色"""
    try:
        roles = Role.query.all()
        roles_list = [{
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'created_at': role.created_at.isoformat() if role.created_at else None
        } for role in roles]

        return jsonify({'roles': roles_list}), 200

    except Exception as e:
        current_app.logger.error(f'Get roles error: {str(e)}')
        return jsonify({'error': '获取角色列表失败'}), 500


@user_mgmt_bp.route('/users/<user_id>/roles', methods=['POST'])
@admin_required
def assign_role(user_id):
    """为用户分配角色"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        data = request.get_json()
        if not data or 'role_name' not in data:
            return jsonify({'error': '角色名不能为空'}), 400

        role_name = data['role_name']
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({'error': '角色不存在'}), 404

        # 检查是否已存在该角色
        existing_role = UserRole.query.filter_by(user_id=user_id, role_id=role.id).first()
        if existing_role:
            return jsonify({'error': '用户已拥有该角色'}), 400

        # 分配角色
        user_role = UserRole(
            id=str(uuid.uuid4()),
            user_id=user_id,
            role_id=role.id
        )
        db.session.add(user_role)
        db.session.commit()

        return jsonify({'message': '角色分配成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Assign role error: {str(e)}')
        return jsonify({'error': '角色分配失败'}), 500


@user_mgmt_bp.route('/users/<user_id>/roles/<role_id>', methods=['DELETE'])
@admin_required
def remove_role(user_id, role_id):
    """移除用户角色"""
    try:
        user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
        if not user_role:
            return jsonify({'error': '用户角色关联不存在'}), 404

        db.session.delete(user_role)
        db.session.commit()

        return jsonify({'message': '角色移除成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Remove role error: {str(e)}')
        return jsonify({'error': '角色移除失败'}), 500