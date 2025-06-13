from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def role_required(*required_roles):
    """角色权限装饰器"""

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                claims = get_jwt()
                user_roles = claims.get('roles', [])
                print("访问者角色：" + ", ".join(user_roles))
                print("请求所需角色：" + ", ".join([str(r) for r in required_roles]))
                # 检查用户是否具有所需角色之一
                if not any(role in user_roles for role in required_roles):
                    return jsonify({'error': '权限不足'}), 403

                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': '权限验证失败'}), 500

        return decorated_function

    return decorator


def admin_required(f):
    """管理员权限装饰器"""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            user_roles = claims.get('roles', [])

            if '管理员' not in user_roles:
                return jsonify({'error': '需要管理员权限'}), 403

            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': '权限验证失败'}), 500

    return decorated_function


def doctor_only(f):
    """医生角色装饰器（所有医生角色）"""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            user_roles = claims.get('roles', [])

            doctor_roles = ['家庭医生', '主治医生', '跨院医生', '急救医生']
            if not any(role in user_roles for role in doctor_roles):
                return jsonify({'error': '需要医生权限'}), 403

            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': '权限验证失败'}), 500

    return decorated_function


def patient_or_doctor(f):
    """患者或医生权限装饰器"""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            user_roles = claims.get('roles', [])

            allowed_roles = ['患者', '家庭医生', '主治医生', '跨院医生', '急救医生']
            if not any(role in user_roles for role in allowed_roles):
                return jsonify({'error': '需要患者或医生权限'}), 403

            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': '权限验证失败'}), 500

    return decorated_function


def researcher_or_admin(f):
    """科研人员或管理员权限装饰器"""

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            claims = get_jwt()
            user_roles = claims.get('roles', [])

            allowed_roles = ['科研人员', '管理员']
            if not any(role in user_roles for role in allowed_roles):
                return jsonify({'error': '需要科研人员或管理员权限'}), 403

            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': '权限验证失败'}), 500

    return decorated_function