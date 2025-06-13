from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt

# ---- 角色常量（角色代码）----
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


def role_required(*allowed_roles: str):
    """通用角色权限装饰器，只识别 JWT.claims 中的 'role' 字符串"""
    allowed_set = set(allowed_roles)

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                role = get_jwt().get("role_code", None)
                current_app.logger.debug(f"访问者角色: {role}, 允许角色: {allowed_set}")

                if not role or role not in allowed_set:
                    return jsonify({"error": "权限不足"}), 403

                return fn(*args, **kwargs)

            except Exception:
                current_app.logger.exception("权限验证失败")
                return jsonify({"error": "权限验证失败"}), 500

        return wrapper

    return decorator


# ---- 语义化装饰器 ----

def admin_required(fn):
    return role_required(ADMIN)(fn)

def doctor_only(fn):
    return role_required(*DOCTOR_ROLES)(fn)

def patient_or_doctor(fn):
    return role_required(*PATIENT_OR_DOCTOR_ROLES)(fn)

def researcher_or_admin(fn):
    return role_required(*RESEARCHER_OR_ADMIN_ROLES)(fn)