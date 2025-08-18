# modules/medical_institutions/routes.py
"""
医疗机构相关API路由
提供患者病历、医生病历等相关数据的管理接口
"""

from datetime import datetime, timezone
import uuid

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_

from modules.medical_institutions.models import (
    PatientMedicalRecord,
    MedicalRecordDisease,
    MedicalRecordDataItem,
    DoctorMedicalRecord
)
from modules.data_management.models import ICD10Code
from utils.extensions import db
from modules.auth.models import User
from modules.auth.decorators import role_required

from utils.response import (
    success_response,
    error_response,
    not_found_response,
    server_error_response,
)

medical_inst_bp = Blueprint("medical_institutions", __name__)


# ─────────────────────────── 患者病历管理 ───────────────────────────
@medical_inst_bp.route("/patient-records", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "DOCTOR", "PATIENT")
def get_patient_records():
    """获取患者病历列表"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        # 获取查询参数
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        patient_id_num = request.args.get("patient_id_num")
        doctor_code = request.args.get("doctor_code")

        # 构建查询
        query = PatientMedicalRecord.query

        # 根据用户角色限制访问
        user_roles = [role.name for role in current_user.roles]
        if "PATIENT" in user_roles and "ADMIN" not in user_roles:
            # 患者只能查看自己的病历
            query = query.filter(PatientMedicalRecord.patient_id_num == current_user.id_card)
        elif patient_id_num:
            query = query.filter(PatientMedicalRecord.patient_id_num == patient_id_num)

        if doctor_code:
            query = query.filter(PatientMedicalRecord.doctor_code == doctor_code)

        # 分页查询
        pagination = query.order_by(PatientMedicalRecord.created_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        records = [record.to_dict() for record in pagination.items]

        return success_response({
            "records": records,
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
        current_app.logger.exception("Get patient records error")
        return server_error_response("获取患者病历失败")


@medical_inst_bp.route("/patient-records", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "DOCTOR")
def create_patient_record():
    """创建患者病历"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 必需字段验证
        required_fields = ["patient_id_num", "patient_name", "patient_sex", "doctor_code"]
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必需字段: {field}", 400)

        # 验证患者是否存在
        patient = User.query.filter_by(id_card=data["patient_id_num"]).first()
        if not patient:
            return error_response("患者用户不存在", 400)

        # 生成病历号
        record_id = f"rec_{data['patient_id_num']}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # 创建新病历
        record = PatientMedicalRecord(
            id=record_id,
            patient_id_num=data["patient_id_num"],
            patient_name=data["patient_name"],
            patient_sex=data["patient_sex"],
            doctor_code=data["doctor_code"],
            created_time=datetime.now(timezone.utc),
            updated_time=datetime.now(timezone.utc)
        )

        db.session.add(record)
        db.session.commit()

        return success_response(
            result=record.to_dict(),
            message="患者病历创建成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create patient record error")
        return server_error_response("创建患者病历失败")


