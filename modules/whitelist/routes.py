# modules/whitelist/routes.py
"""
白名单管理API路由
"""

from flask import Blueprint, request, jsonify
from models import IPWhitelist, WorkingTimeWhitelist
from utils.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, time
from typing import List, Dict, Any


# 创建蓝图
whitelist_bp = Blueprint('whitelist', __name__)


# ==================== IP白名单管理 ====================

@whitelist_bp.route('/ip-whitelist', methods=['GET'])
@jwt_required()
def get_ip_whitelist():
    """获取IP白名单列表"""
    try:
        whitelist_ips = IPWhitelist.query.order_by(IPWhitelist.created_time.desc()).all()
        
        result = []
        for ip_record in whitelist_ips:
            result.append(ip_record.to_dict())
        
        return jsonify({
            'code': 200,
            'msg': '获取成功',
            'data': result,
            'total': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取IP白名单失败: {str(e)}'
        }), 500


@whitelist_bp.route('/ip-whitelist', methods=['POST'])
@jwt_required()
def add_ip_whitelist():
    """添加IP白名单"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('ip_address'):
            return jsonify({
                'code': 400,
                'msg': 'IP地址不能为空'
            }), 400
        
        # 检查IP是否已存在
        existing_ip = IPWhitelist.query.filter_by(ip_address=data['ip_address']).first()
        if existing_ip:
            return jsonify({
                'code': 400,
                'msg': '该IP地址已存在于白名单中'
            }), 400
        
        # 创建新记录
        ip_record = IPWhitelist(
            ip_address=data['ip_address'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(ip_record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '添加成功',
            'data': ip_record.to_dict()
        })
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'数据库错误: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'添加IP白名单失败: {str(e)}'
        }), 500


@whitelist_bp.route('/ip-whitelist/<int:ip_id>', methods=['PUT'])
@jwt_required()
def update_ip_whitelist(ip_id):
    """更新IP白名单"""
    try:
        ip_record = IPWhitelist.query.get(ip_id)
        if not ip_record:
            return jsonify({
                'code': 404,
                'msg': 'IP白名单记录不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'ip_address' in data:
            # 检查新IP是否与其他记录冲突
            existing_ip = IPWhitelist.query.filter(
                IPWhitelist.ip_address == data['ip_address'],
                IPWhitelist.id != ip_id
            ).first()
            if existing_ip:
                return jsonify({
                    'code': 400,
                    'msg': '该IP地址已存在于其他白名单记录中'
                }), 400
            ip_record.ip_address = data['ip_address']
        
        if 'description' in data:
            ip_record.description = data['description']
        
        if 'is_active' in data:
            ip_record.is_active = data['is_active']
        
        ip_record.updated_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': ip_record.to_dict()
        })
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'数据库错误: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'更新IP白名单失败: {str(e)}'
        }), 500


@whitelist_bp.route('/ip-whitelist/<int:ip_id>', methods=['DELETE'])
@jwt_required()
def delete_ip_whitelist(ip_id):
    """删除IP白名单"""
    try:
        ip_record = IPWhitelist.query.get(ip_id)
        if not ip_record:
            return jsonify({
                'code': 404,
                'msg': 'IP白名单记录不存在'
            }), 404
        
        db.session.delete(ip_record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'数据库错误: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'删除IP白名单失败: {str(e)}'
        }), 500


# ==================== 工作时间白名单管理 ====================

@whitelist_bp.route('/working-time-whitelist', methods=['GET'])
@jwt_required()
def get_working_time_whitelist():
    """获取工作时间白名单列表"""
    try:
        working_times = WorkingTimeWhitelist.query.order_by(
            WorkingTimeWhitelist.day_of_week,
            WorkingTimeWhitelist.start_time
        ).all()
        
        result = []
        for time_record in working_times:
            result.append(time_record.to_dict())
        
        return jsonify({
            'code': 200,
            'msg': '获取成功',
            'data': result,
            'total': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取工作时间白名单失败: {str(e)}'
        }), 500


@whitelist_bp.route('/working-time-whitelist', methods=['POST'])
@jwt_required()
def add_working_time_whitelist():
    """添加工作时间白名单"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'msg': f'{field}字段不能为空'
                }), 400
        
        # 验证星期几范围
        if not (0 <= data['day_of_week'] <= 6):
            return jsonify({
                'code': 400,
                'msg': '星期几必须在0-6之间（0为周日）'
            }), 400
        
        # 验证时间格式
        try:
            start_time = time.fromisoformat(data['start_time']) if isinstance(data['start_time'], str) else data['start_time']
            end_time = time.fromisoformat(data['end_time']) if isinstance(data['end_time'], str) else data['end_time']
        except ValueError:
            return jsonify({
                'code': 400,
                'msg': '时间格式错误，请使用HH:MM:SS格式'
            }), 400
        
        # 检查是否有重叠的时间段
        existing_times = WorkingTimeWhitelist.query.filter_by(
            day_of_week=data['day_of_week'],
            is_active=True
        ).all()
        
        for existing_time in existing_times:
            if (start_time < existing_time.end_time and end_time > existing_time.start_time):
                return jsonify({
                    'code': 400,
                    'msg': f'与现有工作时间段重叠: {existing_time.description}'
                }), 400
        
        # 创建新记录
        time_record = WorkingTimeWhitelist(
            day_of_week=data['day_of_week'],
            start_time=start_time,
            end_time=end_time,
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(time_record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '添加成功',
            'data': time_record.to_dict()
        })
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'数据库错误: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'添加工作时间白名单失败: {str(e)}'
        }), 500


