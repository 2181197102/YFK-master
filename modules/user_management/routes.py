# user_management/routes.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from modules.auth.models import db, User, Role, UserRoleRelation, Group, UserGroupRelation
from modules.auth.decorators import admin_required
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
        group_filter = request.args.get('group')
        search = request.args.get('search')

        query = User.query

        # 搜索过滤
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.name.contains(search)
                )
            )

        # 角色过滤
        if role_filter:
            query = query.join(UserRoleRelation).join(Role).filter(Role.role_name == role_filter)

        # 组过滤
        if group_filter:
            query = query.join(UserGroupRelation).join(Group).filter(Group.group_name == group_filter)

        users = query.paginate(page=page, per_page=per_page, error_out=False)

        users_list = []
        for user in users.items:
            # 获取用户角色
            user_roles = db.session.query(Role).join(UserRoleRelation).filter(UserRoleRelation.user_id == user.id).all()
            roles = [{'id': role.id, 'role_code': role.role_code, 'role_name': role.role_name} for role in user_roles]

            # 获取用户组
            user_groups = db.session.query(Group, UserGroupRelation.type, UserGroupRelation.enable).join(UserGroupRelation).filter(UserGroupRelation.user_id == user.id).all()
            groups = [{'id': group.id, 'group_name': group.group_name, 'type': type_, 'enable': enable} for group, type_, enable in user_groups]

            user_dict = user.to_dict()
            user_dict['roles'] = roles
            user_dict['groups'] = groups
            users_list.append(user_dict)

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


