from flask import Blueprint, jsonify, request
from models import db, UserVisit

# 创建名为'visits'的蓝图
trust_compute_bp = Blueprint('trust_value', __name__)


@trust_compute_bp.route('/get_trust_value/<user_id>', methods=['GET'])
def record_visit(user_id):
    # 查找用户记录，如果不存在则创建
    user_visit = UserVisit.query.filter_by(user_id=user_id).first()

    if not user_visit:
        # 创建新用户记录
        user_visit = UserVisit(user_id=user_id)
        db.session.add(user_visit)

    # 增加访问次数
    user_visit.increment_visit()
    db.session.commit()

    # 返回用户访问信息
    return jsonify({
        'user_id': user_visit.user_id,
        'visit_count': user_visit.visit_count,
        'last_visit': user_visit.last_visit.isoformat()
    }), 200


@trust_compute_bp.route('/stats/<user_id>', methods=['GET'])
def get_stats(user_id):
    """获取特定用户的访问统计信息"""
    user_visit = UserVisit.query.filter_by(user_id=user_id).first()

    if not user_visit:
        return jsonify({
            'error': 'User not found',
            'message': f'No visit records for user {user_id}'
        }), 404

    return jsonify({
        'user_id': user_visit.user_id,
        'visit_count': user_visit.visit_count,
        'first_visit': user_visit.created_at.isoformat(),
        'last_visit': user_visit.last_visit.isoformat()
    }), 200


@trust_compute_bp.route('/stats', methods=['GET'])
def get_all_stats():
    """获取所有用户的访问统计信息（分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = UserVisit.query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    return jsonify({
        'users': [{
            'user_id': user.user_id,
            'visit_count': user.visit_count,
            'last_visit': user.last_visit.isoformat()
        } for user in users],
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200
