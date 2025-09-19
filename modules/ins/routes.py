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
INSTITUTION_MODEL_MAP: Dict[str, Type[ins1_record_data | ins2_record_data | ins3_record_data]] = {
    'ins1': ins1_record_data,
    'ins2': ins2_record_data,
    'ins3': ins3_record_data
}


def get_valid_fields(model: Type[ins1_record_data]) -> List[str]:
    """获取模型中所有有效的数据字段（排除基础字段）"""
    base_fields = ['id', 'medical_record_num', 'created_time', 'updated_time']
    model_columns = model.__table__.columns.keys()
    return [field for field in model_columns if field not in base_fields]


def query_institution_data(
        model: Type[ins1_record_data],
        data_codes: List[str],
        nums: int
) -> List[Dict]:
    """查询指定机构表中的数据并格式化结果"""
    # 查询前nums条数据，按ID排序确保结果一致性
    records = model.query.order_by(model.id).limit(nums).all()
    # print(records)
    # 格式化结果，只包含需要的字段
    result = []
    for record in records:
        record_data = {
            'medical_record_num': record.medical_record_num,
            'institution': model.__tablename__.split('_')[0]  # 提取机构标识
        }
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

    # 3. 多机构数据查询
    all_results = []
    for ins in institutions:
        model = INSTITUTION_MODEL_MAP[ins]
        ins_results = query_institution_data(model, data_codes, nums)
        all_results.extend(ins_results)
    # print('*********************')
    # print(all_results)
    # 4. 返回查询结果
    return jsonify({
        "status": "success",
        "message": f"成功查询到{len(all_results)}条数据",
        "total_count": len(all_results),
        "institutions": institutions,
        "data_codes": data_codes,
        "requested_nums": nums,
        "client_ip": client_ip,
        "is_whitelist_ip": is_whitelist_ip,
        "is_working_time": is_working_time_flag,
        "results": all_results
    }), 200


@medical_record_bp.route('/get_mypatients', methods=['GET'])
@jwt_required()
def get_mypatient():
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取客户端IP并检查白名单
        client_ip = get_client_ip()
        is_whitelist_ip = is_ip_in_whitelist(client_ip)
        
        # 检查工作时间
        is_working_time_flag = is_working_time()
        
        # 更新访问追踪统计
        update_access_tracking(user_id, client_ip, is_working_time_flag, is_whitelist_ip)

        # 查询用户信息获取姓名
        user_info = User.query.filter_by(id=user_id).first()
        if not user_info:
            return jsonify({
                'code': 404,
                'msg': '用户不存在'
            }), 404

        doctor_name = user_info.name

        # 查询用户所属机构
        user_group = UserGroupRelation.query.filter_by(user_id=user_id).first()
        if not user_group:
            return jsonify({
                'code': 403,
                'msg': '未分配机构权限'
            }), 403

        ins = user_group.group_id

        # 根据机构ID选择对应的模型
        if ins == 1:
            ins_record = ins1_record
            ins_record_disease = ins1_record_disease
            ins_record_data = ins1_record_data
            ins_doctor_record = ins1_doctor_record
        elif ins == 2:
            ins_record = ins2_record
            ins_record_disease = ins2_record_disease
            ins_record_data = ins2_record_data
            ins_doctor_record = ins2_doctor_record
        elif ins == 3:
            ins_record = ins3_record
            ins_record_disease = ins3_record_disease
            ins_record_data = ins3_record_data
            ins_doctor_record = ins3_doctor_record
        else:
            return jsonify({
                'code': 400,
                'msg': '无效的机构ID'
            }), 400

        # 查询该医生名下的所有病历记录
        doctor_records = ins_doctor_record.query.filter_by(doctor_name=doctor_name).all()
        if not doctor_records:
            return jsonify({
                'code': 200,
                'msg': '未查询到患者数据',
                'data': []
            })

        # 处理患者数据
        patients = []
        for dr in doctor_records:
            # 获取患者基本信息
            patient_info = ins_record.query.filter_by(id_card=dr.patient_id_num).first()
            if not patient_info:
                continue

            # 获取患者疾病信息
            disease_info = ins_record_disease.query.filter_by(
                medical_record_num=dr.medical_record_num
            ).first()

            # 获取患者数据项信息
            data_info = ins_record_data.query.filter_by(
                medical_record_num=dr.medical_record_num
            ).first()

            # 组装患者数据
            patient_data = {
                'medical_record_num': dr.medical_record_num,
                'patient_name': dr.patient_name,
                'patient_id_num': dr.patient_id_num,
                'basic_info': {
                    'name': patient_info.name,
                    'age': patient_info.age,
                    'gender': patient_info.gender,
                    'doctor_code': patient_info.doctor_code
                },
                'disease_code': disease_info.disease_code if disease_info else None,
                'record_timestamps': {
                    'created_time': patient_info.created_time.isoformat() if patient_info.created_time else None,
                    'updated_time': patient_info.updated_time.isoformat() if patient_info.updated_time else None
                }
            }
            # print(patient_data)
            # 添加数据项（如果存在）
            if data_info:
                patient_data['data_items'] = {
                    'data_code1': data_info.data_code1,
                    'data_code2': data_info.data_code2,
                    'data_code3': data_info.data_code3,
                    'data_code4': data_info.data_code4,
                    'data_code5': data_info.data_code5,
                    'data_code6': data_info.data_code6,
                    'data_code7': data_info.data_code7,
                    'data_code8': data_info.data_code8,
                    'data_code9': data_info.data_code9
                }

            patients.append(patient_data)

        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'client_ip': client_ip,
            'is_whitelist_ip': is_whitelist_ip,
            'is_working_time': is_working_time_flag,
            'data': {
                'doctor_name': doctor_name,
                'institution_id': ins,
                'patient_count': len(patients),
                'patients': patients
            }
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'查询失败: {str(e)}'
        }), 500


