from flask import Blueprint, request, jsonify
from models import *
from utils.extensions import db
from typing import List, Dict, Any, Type
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from modules.TrustValue import TrustValue
from datetime import datetime, time
import ipaddress

# 创建蓝图
medical_record_bp = Blueprint('medical_record', __name__)

# 机构与数据表模型的映射关系
INSTITUTION_RECORD_DATA: Dict[str, Type[ins1_record_data | ins2_record_data | ins3_record_data]] = {
    'ins1': ins1_record_data,
    'ins2': ins2_record_data,
    'ins3': ins3_record_data
}

# 机构与数据表模型的映射关系
INSTITUTION_RECORD: Dict[str, Type[ins1_record | ins2_record | ins3_record]] = {
    'ins1': ins1_record,
    'ins2': ins2_record,
    'ins3': ins3_record
}

# 机构模型映射
INSTITUTION_MODELS = {
    1: {
        'record': ins1_record,
        'record_disease': ins1_record_disease,
        'record_data': ins1_record_data,
        'doctor_record': ins1_doctor_record
    },
    2: {
        'record': ins2_record,
        'record_disease': ins2_record_disease,
        'record_data': ins2_record_data,
        'doctor_record': ins2_doctor_record
    },
    3: {
        'record': ins3_record,
        'record_disease': ins3_record_disease,
        'record_data': ins3_record_data,
        'doctor_record': ins3_doctor_record
    }
}

def get_valid_fields(model: Type[ins1_record_data]) -> List[str]:
    """获取模型中所有有效的数据字段（排除基础字段）"""
    base_fields = ['id', 'medical_record_num', 'created_time', 'updated_time']
    model_columns = model.__table__.columns.keys()
    return [field for field in model_columns if field not in base_fields]


def query_institution_data(
        model_record_data, model_record,
        data_codes: List[str],
        nums: int
) -> List[Dict]:
    """查询指定机构表中的数据并格式化结果，包含关联的model_record信息"""
    # 查询前nums条数据，按ID排序确保结果一致性
    records = model_record_data.query.order_by(model_record_data.id).limit(nums).all()

    # 提取所有model_record_data的id，用于批量查询关联的model_record（优化查询效率）
    data_ids = [record.id for record in records]

    # 批量查询model_record中匹配的记录，减少数据库交互
    # 假设model_record的id字段与model_record_data的id字段直接关联
    model_records = model_record.query.filter(model_record.id.in_(data_ids)).all()

    # 将model_record结果转为字典，便于快速查询（key为id）
    model_record_map = {rec.id: rec for rec in model_records}

    # 格式化结果，包含需要的字段及关联信息
    result = []
    for record in records:
        # 获取关联的model_record
        related_model_rec = model_record_map.get(record.id)
        print(related_model_rec)
        # 基础信息（机构数据）
        record_data = {
            'medical_record_num': record.medical_record_num,
            'institution': model_record_data.__tablename__.split('_')[0],  # 提取机构标识
            # 初始化关联字段为None（若未匹配到）
            'age': None,
            'gender': None,
            'id_card': None,
            'doctor_code': None,
            'phone': None
        }
        # 如果找到关联的model_record，补充字段
        if related_model_rec:
            record_data.update({
                'age': related_model_rec.age,
                'gender': related_model_rec.gender,
                'id_card': related_model_rec.id_card,
                'doctor_code': related_model_rec.doctor_code,
                'phone': related_model_rec.phone
            })

        # 添加用户选择的字段
        for code in data_codes:
            if hasattr(record, code):
                record_data[code] = getattr(record, code)

        result.append(record_data)

    return result