@user_mgmt_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """获取单个用户详情"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取用户角色
        user_roles = db.session.query(Role).join(UserRoleRelation).filter(UserRoleRelation.user_id == user.id).all()
        roles = [{'id': role.id, 'role_code': role.role_code, 'role_name': role.role_name} for role in user_roles]

        # 获取用户组
        user_groups = db.session.query(Group, UserGroupRelation.type, UserGroupRelation.enable).join(UserGroupRelation).filter(UserGroupRelation.user_id == user.id).all()
        groups = [{'id': group.id, 'group_name': group.group_name, 'type': type_, 'enable': enable} for group, type_, enable in user_groups]

        user_dict = user.to_dict()
        user_dict['roles'] = roles
        user_dict['groups'] = groups

        return jsonify({'user': user_dict}), 200

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

        required_fields = ['username', 'password', 'name', 'age', 'gender']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}不能为空'}), 400

        username = data['username']
        password = data['password']
        name = data['name']
        age = data['age']
        gender = data['gender']
        enable = data.get('enable', True)
        roles = data.get('roles', [])
        groups = data.get('groups', [])

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': '用户名已存在'}), 400

        # 创建用户
        user = User(
            username=username,
            name=name,
            age=age,
            gender=gender,
            enable=enable
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()  # 获取用户ID

        # 分配角色
        for role_data in roles:
            role_id = role_data.get('role_id') if isinstance(role_data, dict) else role_data
            role = Role.query.get(role_id)
            if role:
                user_role = UserRoleRelation(
                    user_id=user.id,
                    role_id=role.id
                )
                db.session.add(user_role)

        # 分配组
        for group_data in groups:
            if isinstance(group_data, dict):
                group_id = group_data.get('group_id')
                group_type = group_data.get('type', 'base')
                group_enable = group_data.get('enable', True)
            else:
                group_id = group_data
                group_type = 'base'
                group_enable = True

            group = Group.query.get(group_id)
            if group:
                user_group = UserGroupRelation(
                    user_id=user.id,
                    group_id=group.id,
                    type=group_type,
                    enable=group_enable
                )
                db.session.add(user_group)

        db.session.commit()

        return jsonify({
            'message': '用户创建成功',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Create user error: {str(e)}')
        return jsonify({'error': '创建用户失败'}), 500


@user_mgmt_bp.route('/users/<int:user_id>', methods=['PUT'])
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

        if 'name' in data:
            user.name = data['name']

        if 'age' in data:
            user.age = data['age']

        if 'gender' in data:
            user.gender = data['gender']

        if 'enable' in data:
            user.enable = data['enable']

        if 'password' in data and data['password']:
            user.set_password(data['password'])

        # 更新角色
        if 'roles' in data:
            roles = data['roles']
            # 删除现有角色
            UserRoleRelation.query.filter_by(user_id=user_id).delete()
            # 添加新角色
            for role_data in roles:
                role_id = role_data.get('role_id') if isinstance(role_data, dict) else role_data
                role = Role.query.get(role_id)
                if role:
                    user_role = UserRoleRelation(
                        user_id=user_id,
                        role_id=role.id
                    )
                    db.session.add(user_role)

        # 更新组
        if 'groups' in data:
            groups = data['groups']
            # 删除现有组关系
            UserGroupRelation.query.filter_by(user_id=user_id).delete()
            # 添加新组关系
            for group_data in groups:
                if isinstance(group_data, dict):
                    group_id = group_data.get('group_id')
                    group_type = group_data.get('type', 'base')
                    group_enable = group_data.get('enable', True)
                else:
                    group_id = group_data
                    group_type = 'base'
                    group_enable = True

                group = Group.query.get(group_id)
                if group:
                    user_group = UserGroupRelation(
                        user_id=user_id,
                        group_id=group.id,
                        type=group_type,
                        enable=group_enable
                    )
                    db.session.add(user_group)

        user.updated_time = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '用户更新成功',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update user error: {str(e)}')
        return jsonify({'error': '更新用户失败'}), 500


@user_mgmt_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 删除用户角色关联
        UserRoleRelation.query.filter_by(user_id=user_id).delete()
        # 删除用户组关联
        UserGroupRelation.query.filter_by(user_id=user_id).delete()

        # 删除用户
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': '用户删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete user error: {str(e)}')
        return jsonify({'error': '删除用户失败'}), 500


# ======================= 角色管理 =======================

@user_mgmt_bp.route('/roles', methods=['GET'])
@admin_required
def get_roles():
    """获取所有角色"""
    try:
        roles = Role.query.all()
        roles_list = [role.to_dict() for role in roles]
        return jsonify({'roles': roles_list}), 200

    except Exception as e:
        current_app.logger.error(f'Get roles error: {str(e)}')
        return jsonify({'error': '获取角色列表失败'}), 500


@user_mgmt_bp.route('/roles', methods=['POST'])
@admin_required
def create_role():
    """创建角色"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        required_fields = ['role_code', 'role_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}不能为空'}), 400

        role_code = data['role_code']
        role_name = data['role_name']
        description = data.get('description', '')

        # 检查角色编码是否已存在
        existing_role = Role.query.filter_by(role_code=role_code).first()
        if existing_role:
            return jsonify({'error': '角色编码已存在'}), 400

        # 创建角色
        role = Role(
            role_code=role_code,
            role_name=role_name,
            description=description
        )

        db.session.add(role)
        db.session.commit()

        return jsonify({
            'message': '角色创建成功',
            'role': role.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Create role error: {str(e)}')
        return jsonify({'error': '创建角色失败'}), 500


@user_mgmt_bp.route('/roles/<int:role_id>', methods=['PUT'])
@admin_required
def update_role(role_id):
    """更新角色信息"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': '角色不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        if 'role_code' in data:
            role_code = data['role_code']
            existing_role = Role.query.filter(Role.role_code == role_code, Role.id != role_id).first()
            if existing_role:
                return jsonify({'error': '角色编码已存在'}), 400
            role.role_code = role_code

        if 'role_name' in data:
            role.role_name = data['role_name']

        if 'description' in data:
            role.description = data['description']

        role.updated_time = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '角色更新成功',
            'role': role.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update role error: {str(e)}')
        return jsonify({'error': '更新角色失败'}), 500


@user_mgmt_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@admin_required
def delete_role(role_id):
    """删除角色"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': '角色不存在'}), 404

        # 检查是否有用户使用该角色
        user_role_count = UserRoleRelation.query.filter_by(role_id=role_id).count()
        if user_role_count > 0:
            return jsonify({'error': '该角色下还有用户，无法删除'}), 400

        db.session.delete(role)
        db.session.commit()

        return jsonify({'message': '角色删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete role error: {str(e)}')
        return jsonify({'error': '删除角色失败'}), 500


# ======================= 组管理 =======================

@user_mgmt_bp.route('/groups', methods=['GET'])
@admin_required
def get_groups():
    """获取所有组"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')

        query = Group.query

        # 搜索过滤
        if search:
            query = query.filter(Group.group_name.contains(search))

        groups = query.paginate(page=page, per_page=per_page, error_out=False)

        groups_list = []
        for group in groups.items:
            group_dict = group.to_dict()
            # 获取组内用户数量
            user_count = UserGroupRelation.query.filter_by(group_id=group.id, enable=True).count()
            group_dict['user_count'] = user_count
            groups_list.append(group_dict)

        return jsonify({
            'groups': groups_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': groups.total,
                'pages': groups.pages,
                'has_next': groups.has_next,
                'has_prev': groups.has_prev
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Get groups error: {str(e)}')
        return jsonify({'error': '获取组列表失败'}), 500


@user_mgmt_bp.route('/groups', methods=['POST'])
@admin_required
def create_group():
    """创建组"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        if not data.get('group_name'):
            return jsonify({'error': 'group_name不能为空'}), 400

        group_name = data['group_name']
        enable = data.get('enable', True)

        # 检查组名是否已存在
        existing_group = Group.query.filter_by(group_name=group_name).first()
        if existing_group:
            return jsonify({'error': '组名已存在'}), 400

        # 创建组
        group = Group(
            group_name=group_name,
            enable=enable
        )

        db.session.add(group)
        db.session.commit()

        return jsonify({
            'message': '组创建成功',
            'group': group.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Create group error: {str(e)}')
        return jsonify({'error': '创建组失败'}), 500


@user_mgmt_bp.route('/groups/<int:group_id>', methods=['PUT'])
@admin_required
def update_group(group_id):
    """更新组信息"""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': '组不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        if 'group_name' in data:
            group_name = data['group_name']
            existing_group = Group.query.filter(Group.group_name == group_name, Group.id != group_id).first()
            if existing_group:
                return jsonify({'error': '组名已存在'}), 400
            group.group_name = group_name

        if 'enable' in data:
            group.enable = data['enable']

        group.updated_time = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': '组更新成功',
            'group': group.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update group error: {str(e)}')
        return jsonify({'error': '更新组失败'}), 500


@user_mgmt_bp.route('/groups/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_group(group_id):
    """删除组"""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': '组不存在'}), 404

        # 检查是否有用户在该组中
        user_group_count = UserGroupRelation.query.filter_by(group_id=group_id).count()
        if user_group_count > 0:
            return jsonify({'error': '该组下还有用户，无法删除'}), 400

        db.session.delete(group)
        db.session.commit()

        return jsonify({'message': '组删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete group error: {str(e)}')
        return jsonify({'error': '删除组失败'}), 500


@user_mgmt_bp.route('/groups/<int:group_id>/users', methods=['GET'])
@admin_required
def get_group_users(group_id):
    """获取组内用户列表"""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': '组不存在'}), 404

        # 获取组内用户
        user_relations = db.session.query(User, UserGroupRelation.type, UserGroupRelation.enable).join(UserGroupRelation).filter(UserGroupRelation.group_id == group_id).all()

        users_list = []
        for user, relation_type, relation_enable in user_relations:
            user_dict = user.to_dict()
            user_dict['relation_type'] = relation_type
            user_dict['relation_enable'] = relation_enable
            users_list.append(user_dict)

        return jsonify({
            'group': group.to_dict(),
            'users': users_list
        }), 200

    except Exception as e:
        current_app.logger.error(f'Get group users error: {str(e)}')
        return jsonify({'error': '获取组用户失败'}), 500


# ======================= 用户角色关系管理 =======================

@user_mgmt_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@admin_required
def assign_role(user_id):
    """为用户分配角色"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        data = request.get_json()
        if not data or 'role_id' not in data:
            return jsonify({'error': '角色ID不能为空'}), 400

        role_id = data['role_id']
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': '角色不存在'}), 404

        # 检查是否已存在该角色
        existing_role = UserRoleRelation.query.filter_by(user_id=user_id, role_id=role_id).first()
        if existing_role:
            return jsonify({'error': '用户已拥有该角色'}), 400

        # 分配角色
        user_role = UserRoleRelation(
            user_id=user_id,
            role_id=role_id
        )
        db.session.add(user_role)
        db.session.commit()

        return jsonify({'message': '角色分配成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Assign role error: {str(e)}')
        return jsonify({'error': '角色分配失败'}), 500


@user_mgmt_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@admin_required
def remove_role(user_id, role_id):
    """移除用户角色"""
    try:
        user_role = UserRoleRelation.query.filter_by(user_id=user_id, role_id=role_id).first()
        if not user_role:
            return jsonify({'error': '用户角色关联不存在'}), 404

        db.session.delete(user_role)
        db.session.commit()

        return jsonify({'message': '角色移除成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Remove role error: {str(e)}')
        return jsonify({'error': '角色移除失败'}), 500


# ======================= 用户组关系管理 =======================

@user_mgmt_bp.route('/users/<int:user_id>/groups', methods=['POST'])
@admin_required
def assign_group(user_id):
    """为用户分配组"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        data = request.get_json()
        if not data or 'group_id' not in data:
            return jsonify({'error': '组ID不能为空'}), 400

        group_id = data['group_id']
        group_type = data.get('type', 'base')  # base/temp
        enable = data.get('enable', True)

        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': '组不存在'}), 404

        # 检查是否已存在该组关系
        existing_group = UserGroupRelation.query.filter_by(user_id=user_id, group_id=group_id).first()
        if existing_group:
            return jsonify({'error': '用户已在该组中'}), 400

        # 分配组
        user_group = UserGroupRelation(
            user_id=user_id,
            group_id=group_id,
            type=group_type,
            enable=enable
        )
        db.session.add(user_group)
        db.session.commit()

        return jsonify({'message': '组分配成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Assign group error: {str(e)}')
        return jsonify({'error': '组分配失败'}), 500


@user_mgmt_bp.route('/users/<int:user_id>/groups/<int:group_id>', methods=['PUT'])
@admin_required
def update_user_group_relation(user_id, group_id):
    """更新用户组关系"""
    try:
        user_group = UserGroupRelation.query.filter_by(user_id=user_id, group_id=group_id).first()
        if not user_group:
            return jsonify({'error': '用户组关联不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        if 'type' in data:
            user_group.type = data['type']

        if 'enable' in data:
            user_group.enable = data['enable']

        user_group.updated_time = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': '用户组关系更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update user group relation error: {str(e)}')
        return jsonify({'error': '用户组关系更新失败'}), 500


@user_mgmt_bp.route('/users/<int:user_id>/groups/<int:group_id>', methods=['DELETE'])
@admin_required
def remove_group(user_id, group_id):
    """移除用户组"""
    try:
        user_group = UserGroupRelation.query.filter_by(user_id=user_id, group_id=group_id).first()
        if not user_group:
            return jsonify({'error': '用户组关联不存在'}), 404

        db.session.delete(user_group)
        db.session.commit()

        return jsonify({'message': '组移除成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Remove group error: {str(e)}')
        return jsonify({'error': '组移除失败'}), 500