# 机构模型映射
INSTITUTION_MODELS = {
    1: {
        'record': ins1_record,
        'record_disease': ins1_record_disease,
        'record_data': ins1_record_data,
        'name': '机构1'
    },
    2: {
        'record': ins2_record,
        'record_disease': ins2_record_disease,
        'record_data': ins2_record_data,
        'name': '机构2'
    },
    3: {
        'record': ins3_record,
        'record_disease': ins3_record_disease,
        'record_data': ins3_record_data,
        'name': '机构3'
    }
}


@medical_record_bp.route("/get_patient/<user_id>", methods=["GET"])
@jwt_required()
def get_patient(user_id):
    """
    根据患者身份证号查询病历信息
    user_id: 患者的身份证号
    """
    try:
        current_user_id = get_jwt_identity()
        
        # 获取客户端IP并检查白名单
        client_ip = get_client_ip()
        is_whitelist_ip = is_ip_in_whitelist(client_ip)
        
        # 检查工作时间
        is_working_time_flag = is_working_time()
        
        # 更新访问追踪统计
        update_access_tracking(current_user_id, client_ip, is_working_time_flag, is_whitelist_ip)
        
        accessible_ins_ids = [1, 2, 3]

        # 2. 遍历所有可访问的机构查询记录
        all_institution_records = []
        for ins_id in accessible_ins_ids:
            if ins_id not in INSTITUTION_MODELS:
                continue  # 跳过无效机构ID

            models = INSTITUTION_MODELS[ins_id]
            ins_name = models['name']

            # 3. 第一步：通过身份证号在病历表中查询记录，获取medical_record_num关联
            # 注意：根据数据模型，insX_record表中没有直接的medical_record_num字段
            # 这里通过insX_doctor_record表关联获取病历号（因为只有该表有medical_record_num）
            # 先查询该机构中该患者的医生关联记录
            doctor_record_model = {
                1: ins1_doctor_record,
                2: ins2_doctor_record,
                3: ins3_doctor_record
            }.get(ins_id)

            if not doctor_record_model:
                continue

            # 通过患者身份证号查询医生-病历关联记录，获取medical_record_num
            doctor_records = doctor_record_model.query.filter_by(
                patient_id_num=user_id
            ).all()

            if not doctor_records:
                continue  # 该机构无此患者的关联记录

            # 4. 处理每条病历记录
            ins_records = []
            for dr in doctor_records:
                medical_record_num = dr.medical_record_num

                # 4.1 查询患者基本信息（insX_record）
                patient_basic = models['record'].query.filter_by(
                    id_card=user_id
                ).first()

                # 4.2 查询病种信息（insX_record_disease）
                disease_info = models['record_disease'].query.filter_by(
                    medical_record_num=medical_record_num
                ).first()

                # 4.3 查询数据项信息（insX_record_data）
                data_info = models['record_data'].query.filter_by(
                    medical_record_num=medical_record_num
                ).first()

                # 4.4 查询疾病对应的数据项编码
                related_data_codes = []
                if disease_info:
                    related_data = Disease_data.query.filter_by(
                        disease_code=disease_info.disease_code
                    ).all()
                    related_data_codes = [item.data_code for item in related_data]

                # 组装记录信息
                ins_records.append({
                    "medical_record_num": medical_record_num,
                    "patient_basic": patient_basic.to_dict() if patient_basic else None,
                    "disease_info": disease_info.to_dict() if disease_info else None,
                    "data_info": data_info.to_dict() if data_info else None,
                    "related_data_codes": related_data_codes,
                    "doctor_info": {
                        "doctor_name": dr.doctor_name,
                        "doctor_code": dr.doctor_code
                    },
                    "record_time": {
                        "created_time": dr.created_time.isoformat() if dr.created_time else None,
                        "updated_time": dr.updated_time.isoformat() if dr.updated_time else None
                    }
                })

            # 5. 汇总该机构的记录
            all_institution_records.append({
                "institution_id": ins_id,
                "institution_name": ins_name,
                "record_count": len(ins_records),
                "records": ins_records
            })

        # 6. 返回结果
        if not all_institution_records:
            return jsonify({
                "code": 200,
                "msg": "未查询到该患者的任何病历记录",
                "data": []
            })

        return jsonify({
            "code": 200,
            "client_ip": client_ip,
            "is_whitelist_ip": is_whitelist_ip,
            "is_working_time": is_working_time_flag,
            "data": {
                "patient_id_card": user_id,
                "total_institutions": len(all_institution_records),
                "total_records": sum(ins["record_count"] for ins in all_institution_records),
                "institution_records": all_institution_records
            }
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"数据库错误: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"}), 500