@medical_record_bp.route('/get_record_data', methods=['POST'])
@jwt_required()
def get_record_data():
    """
    根据选择的机构、字段和数量查询医疗数据
    输入格式:
    {
        "data_code": ["K_FH", "J_HD1"],
        "nums": 10,
        "institutions": ["ins1", "ins2"]
    }
    """
    req_data = request.get_json()
    user_id = get_jwt_identity()

    # 获取客户端IP并检查白名单
    client_ip = get_client_ip()
    is_whitelist_ip = is_ip_in_whitelist(client_ip)

    # 检查工作时间
    is_working_time_flag = is_working_time()

    # 更新访问追踪统计
    update_access_tracking(user_id, client_ip, is_working_time_flag, is_whitelist_ip)

    # 2. 提取并验证参数
    data_codes = req_data.get('data_code', [])
    nums = req_data.get('nums', 0)
    institutions = req_data.get('institutions', [])
    # print(req_data)
    # 3. 多机构数据查询
    all_results = []
    for ins in institutions:
        model_record_data = INSTITUTION_RECORD_DATA[ins]
        model_record = INSTITUTION_RECORD[ins]
        ins_results = query_institution_data(model_record_data,model_record, data_codes, nums)
        all_results.extend(ins_results)

    data_code_details = {}
    if data_codes:  # 避免空列表查询
        # 查询条件：data_code在请求的data_codes中
        disease_data_records = Disease_data.query.filter(
            Disease_data.data_code.in_(data_codes)
        ).all()
        # 整理为 {data_code: 详细信息字典} 的格式
        for record in disease_data_records:
            data_code_details[record.data_code] = record.to_dict()

    sensitive = req_data.get('sensitive', 0)
    Trustvalue = req_data.get('Trustvalue', 0)
    # if is_single:
    #     sensitive = sensitive + 0.2
    # print(sensitive)
    return jsonify({
        "status": "success",
        "message": f"成功查询到{len(all_results)}条数据",
        "total_count": len(all_results),
        "institutions": institutions,
        "data_codes": data_codes,
        "data_code_details": data_code_details,
        "requested_nums": nums,
        "client_ip": client_ip,
        "is_whitelist_ip": is_whitelist_ip,
        "is_working_time": is_working_time_flag,
        "results": all_results,
        "sensitive": sensitive,
        "Trustvalue": Trustvalue,
    }), 200


@medical_record_bp.route("/get_patient", methods=["GET"])
@jwt_required()
def get_patient():
    # print(11111)
    user_id = get_jwt_identity()

    if not user_id:
        return jsonify({
            "code": 400,
            "msg": "参数错误：请传入有效的user_id（整数）",
            "data": None
        }), 400

        # -------------------------- 2. 根据user_id查询sys_users表，获取id_card --------------------------
    user = User.query.filter_by(id=user_id, enable=True).first()
    if not user:
        return jsonify({
            "code": 404,
            "msg": f"未找到ID为{user_id}的有效用户",
            "data": None
        }), 404
    user_id_card = user.id_card  # 提取用户身份证号

    # -------------------------- 3. 根据user_id查询sys_user_group_relation表，获取group_id --------------------------
    group_relations = UserGroupRelation.query.filter_by(
        user_id=user_id,
        enable=True
    ).all()
    if not group_relations:
        return jsonify({
            "code": 404,
            "msg": f"用户{user_id}未关联任何有效组",
            "data": None
        }), 404
    # 提取去重的group_id（避免同一组重复查询）
    group_ids = list({relation.group_id for relation in group_relations})

    # -------------------------- 4. 根据group_id查询对应ins{group_id}_doctor_record表 --------------------------
    all_medical_records = []
    for group_id in group_ids:
        # 4.1 获取当前组对应的医生病历模型（无则跳过）
        doctor_record_model = INSTITUTION_MODELS.get(group_id)['doctor_record']

        if not doctor_record_model:
            continue  # 若group_id无对应ins表，跳过该组

        # 4.2 用身份证号（patient_id_num）查询该机构的所有病历记录
        medical_records = doctor_record_model.query.filter_by(
            doctor_code=user_id_card
        ).all()

        # 4.3 用模型自带的to_dict()格式化数据（复用用户定义的方法）
        formatted_records = [record.to_dict() for record in medical_records]
        all_medical_records.extend(formatted_records)

    # -------------------------- 5. 返回最终查询结果 --------------------------
    return jsonify({
        "code": 200,
        "msg": "查询成功" if all_medical_records else "未查询到该用户的病历记录",
        "data": {
            "user_info": {
                "user_id": user_id,
                "id_card": user_id_card,
                "user_name": user.name  # 附加用户名，提升结果实用性（非新功能，属用户表已有字段）
            },
            "related_group_ids": group_ids,
            "total_medical_records": len(all_medical_records),
            "medical_records": all_medical_records
        }
    })


