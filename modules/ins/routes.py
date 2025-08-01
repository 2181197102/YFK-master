from flask import Blueprint, request, jsonify
from models import ins_record_disease, ins_record_data
from utils.extensions import db
from flask import current_app

# 创建蓝图
medical_record_bp = Blueprint('medical_record', __name__)


@medical_record_bp.route('/get_record_by_disease', methods=['POST'])
def get_record_by_disease():
    """
    根据多个疾病代码查询对应的病历数据
    请求体: JSON格式，包含 disease_codes 数组（支持多选）
    返回: 所有匹配的病历数据或错误信息
    """
    try:
        # 解析请求体中的JSON数据
        request_data = request.get_json()

        # 检查JSON解析是否成功
        if not request_data:
            return jsonify({
                'success': False,
                'message': '请求体不是有效的JSON格式'
            }), 400

        # 提取disease_codes（从JSON中获取数组）
        disease_codes = request_data.get('disease_codes')
        # 验证参数格式：必须是非空列表
        if not disease_codes or not isinstance(disease_codes, list) or len(disease_codes) == 0:
            return jsonify({
                'success': False,
                'message': 'JSON数据中缺少必要字段: disease_codes（需为非空数组）'
            }), 400

        # 1. 根据多个disease_code查询ins_record_disease表，获取所有匹配的medical_record_num
        # 使用in_()方法实现"多值匹配"
        disease_records = ins_record_disease.query.filter(
            ins_record_disease.disease_code.in_(disease_codes)
        ).all()

        # 检查是否存在对应的记录
        if not disease_records:
            return jsonify({
                'success': False,
                'message': f'未找到与disease_codes {disease_codes} 匹配的记录'
            }), 404

        # 提取所有相关的medical_record_num（去重处理，避免重复查询）
        medical_record_nums = list({
            record.medical_record_num for record in disease_records
        })

        # 2. 根据medical_record_num查询ins_record_data表
        data_records = ins_record_data.query.filter(
            ins_record_data.medical_record_num.in_(medical_record_nums)
        ).all()

        # 检查是否存在对应的数据记录
        if not data_records:
            return jsonify({
                'success': False,
                'message': f'未找到与disease_codes {disease_codes} 关联的病历数据'
            }), 404

        # 转换为字典列表返回，包含匹配的疾病代码信息
        result = {
            'success': True,
            'requested_disease_codes': disease_codes,  # 返回请求的疾病代码
            'matched_medical_record_count': len(medical_record_nums),  # 匹配的病历编号数量
            'data_count': len(data_records),  # 返回的数据记录数量
            'data': [record.to_dict() for record in data_records]
        }

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"查询失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}'
        }), 500