@medical_record_bp.route('/disease-data-codes', methods=['GET'])
def get_disease_data_codes():
    """
    获取每个disease_code对应的所有data_code
    支持可选参数disease_code进行过滤，例如:
    /disease-data-codes?disease_code=A000&disease_code=B159
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

    # 整理结果：按disease_code分组，收集对应的data_code
    disease_data_map = defaultdict(list)
    for item in results:
        # 确保每个data_code在列表中唯一
        if item.data_code not in disease_data_map[item.disease_code]:
            disease_data_map[item.disease_code].append(item.data_code)
    # print(disease_data_map)
    # 转换为有序字典并排序
    sorted_result = {
        disease_code: sorted(data_codes)
        for disease_code, data_codes in sorted(disease_data_map.items())
    }
    # print(sorted_result)
    return jsonify({
        'status': 'success',
        'data': sorted_result,
        'message': f"共找到{len(sorted_result)}个疾病代码对应的{sum(len(v) for v in sorted_result.values())}个数据项代码"
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
        'num2': ds.ds_num2 if ds else 0,
        'num3': ds.ds_num3 if ds else 0,
        'num4': ds.ds_num4 if ds else 0
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
        if val in (0.6, 0.8):
            ds.ds_num4 += 1
        elif val == 0.4:
            ds.ds_num3 += 1
        elif val == 0.2:
            ds.ds_num2 += 1
        elif val == 0.1:
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
        'sensitive': sensitive
    }), 200