@medical_record_bp.route('/disease-data-codes', methods=['GET'])
def get_disease_data_rows():
    """
    获取每个disease_code对应的所有完整行数据
    支持可选参数disease_code进行过滤，例如:
    /disease-data-rows?disease_code=A000&disease_code=B159
    """
    # 获取查询参数中的disease_code列表
    disease_codes = request.args.getlist('disease_code')
    # 构建查询
    query = Disease_data.query

    # 如果指定了disease_code参数，则过滤
    if disease_codes:
        query = query.filter(Disease_data.disease_code.in_(disease_codes))

    # 执行查询
    results = query.all()

    # 整理结果：按disease_code分组，收集对应的完整行数据
    disease_data_map = defaultdict(list)
    for item in results:
        # 将对象转换为字典（假设模型类有to_dict()方法，若无则手动构造）
        row_data = item.to_dict() if hasattr(item, 'to_dict') else {
            column.name: getattr(item, column.name)
            for column in item.__table__.columns
        }
        disease_data_map[item.disease_code].append(row_data)

    # 转换为有序字典并排序（按disease_code排序）
    sorted_result = {
        disease_code: rows
        for disease_code, rows in sorted(disease_data_map.items())
    }

    # 计算总记录数
    total_rows = sum(len(rows) for rows in sorted_result.values())

    return jsonify({
        'status': 'success',
        'data': sorted_result,
        'message': f"共找到{len(sorted_result)}个疾病代码，对应{total_rows}行数据"
    }), 200