@whitelist_bp.route('/working-time-whitelist/<int:time_id>', methods=['PUT'])
@jwt_required()
def update_working_time_whitelist(time_id):
    """更新工作时间白名单"""
    try:
        time_record = WorkingTimeWhitelist.query.get(time_id)
        if not time_record:
            return jsonify({
                'code': 404,
                'msg': '工作时间白名单记录不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'day_of_week' in data:
            if not (0 <= data['day_of_week'] <= 6):
                return jsonify({
                    'code': 400,
                    'msg': '星期几必须在0-6之间（0为周日）'
                }), 400
            time_record.day_of_week = data['day_of_week']
        
        if 'start_time' in data:
            try:
                start_time = time.fromisoformat(data['start_time']) if isinstance(data['start_time'], str) else data['start_time']
                time_record.start_time = start_time
            except ValueError:
                return jsonify({
                    'code': 400,
                    'msg': '开始时间格式错误，请使用HH:MM:SS格式'
                }), 400
        
        if 'end_time' in data:
            try:
                end_time = time.fromisoformat(data['end_time']) if isinstance(data['end_time'], str) else data['end_time']
                time_record.end_time = end_time
            except ValueError:
                return jsonify({
                    'code': 400,
                    'msg': '结束时间格式错误，请使用HH:MM:SS格式'
                }), 400
        
        if 'description' in data:
            time_record.description = data['description']
        
        if 'is_active' in data:
            time_record.is_active = data['is_active']
        
        time_record.updated_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '更新成功',
            'data': time_record.to_dict()
        })
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'数据库错误: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'更新工作时间白名单失败: {str(e)}'
        }), 500


@whitelist_bp.route('/working-time-whitelist/<int:time_id>', methods=['DELETE'])
@jwt_required()
def delete_working_time_whitelist(time_id):
    """删除工作时间白名单"""
    try:
        time_record = WorkingTimeWhitelist.query.get(time_id)
        if not time_record:
            return jsonify({
                'code': 404,
                'msg': '工作时间白名单记录不存在'
            }), 404
        
        db.session.delete(time_record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除成功'
        })
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': f'数据库错误: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'删除工作时间白名单失败: {str(e)}'
        }), 500


# ==================== 白名单状态检查 ====================

@whitelist_bp.route('/check-status', methods=['GET'])
@jwt_required()
def check_whitelist_status():
    """检查当前IP和时间是否在白名单中"""
    try:
        from modules.ins.routes import get_client_ip, is_ip_in_whitelist, is_working_time
        
        client_ip = get_client_ip()
        is_whitelist_ip = is_ip_in_whitelist(client_ip)
        is_working_time_flag = is_working_time()
        
        return jsonify({
            'code': 200,
            'msg': '检查成功',
            'data': {
                'client_ip': client_ip,
                'is_whitelist_ip': is_whitelist_ip,
                'is_working_time': is_working_time_flag,
                'access_allowed': is_whitelist_ip and is_working_time_flag
            }
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'检查白名单状态失败: {str(e)}'
        }), 500
