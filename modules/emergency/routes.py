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

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/emergency_rate', methods=['POST'])
def get_health_records():
    """
    根据身份证号查询24小时健康记录（hr、sys、dia数据）
    请求参数：id_card（查询参数）
    返回：包含所有时间点的心率、收缩压、舒张压数据
    """
    try:
        # 获取并验证身份证号参数
        req_data = request.get_json()
        id_card = req_data['id_card']
        # print(id_card)
        # 查询数据库中匹配的健康记录
        records = HealthRecord24h.query.filter_by(id_card=id_card).all()
        if not records:
            return jsonify({
                'code': 404,
                'message': f'未找到身份证号为 {id_card} 的健康记录',
                'data': None
            }), 404

        # 提取所有记录中的hr、sys、dia字段（过滤其他无关字段）
        result = []
        for record in records:
            record_dict = record.to_dict()
            # 筛选出所有以hr_、sys_、dia_开头的字段
            health_data = {
                key: value for key, value in record_dict.items()
                if key.startswith(('hr_', 'sys_', 'dia_', 'spo2_'))
            }
            # 补充记录ID和时间（可选，便于定位记录）
            health_data['record_id'] = record_dict['id']
            health_data['created_time'] = record_dict['created_time']
            result.append(health_data)
        # print(result)
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': {
                'id_card': id_card,
                'record_count': len(result),
                'records': result
            }
        }), 200

    except Exception as e:
        # 捕获数据库查询等异常
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'服务器错误：{str(e)}',
            'data': None
        }), 500