def keep_first_occurrence(lst):
    """保留列表中首次出现的元素，去除后续重复项"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def get_client_ip():
    """获取客户端真实IP地址"""
    # 优先从X-Forwarded-For获取（适用于代理环境）
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    # 其次从X-Real-IP获取
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    # 最后从remote_addr获取
    else:
        return request.remote_addr


def is_ip_in_whitelist(client_ip: str) -> bool:
    """检查IP是否在白名单中"""
    try:
        # 查询所有启用的IP白名单
        whitelist_ips = IPWhitelist.query.filter_by(is_active=True).all()

        if not whitelist_ips:
            return True  # 如果没有配置白名单，默认允许所有IP

        # 检查IP是否匹配
        for whitelist_ip in whitelist_ips:
            try:
                # 支持CIDR格式的IP范围
                if '/' in whitelist_ip.ip_address:
                    if ipaddress.ip_address(client_ip) in ipaddress.ip_network(whitelist_ip.ip_address, strict=False):
                        return True
                else:
                    # 精确匹配
                    if client_ip == whitelist_ip.ip_address:
                        return True
            except (ipaddress.AddressValueError, ValueError):
                # IP格式错误，跳过
                continue

        return False
    except Exception:
        # 发生异常时默认允许访问
        return True


def is_working_time() -> bool:
    """检查当前时间是否在工作时间白名单中"""
    try:
        # 查询所有启用的工作时间白名单
        working_times = WorkingTimeWhitelist.query.filter_by(is_active=True).all()

        if not working_times:
            return True  # 如果没有配置工作时间，默认允许所有时间

        current_time = datetime.now().time()
        current_weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday

        # 检查当前时间是否在任何一个工作时间段内
        for working_time in working_times:
            # 检查星期几是否匹配
            if working_time.day_of_week == current_weekday:
                # 检查时间是否在范围内
                if working_time.start_time <= current_time <= working_time.end_time:
                    return True

        return False
    except Exception:
        # 发生异常时默认允许访问
        return True


def update_access_tracking(user_id: int, client_ip: str, is_working_time_flag: bool, is_whitelist_ip_flag: bool):
    """更新访问追踪统计"""
    try:
        # 更新访问时间统计
        ap_record = AccessTimeTracker.query.filter_by(user_id=user_id).first()
        if not ap_record:
            ap_record = AccessTimeTracker(
                user_id=user_id,
                ap_num_ni=0 if is_working_time_flag else 1,
                ap_num_ui=1 if is_working_time_flag else 0
            )
            db.session.add(ap_record)
        else:
            if is_working_time_flag:
                ap_record.ap_num_ni += 1
            else:
                ap_record.ap_num_ui += 1

        # 更新访问IP统计
        at_record = AccessLocationTracker.query.filter_by(user_id=user_id).first()
        if not at_record:
            at_record = AccessLocationTracker(
                user_id=user_id,
                at_num_nd=0 if is_whitelist_ip_flag else 1,
                at_num_ad=1 if is_whitelist_ip_flag else 0,
                last_ip=client_ip
            )
            at_record.add_ip_to_history(client_ip)
            db.session.add(at_record)
        else:
            if is_whitelist_ip_flag:
                at_record.at_num_nd += 1
            else:
                at_record.at_num_ad += 1

            at_record.add_ip_to_history(client_ip)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        # 记录错误但不影响主流程
        print(f"更新访问追踪统计失败: {str(e)}")


@medical_record_bp.route('/get_sensitive_data', methods=['POST'])
@jwt_required()
def get_sensitive_data():
    # 获取请求数据

    data = request.get_json()
    user_id = get_jwt_identity()

    # 获取客户端IP并检查白名单
    client_ip = get_client_ip()
    is_whitelist_ip = is_ip_in_whitelist(client_ip)

    # 检查工作时间
    is_working_time_flag = is_working_time()

    # 更新访问追踪统计
    update_access_tracking(user_id, client_ip, is_working_time_flag, is_whitelist_ip)

    # 验证输入格式
    if not isinstance(data, dict):
        return jsonify({"message": "输入格式错误，应为JSON对象"}), 400

    # 提取参数并验证
    disease_codes = data.get('disease_code', [])
    data_codes = data.get('data_code', [])

    # 处理重复的disease_code，只保留首次出现的
    unique_disease = keep_first_occurrence(disease_codes)

    # 查询similar结果
    similar_results = []
    if unique_disease:
        # 查询数据库
        query = Disease_data.query.filter(Disease_data.disease_code.in_(unique_disease)).all()

        # 确保结果顺序与输入顺序一致，并去重
        seen_disease = set()
        for code in unique_disease:
            if code not in seen_disease:
                # 查找对应的数据
                for item in query:
                    if item.disease_code == code:
                        similar_results.append(float(item.similar))
                        break

    # 处理重复的data_code，只保留首次出现的
    unique_data = keep_first_occurrence(data_codes)

    # 查询sensitive结果
    sensitive_results = []
    if unique_data:
        # 查询数据库
        query = Disease_data.query.filter(Disease_data.data_code.in_(unique_data)).all()

        # 确保结果顺序与输入顺序一致，并去重
        seen_data = set()
        for code in unique_data:
            if code not in seen_data:
                # 查找对应的数据
                for item in query:
                    if item.data_code == code:
                        sensitive_results.append(float(item.sensitive))
                        break

    # 访问成功率
    ast = AccessSuccessTracker.query.filter_by(user_id=user_id).first()
    ast_data = {
        'num_as': ast.ast_num_as if ast else 0,
        'num_af': ast.ast_num_af if ast else 0
    }

    # 操作行为
    ob = OperationBehaviorTracker.query.filter_by(user_id=user_id).first()
    ob_data = {
        'num_view': ob.ob_num_view if ob else 0,
        'num_copy': ob.ob_num_copy if ob else 0,
        'num_download': ob.ob_num_download if ob else 0,
        'num_add': ob.ob_num_add if ob else 0,
        'num_revise': ob.ob_num_revise if ob else 0,
        'num_delete': ob.ob_num_delete if ob else 0
    }

    # 数据敏感度
    ds = DataSensitivityTracker.query.filter_by(user_id=user_id).first()
    ds_data = {
        'num1': ds.ds_num1 if ds else 0,
        'num2': ds.ds_num2 if ds else 0
    }

    # 访问时间
    ap = AccessTimeTracker.query.filter_by(user_id=user_id).first()
    ap_data = {
        'num_ni': ap.ap_num_ni if ap else 0,
        'num_ui': ap.ap_num_ui if ap else 0
    }

    # 访问IP
    at = AccessLocationTracker.query.filter_by(user_id=user_id).first()
    at_data = {
        'num_nd': at.at_num_nd if at else 0,
        'num_ad': at.at_num_ad if at else 0
    }

    Trustelement = TrustValue.TrustElement(ast_data, ob_data, ds_data, ap_data, at_data, similar_results,
                                           sensitive_results)
    Trustvalue = TrustValue.TrustValue(Trustelement)

    value = Trustvalue.GetValue()
    sensitive = Trustvalue.GetSensitiveValue()

    if value > sensitive:
        ob.ob_num_view += 1
        ast.ast_num_as += 1  # 成功访问次数加1
        db.session.add(ob)
    else:
        ast.ast_num_af += 1  # 失败访问次数加1
    db.session.add(ast)
    # 根据sensitive_results更新DataSensitivityTracker
    for val in sensitive_results:
        if val == 0.5:
            ds.ds_num2 += 1
        elif val == 0.3:
            ds.ds_num1 += 1
    db.session.add(ds)
    db.session.commit()

    # 返回结果
    return jsonify({
        'user_id': user_id,
        'client_ip': client_ip,
        'is_whitelist_ip': is_whitelist_ip,
        'is_working_time': is_working_time_flag,
        'access_success': ast_data,
        'operation_behavior': ob_data,
        'data_sensitivity': ds_data,
        'access_period': ap_data,
        'access_location': at_data,
        'Trustvalue': value,
        'sensitive': sensitive,
    }), 200


@medical_record_bp.route("/get_patient_detail", methods=["GET"])
@jwt_required()
def get_patient_detail():
    """
    根据病历号查询病人的详细病历数据
    请求参数:
        medical_record_num: 病历号（必填）
    返回:
        病人基本信息 + 病历详细数据
    示例: GET /get_patient_detail?medical_record_num=MR001
    """
    try:
        # -------------------------- 1. 参数验证 --------------------------
        medical_record_num = request.args.get("medical_record_num")

        if not medical_record_num:
            return jsonify({
                "code": 400,
                "msg": "参数错误：缺少必填参数 medical_record_num",
                "data": None
            }), 400

        # -------------------------- 2. 获取当前登录用户信息 --------------------------
        user_id = get_jwt_identity()

        if not user_id:
            return jsonify({
                "code": 400,
                "msg": "参数错误：请传入有效的user_id（整数）",
                "data": None
            }), 400

        user = User.query.filter_by(id=user_id, enable=True).first()
        if not user:
            return jsonify({
                "code": 404,
                "msg": f"未找到ID为{user_id}的有效用户",
                "data": None
            }), 404

        user_id_card = user.id_card  # 医生工号即为身份证号

        # -------------------------- 3. 查询用户所属的group_id（即institution_id） --------------------------
        group_relations = UserGroupRelation.query.filter_by(
            user_id=user_id,
            enable=True
        ).all()

        if not group_relations:
            return jsonify({
                "code": 404,
                "msg": f"用户{user_id}未关联任何有效组",
                "data": None
            }), 404

        # 提取去重的group_id（即institution_id）
        group_ids = list({relation.group_id for relation in group_relations})

        # -------------------------- 4. 遍历用户所属的所有机构，查找该病历 --------------------------
        for institution_id in group_ids:
            # 跳过无效的机构ID
            if institution_id not in INSTITUTION_MODELS:
                continue

            # 获取对应机构的模型
            model_map = INSTITUTION_MODELS[institution_id]
            doctor_record_model = model_map["doctor_record"]
            record_model = model_map["record"]
            record_data_model = model_map["record_data"]
            record_disease_model = model_map["record_disease"]

            # 验证该病历是否属于当前医生
            doctor_record = doctor_record_model.query.filter_by(
                medical_record_num=medical_record_num,
                doctor_code=user_id_card
            ).first()

            # 如果在该机构找到了该病历
            if doctor_record:
                # -------------------------- 5. 查询病人基本信息（record表） --------------------------
                patient_basic = record_model.query.filter_by(
                    id=medical_record_num
                ).first()

                # -------------------------- 6. 查询病历详细数据（record_data表） --------------------------
                patient_data = record_data_model.query.filter_by(
                    medical_record_num=medical_record_num
                ).first()

                # -------------------------- 7. 查询病种信息（record_disease表） --------------------------
                disease_info = record_disease_model.query.filter_by(
                    medical_record_num=medical_record_num
                ).first()

                # -------------------------- 8. 格式化返回数据 --------------------------
                patient_detail = {
                    "medical_record_num": medical_record_num,
                    "institution_id": institution_id,
                    "institution_name": f"机构{institution_id}",
                    "patient_basic_info": patient_basic.to_dict() if patient_basic else None,
                    "patient_record_data": patient_data.to_dict() if patient_data else None,
                    "disease_info": disease_info.to_dict() if disease_info else None,
                    "doctor_info": {
                        "doctor_name": doctor_record.doctor_name,
                        "doctor_code": doctor_record.doctor_code
                    }
                }

                # -------------------------- 9. 返回结果 --------------------------
                return jsonify({
                    "code": 200,
                    "msg": "查询成功",
                    "data": patient_detail
                }), 200

        # 如果所有机构都没有找到该病历
        return jsonify({
            "code": 403,
            "msg": f"无权访问：病历号 {medical_record_num} 不属于当前医生",
            "data": None
        }), 403

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "msg": f"数据库错误: Database query failed",
            "data": None
        }), 500
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"服务器错误: Internal server error",
            "data": None
        }), 500


@medical_record_bp.route("/get_patient_records_by_idcard", methods=["GET"])
@jwt_required()
def get_patient_records_by_idcard():
    """
    根据病人身份证号查询该病人在所有机构的病历详情
    请求参数:
        id_card: 病人身份证号（必填）
    返回:
        该病人在所有机构的病历详细数据列表，突出显示当前医生信息和所属机构
    示例: GET /get_patient_records_by_idcard?id_card=110101199001011234
    """
    try:
        # -------------------------- 1. 参数验证 --------------------------
        patient_id_card = request.args.get("id_card")

        if not patient_id_card:
            return jsonify({
                "code": 400,
                "msg": "参数错误：缺少必填参数 id_card",
                "data": None
            }), 400

        # -------------------------- 2. 获取当前登录医生信息和所属机构 --------------------------
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id, enable=True).first()

        if not user:
            return jsonify({
                "code": 404,
                "msg": f"未找到ID为{user_id}的有效用户",
                "data": None
            }), 404

        # 获取当前医生的工号（身份证号）
        current_doctor_code = user.id_card

        # 查询当前医生所属的机构（group_id即institution_id）
        group_relations = UserGroupRelation.query.filter_by(
            user_id=user_id,
            enable=True
        ).all()

        if not group_relations:
            return jsonify({
                "code": 404,
                "msg": f"用户{user_id}未关联任何有效组",
                "data": None
            }), 404

        # 提取当前医生所属的所有机构ID
        current_doctor_institutions = list({relation.group_id for relation in group_relations})

        # 组装当前医生信息
        current_doctor_info = {
            "doctor_id": user_id,
            "doctor_name": user.name,
            "doctor_code": current_doctor_code,
            "id_card": current_doctor_code,
            "institutions": [
                {
                    "institution_id": inst_id,
                    "institution_name": f"机构{inst_id}"
                } 
                for inst_id in current_doctor_institutions
            ]
        }

        # -------------------------- 3. 遍历所有机构，查询病历数据 --------------------------
        all_institution_records = []
        total_records_count = 0

        for institution_id, model_map in INSTITUTION_MODELS.items():
            # 获取当前机构的模型
            doctor_record_model = model_map["doctor_record"]
            record_model = model_map["record"]
            record_data_model = model_map["record_data"]
            record_disease_model = model_map["record_disease"]

            # 3.1 从doctor_record表中查询该身份证号对应的所有病历号
            doctor_records = doctor_record_model.query.filter_by(
                patient_id_num=patient_id_card
            ).all()

            if not doctor_records:
                # 该机构没有该病人的病历，跳过
                continue

            # 提取所有病历号
            medical_record_nums = [dr.medical_record_num for dr in doctor_records]

            # 3.2 根据病历号列表，批量查询record_data表获取详细信息
            institution_records = []
            for medical_record_num in medical_record_nums:
                # 查询病人基本信息
                patient_basic = record_model.query.filter_by(
                    id_card=patient_id_card
                ).first()

                # 查询病历详细数据
                patient_data = record_data_model.query.filter_by(
                    medical_record_num=medical_record_num
                ).first()

                # 查询病种信息
                disease_info = record_disease_model.query.filter_by(
                    medical_record_num=medical_record_num
                ).first()

                # 查找对应的医生信息
                doctor_info = next(
                    (dr for dr in doctor_records if dr.medical_record_num == medical_record_num),
                    None
                )

                # 判断该病历是否由当前登录医生创建
                is_current_doctor = (
                    doctor_info and 
                    doctor_info.doctor_code == current_doctor_code
                )

                # 组装单条病历记录
                record_detail = {
                    "medical_record_num": medical_record_num,
                    "is_current_doctor_record": is_current_doctor,  # 标记是否为当前医生的病历
                    "patient_basic_info": patient_basic.to_dict() if patient_basic else None,
                    "patient_record_data": patient_data.to_dict() if patient_data else None,
                    "disease_info": disease_info.to_dict() if disease_info else None,
                    "doctor_info": {
                        "doctor_name": doctor_info.doctor_name if doctor_info else None,
                        "doctor_code": doctor_info.doctor_code if doctor_info else None,
                        "is_current_doctor": is_current_doctor  # 标记是否为当前医生
                    },
                    "record_time": {
                        "created_time": doctor_info.created_time.isoformat() if doctor_info and doctor_info.created_time else None,
                        "updated_time": doctor_info.updated_time.isoformat() if doctor_info and doctor_info.updated_time else None
                    }
                }

                institution_records.append(record_detail)

            # 判断该机构是否为当前医生所属机构
            is_current_doctor_institution = institution_id in current_doctor_institutions

            # 统计当前医生在该机构的病历数
            current_doctor_records_count = sum(
                1 for record in institution_records 
                if record.get("is_current_doctor_record", False)
            )

            # 3.3 汇总当前机构的所有病历
            all_institution_records.append({
                "institution_id": institution_id,
                "institution_name": f"机构{institution_id}",
                "is_current_doctor_institution": is_current_doctor_institution,  # 标记是否为当前医生所属机构
                "records_count": len(institution_records),
                "current_doctor_records_count": current_doctor_records_count,  # 当前医生在该机构的病历数
                "records": institution_records
            })

            total_records_count += len(institution_records)

        # -------------------------- 4. 统计当前医生的病历数 --------------------------
        current_doctor_total_records = sum(
            inst.get("current_doctor_records_count", 0) 
            for inst in all_institution_records
        )

        # -------------------------- 5. 返回结果 --------------------------
        if total_records_count == 0:
            return jsonify({
                "code": 200,
                "msg": f"未查询到身份证号 {patient_id_card} 的任何病历记录",
                "data": {
                    "current_doctor": current_doctor_info,  # 当前医生信息
                    "patient_id_card": patient_id_card,
                    "total_institutions": 0,
                    "total_records": 0,
                    "current_doctor_total_records": 0,
                    "institution_records": []
                }
            }), 200

        return jsonify({
            "code": 200,
            "msg": "查询成功",
            "data": {
                "current_doctor": current_doctor_info,  # 当前登录医生的完整信息
                "patient_id_card": patient_id_card,
                "total_institutions": len(all_institution_records),
                "total_records": total_records_count,
                "current_doctor_total_records": current_doctor_total_records,  # 当前医生创建的病历总数
                "institution_records": all_institution_records
            }
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "msg": f"数据库错误: Database query failed",
            "data": None
        }), 500
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"服务器错误: Internal server error",
            "data": None
        }), 500


@medical_record_bp.route("/get_my_data", methods=["GET"])
@jwt_required()
def get_my_data():

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id, enable=True).first()
    user_id_card = user.id_card  # 提取用户身份证号（用于后续关联）
    user_info = user.to_dict()  # 复用模型to_dict()方法，获取用户完整信息
    # print(user_id_card)
    # -------------------------- 3. 遍历group_id=1/2/3，查询对应机构的病历数据 --------------------------
    all_group_records = []  # 存储所有机构的病历数据
    for group_id, model_map in INSTITUTION_MODELS.items():
        # 获取当前机构的两个核心模型
        record_model = model_map["record"]  # 病历主表（关联身份证号）
        record_data_model = model_map["record_data"]  # 病历数据项表（目标表）
        # print(record_model)
        # 3.1 第一步：从病历主表查询该用户的medical_record_num（关联身份证号）
        # 注：ins{group_id}_record表需含patient_id_num字段（对应user.id_card）
        user_medical_nums = record_model.query.filter_by(
            id_card=user_id_card,
        ).with_entities(record_model.id).all()
        # print(user_medical_nums)
        # 提取medical_record_num列表（去重，避免重复查询）
        medical_num_list = list({item[0] for item in user_medical_nums})
        # print(medical_num_list)
        if not medical_num_list:
            # 该机构无此用户的病历主记录，跳过
            all_group_records.append({
                "group_id": group_id,
                "institution_name": f"机构{group_id}",
                "record_data_count": 0,
                "record_data": []
            })
            continue
        # print(all_group_records)
        # 3.2 第二步：根据medical_record_num查询病历数据项表
        record_data_list = record_data_model.query.filter(
            record_data_model.medical_record_num.in_(medical_num_list)
        ).all()
        # print(record_data_list)
        # 3.3 格式化数据（复用模型to_dict()方法）
        formatted_data = [data.to_dict() for data in record_data_list]

        # 3.4 汇总当前机构数据
        all_group_records.append({
            "group_id": group_id,
            "institution_name": f"机构{group_id}",
            "record_data_count": len(formatted_data),
            "record_data": formatted_data
        })

    # -------------------------- 4. 计算总数据量 --------------------------
    total_data_count = sum(item["record_data_count"] for item in all_group_records)

    # -------------------------- 5. 返回最终结果 --------------------------
    return jsonify({
        "code": 200,
        "msg": "查询成功" if total_data_count > 0 else "未查询到任何病历数据",
        "data": {
            "user_info": {
                "user_id": user_id,
                "id_card": user_id_card,
                "user_name": user_info["name"],  # 附加用户名，提升可读性
                "enable": user_info["enable"]
            },
            "total_record_data_count": total_data_count,
            "group_records": all_group_records  # 各机构的详细数据
        }
    })


@medical_record_bp.route('/add_record', methods=['POST'])
@jwt_required()
def add_record():
    """
    添加病历记录（多表关联插入）
    请求体需包含：用户认证信息、患者基本信息、医生信息、疾病相关参数
    """
    try:
        # 1. 获取当前用户ID（实际应用中建议从认证token中解析）
        user_id = get_jwt_identity()
        # print(user_id)
        # 2. 查询用户所属组ID
        user_group = UserGroupRelation.query.filter_by(
            user_id=user_id,
            enable=True
        ).first()
        doctor = User.query.filter_by(
            id=user_id,
            enable=True
        ).first()
        doctor_id = doctor.id_card
        doctor_name = doctor.username
        # print(user_code)
        if not user_group:
            return jsonify({'code': 404, 'msg': '未查询到用户所属有效组'}), 404

        group_id = user_group.group_id
        # print(group_id)

        # 3. 动态获取对应组的模型类
        model_suffixes = [
            'record',
            'record_data',
            'record_disease',
            'doctor_record'
        ]
        models = {}

        for suffix in model_suffixes:
            models[suffix] = INSTITUTION_MODELS[group_id][suffix]


        # 4. 解析请求数据
        req_data = request.json
        # print(req_data)
        # 6. 开启数据库事务
        db.session.begin_nested()

        # 7. 插入医生-病历表（获取自增ID作为medical_record_num）
        doctor_record = models['doctor_record'](
            doctor_name=doctor_name,
            doctor_code=doctor_id,
            patient_name=req_data['name'],
            patient_id_num=req_data['id_card'],
            medical_record_num='temp'  # 临时值，稍后更新
        )

        db.session.add(doctor_record)
        db.session.flush()  # 触发自增ID生成
        print(1)
        medical_record_num = str(doctor_record.id)
        doctor_record.medical_record_num = medical_record_num  # 更新为自增ID

        # 8. 插入病历主表
        record = models['record'](
            name=req_data['name'],
            age=int(req_data['age']),
            gender=req_data['gender'],
            id_card=req_data['id_card'],
            phone=req_data['phone'],
            doctor_code=doctor_id
        )
        db.session.add(record)
        print(2)
        # 9. 插入病历-病种表
        disease_record = models['record_disease'](
            medical_record_num=medical_record_num,
            disease_code=req_data['diagnosis_name_code']
        )
        db.session.add(disease_record)
        print(3)
        # 10. 插入病历-数据项表（从请求和疾病数据中提取字段）
        record_data_kwargs = {'medical_record_num': medical_record_num}

        for col in models['record_data'].__table__.columns:
            col_name = col.name
            if col_name in ['id', 'medical_record_num', 'created_time', 'updated_time']:
                continue
            # if req_data.get(col_name):
            req_value = req_data.get(col_name)
            from sqlalchemy.types import String, Numeric
            if isinstance(col.type, String):
                if req_value:
                    record_data_kwargs[col_name] = str(req_value)
                else:
                    record_data_kwargs[col_name]=''
            else:
                from decimal import Decimal
                if req_value:
                    decimal_value = Decimal(str(req_value)).quantize(Decimal('0.00'))  # 强制保留2位小数
                    record_data_kwargs[col_name] = decimal_value
                else:
                    record_data_kwargs[col_name]=Decimal('0.00')

        record_data = models['record_data'](**record_data_kwargs)
        db.session.add(record_data)
        print(4)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '添加成功'})

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'数据库操作失败：{str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'服务器错误：{str(e)}'}), 500