@medical_inst_bp.route("/patient-records/<record_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "DOCTOR", "PATIENT")
def get_patient_record(record_id):
    """获取单个患者病历详情"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response("当前用户不存在", 400)

        record = PatientMedicalRecord.query.get(record_id)
        if not record:
            return not_found_response("病历不存在")

        # 权限检查：患者只能查看自己的病历
        user_roles = [role.name for role in current_user.roles]
        if "PATIENT" in user_roles and "ADMIN" not in user_roles:
            if record.patient_id_num != current_user.id_card:
                return error_response("无权访问此病历", 403)

        # 获取关联的疾病信息
        diseases = MedicalRecordDisease.query.filter_by(
            medical_record_num=record_id
        ).all()

        # 获取关联的数据项信息
        data_items = MedicalRecordDataItem.query.filter_by(
            medical_record_num=record_id
        ).all()

        result = record.to_dict()
        result['diseases'] = [disease.to_dict() for disease in diseases]
        result['data_items'] = [item.to_dict() for item in data_items]

        return success_response(result)

    except Exception:  # pragma: no cover
        current_app.logger.exception("Get patient record error")
        return server_error_response("获取患者病历失败")


# ─────────────────────────── 病历疾病管理 ───────────────────────────
@medical_inst_bp.route("/medical-record-diseases", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "DOCTOR")
def create_medical_record_disease():
    """为病历添加疾病诊断"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 必需字段验证
        required_fields = ["medical_record_num", "disease_code"]
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必需字段: {field}", 400)

        # 验证病历是否存在
        record = PatientMedicalRecord.query.get(data["medical_record_num"])
        if not record:
            return error_response("病历不存在", 400)

        # 验证疾病编码是否有效
        icd_code = ICD10Code.query.filter_by(code=data["disease_code"]).first()
        if not icd_code:
            return error_response("无效的疾病编码", 400)

        # 检查是否已存在相同的诊断
        existing = MedicalRecordDisease.query.filter_by(
            medical_record_num=data["medical_record_num"],
            disease_code=data["disease_code"]
        ).first()

        if existing:
            return error_response("该病历已存在相同的疾病诊断", 400)

        # 创建新的疾病诊断记录
        disease_record = MedicalRecordDisease(
            id=f"mrd_{data['medical_record_num']}_{data['disease_code']}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            medical_record_num=data["medical_record_num"],
            disease_code=data["disease_code"],
            created_time=datetime.now(timezone.utc),
            updated_time=datetime.now(timezone.utc)
        )

        db.session.add(disease_record)
        db.session.commit()

        return success_response(
            result=disease_record.to_dict(),
            message="疾病诊断添加成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create medical record disease error")
        return server_error_response("添加疾病诊断失败")


# ─────────────────────────── 病历数据项管理 ───────────────────────────
@medical_inst_bp.route("/medical-record-data-items", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "DOCTOR")
def create_medical_record_data_item():
    """为病历添加数据项"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 必需字段验证
        required_fields = ["medical_record_num", "associated_code"]
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必需字段: {field}", 400)

        # 验证病历是否存在
        record = PatientMedicalRecord.query.get(data["medical_record_num"])
        if not record:
            return error_response("病历不存在", 400)

        # 创建新的数据项记录
        data_item = MedicalRecordDataItem(
            id=f"mdi_{data['medical_record_num']}_{data['associated_code']}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            medical_record_num=data["medical_record_num"],
            associated_code=data["associated_code"],
            created_time=datetime.now(timezone.utc),
            updated_time=datetime.now(timezone.utc)
        )

        # 设置数据项内容
        if "data_fields" in data:
            data_item.set_data_fields_dict(data["data_fields"])

        db.session.add(data_item)
        db.session.commit()

        return success_response(
            result=data_item.to_dict(),
            message="数据项添加成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create medical record data item error")
        return server_error_response("添加数据项失败")


# ─────────────────────────── 医生病历关联管理 ───────────────────────────
@medical_inst_bp.route("/doctor-medical-records", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "DOCTOR")
def create_doctor_medical_record():
    """创建医生-病历关联"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 必需字段验证
        required_fields = ["doctor_name", "doctor_code", "patient_name", "patient_id_num", "medical_record_num"]
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必需字段: {field}", 400)

        # 验证病历是否存在
        record = PatientMedicalRecord.query.get(data["medical_record_num"])
        if not record:
            return error_response("病历不存在", 400)

        # 检查是否已存在相同的关联
        existing = DoctorMedicalRecord.query.filter_by(
            doctor_code=data["doctor_code"],
            medical_record_num=data["medical_record_num"]
        ).first()

        if existing:
            return error_response("该医生与病历的关联已存在", 400)

        # 创建新的医生-病历关联
        doctor_record = DoctorMedicalRecord(
            id=f"dmr_{data['doctor_code']}_{data['medical_record_num']}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            doctor_name=data["doctor_name"],
            doctor_code=data["doctor_code"],
            patient_name=data["patient_name"],
            patient_id_num=data["patient_id_num"],
            medical_record_num=data["medical_record_num"],
            created_time=datetime.now(timezone.utc),
            updated_time=datetime.now(timezone.utc)
        )

        db.session.add(doctor_record)
        db.session.commit()

        return success_response(
            result=doctor_record.to_dict(),
            message="医生-病历关联创建成功"
        )

    except Exception:  # pragma: no cover
        db.session.rollback()
        current_app.logger.exception("Create doctor medical record error")
        return server_error_response("创建医生-病历关联失败")


@medical_inst_bp.route("/doctor-medical-records/doctor/<doctor_code>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "DOCTOR")
def get_doctor_medical_records(doctor_code):
    """获取医生关联的病历列表"""
    try:
        # 获取查询参数
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # 查询医生关联的病历
        query = DoctorMedicalRecord.query.filter_by(doctor_code=doctor_code)

        # 分页查询
        pagination = query.order_by(DoctorMedicalRecord.created_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        records = [record.to_dict() for record in pagination.items]

        return success_response({
            "records": records,
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
        current_app.logger.exception("Get doctor medical records error")
        return server_error_response("获取医生病历关联失败")
