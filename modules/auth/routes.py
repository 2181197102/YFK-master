from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
import uuid
from models.models import db, User, Role, UserRole

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': '用户名和密码不能为空'}), 400

        username = data['username']
        password = data['password']

        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': '用户名或密码错误'}), 401

        # 检查用户状态
        if not user.is_active:
            return jsonify({'error': '用户已被禁用'}), 401

        # 获取用户角色
        user_roles = db.session.query(Role).join(UserRole).filter(UserRole.user_id == user.id).all()
        roles = [role.name for role in user_roles]

        # 创建JWT token
        additional_claims = {
            'user_id': user.id,
            'username': user.username,
            'roles': roles
        }

        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24),
            additional_claims=additional_claims
        )

        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'roles': roles
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Login error: {str(e)}')
        return jsonify({'error': '登录失败'}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        required_fields = ['username', 'password', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}不能为空'}), 400

        username = data['username']
        password = data['password']
        email = data['email']
        role_name = data['role']

        # 验证角色是否存在
        valid_roles = ['患者', '家庭医生', '主治医生', '跨院医生', '急救医生', '科研人员', '管理员']
        if role_name not in valid_roles:
            return jsonify({'error': '无效的角色'}), 400

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': '用户名已存在'}), 400

        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'error': '邮箱已存在'}), 400

        # 创建新用户
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_active=True
        )

        db.session.add(user)
        db.session.flush()  # 获取用户ID

        # 分配角色
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user_role = UserRole(user_id=user.id, role_id=role.id)
            db.session.add(user_role)

        db.session.commit()

        return jsonify({
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Register error: {str(e)}')
        return jsonify({'error': '注册失败'}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        user_id = get_jwt_identity()
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
                'roles': roles,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Get profile error: {str(e)}')
        return jsonify({'error': '获取用户信息失败'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        # 这里可以实现token黑名单功能
        # 目前只返回成功消息
        return jsonify({'message': '登出成功'}), 200

    except Exception as e:
        current_app.logger.error(f'Logout error: {str(e)}')
        return jsonify({'error': '登出失败'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': '旧密码和新密码不能为空'}), 400

        old_password = data['old_password']
        new_password = data['new_password']

        # 获取用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 验证旧密码
        if not check_password_hash(user.password_hash, old_password):
            return jsonify({'error': '旧密码错误'}), 400

        # 更新密码
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({'message': '密码修改成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Change password error: {str(e)}')
        return jsonify({'error': '密码修改失败'}), 500