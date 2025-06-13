from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import (db, User, AccessSuccessTracker, OperationBehaviorTracker,
                           DataSensitivityTracker, AccessTimeTracker, AccessLocationTracker)
from modules.auth.decorators import role_required
from datetime import datetime
from sqlalchemy import func
import uuid

data_mgmt_bp = Blueprint('data_management', __name__)


@data_mgmt_bp.route('/access-success/user/<user_id>', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER') # 注意不要写成 @role_required(['ADMIN', 'RESEARCHER']) ，这样写代表一个人需要同时拥有这两个角色才可以访问该请求
def get_user_access_success(user_id):
    """获取用户的访问成功率数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = AccessSuccessTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(AccessSuccessTracker.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(AccessSuccessTracker.created_at <= datetime.fromisoformat(end_date))

        records = query.order_by(AccessSuccessTracker.created_at.desc()).all()

        for record in records:
            print(record.to_dict())

        data = [{
            'id': record.id,
            'num_as': record.ast_num_as,
            'num_af': record.ast_num_af,
            'success_rate': record.ast_num_as / (record.ast_num_as + record.ast_num_af) if (
                                                                                                       record.ast_num_as + record.ast_num_af) > 0 else 0,
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat() if record.updated_at else None
        } for record in records]

        return jsonify({'access_success_data': data}), 200

    except Exception as e:
        current_app.logger.error(f'Get access success error: {str(e)}')
        return jsonify({'error': '获取访问成功率数据失败'}), 500


@data_mgmt_bp.route('/access-success', methods=['POST'])
@jwt_required()
def update_access_success():
    """更新访问成功率数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        user_id = data.get('user_id', current_user_id)
        num_as = data.get('num_as', 0)
        num_af = data.get('num_af', 0)

        # 检查是否存在今天的记录
        today = datetime.utcnow().date()
        existing_record = AccessSuccessTracker.query.filter(
            AccessSuccessTracker.user_id == user_id,
            func.date(AccessSuccessTracker.created_at) == today
        ).first()

        if existing_record:
            # 更新现有记录
            existing_record.num_as += num_as
            existing_record.num_af += num_af
            existing_record.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            record = AccessSuccessTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_as=num_as,
                num_af=num_af
            )
            db.session.add(record)

        db.session.commit()
        return jsonify({'message': '访问成功率数据更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update access success error: {str(e)}')
        return jsonify({'error': '更新访问成功率数据失败'}), 500


@data_mgmt_bp.route('/operation-behavior/user/<user_id>', methods=['GET'])
@jwt_required()
@role_required(['管理员', '科研人员'])
def get_user_operation_behavior(user_id):
    """获取用户的操作行为数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = OperationBehaviorTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(OperationBehaviorTracker.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(OperationBehaviorTracker.created_at <= datetime.fromisoformat(end_date))

        records = query.order_by(OperationBehaviorTracker.created_at.desc()).all()

        data = [{
            'id': record.id,
            'num_view': record.num_view,
            'num_copy': record.num_copy,
            'num_download': record.num_download,
            'num_add': record.num_add,
            'num_revise': record.num_revise,
            'num_delete': record.num_delete,
            'ob_a': record.ob_a,
            'ob_b': record.ob_b,
            'ob_c': record.ob_c,
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat() if record.updated_at else None
        } for record in records]

        return jsonify({'operation_behavior_data': data}), 200

    except Exception as e:
        current_app.logger.error(f'Get operation behavior error: {str(e)}')
        return jsonify({'error': '获取操作行为数据失败'}), 500


@data_mgmt_bp.route('/operation-behavior', methods=['POST'])
@jwt_required()
def update_operation_behavior():
    """更新操作行为数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        user_id = data.get('user_id', current_user_id)

        # 检查是否存在今天的记录
        today = datetime.utcnow().date()
        existing_record = OperationBehaviorTracker.query.filter(
            OperationBehaviorTracker.user_id == user_id,
            func.date(OperationBehaviorTracker.created_at) == today
        ).first()

        if existing_record:
            # 更新现有记录
            existing_record.num_view += data.get('num_view', 0)
            existing_record.num_copy += data.get('num_copy', 0)
            existing_record.num_download += data.get('num_download', 0)
            existing_record.num_add += data.get('num_add', 0)
            existing_record.num_revise += data.get('num_revise', 0)
            existing_record.num_delete += data.get('num_delete', 0)
            existing_record.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            record = OperationBehaviorTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_view=data.get('num_view', 0),
                num_copy=data.get('num_copy', 0),
                num_download=data.get('num_download', 0),
                num_add=data.get('num_add', 0),
                num_revise=data.get('num_revise', 0),
                num_delete=data.get('num_delete', 0),
                ob_a=data.get('ob_a', 0.3),
                ob_b=data.get('ob_b', 0.3),
                ob_c=data.get('ob_c', 0.4)
            )
            db.session.add(record)

        db.session.commit()
        return jsonify({'message': '操作行为数据更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update operation behavior error: {str(e)}')
        return jsonify({'error': '更新操作行为数据失败'}), 500


@data_mgmt_bp.route('/data-sensitivity/user/<user_id>', methods=['GET'])
@jwt_required()
@role_required(['管理员', '科研人员'])
def get_user_data_sensitivity(user_id):
    """获取用户的数据敏感度数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = DataSensitivityTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(DataSensitivityTracker.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(DataSensitivityTracker.created_at <= datetime.fromisoformat(end_date))

        records = query.order_by(DataSensitivityTracker.created_at.desc()).all()

        data = [{
            'id': record.id,
            'num1': record.num1,
            'num2': record.num2,
            'num3': record.num3,
            'num4': record.num4,
            'ds_a': record.ds_a,
            'ds_b': record.ds_b,
            'ds_c': record.ds_c,
            'ds_d': record.ds_d,
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat() if record.updated_at else None
        } for record in records]

        return jsonify({'data_sensitivity_data': data}), 200

    except Exception as e:
        current_app.logger.error(f'Get data sensitivity error: {str(e)}')
        return jsonify({'error': '获取数据敏感度数据失败'}), 500


@data_mgmt_bp.route('/data-sensitivity', methods=['POST'])
@jwt_required()
def update_data_sensitivity():
    """更新数据敏感度数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        user_id = data.get('user_id', current_user_id)

        # 检查是否存在今天的记录
        today = datetime.utcnow().date()
        existing_record = DataSensitivityTracker.query.filter(
            DataSensitivityTracker.user_id == user_id,
            func.date(DataSensitivityTracker.created_at) == today
        ).first()

        if existing_record:
            # 更新现有记录
            existing_record.num1 += data.get('num1', 0)
            existing_record.num2 += data.get('num2', 0)
            existing_record.num3 += data.get('num3', 0)
            existing_record.num4 += data.get('num4', 0)
            existing_record.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            record = DataSensitivityTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num1=data.get('num1', 0),
                num2=data.get('num2', 0),
                num3=data.get('num3', 0),
                num4=data.get('num4', 0),
                ds_a=data.get('ds_a', 1.0),
                ds_b=data.get('ds_b', 1.0),
                ds_c=data.get('ds_c', 1.0),
                ds_d=data.get('ds_d', 1.0)
            )
            db.session.add(record)

        db.session.commit()
        return jsonify({'message': '数据敏感度数据更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update data sensitivity error: {str(e)}')
        return jsonify({'error': '更新数据敏感度数据失败'}), 500


@data_mgmt_bp.route('/access-period/user/<user_id>', methods=['GET'])
@jwt_required()
@role_required(['管理员', '科研人员'])
def get_user_access_period(user_id):
    """获取用户的访问时间数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = AccessTimeTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(AccessTimeTracker.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(AccessTimeTracker.created_at <= datetime.fromisoformat(end_date))

        records = query.order_by(AccessTimeTracker.created_at.desc()).all()

        data = [{
            'id': record.id,
            'num_ni': record.num_ni,
            'num_ui': record.num_ui,
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat() if record.updated_at else None
        } for record in records]

        return jsonify({'access_period_data': data}), 200

    except Exception as e:
        current_app.logger.error(f'Get access period error: {str(e)}')
        return jsonify({'error': '获取访问时间数据失败'}), 500


@data_mgmt_bp.route('/access-period', methods=['POST'])
@jwt_required()
def update_access_period():
    """更新访问时间数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        user_id = data.get('user_id', current_user_id)

        today = datetime.utcnow().date()
        existing_record = AccessTimeTracker.query.filter(
            AccessTimeTracker.user_id == user_id,
            func.date(AccessTimeTracker.created_at) == today
        ).first()

        if existing_record:
            existing_record.num_ni += data.get('num_ni', 0)
            existing_record.num_ui += data.get('num_ui', 0)
            existing_record.updated_at = datetime.utcnow()
        else:
            record = AccessTimeTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_ni=data.get('num_ni', 0),
                num_ui=data.get('num_ui', 0)
            )
            db.session.add(record)

        db.session.commit()
        return jsonify({'message': '访问时间数据更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update access period error: {str(e)}')
        return jsonify({'error': '更新访问时间数据失败'}), 500


@data_mgmt_bp.route('/access-location/user/<user_id>', methods=['GET'])
@jwt_required()
@role_required(['管理员', '科研人员'])
def get_user_access_location(user_id):
    """获取用户的访问IP数据"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = AccessLocationTracker.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(AccessLocationTracker.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(AccessLocationTracker.created_at <= datetime.fromisoformat(end_date))

        records = query.order_by(AccessLocationTracker.created_at.desc()).all()

        data = [{
            'id': record.id,
            'num_nd': record.num_nd,
            'num_ad': record.num_ad,
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat() if record.updated_at else None
        } for record in records]

        return jsonify({'access_location_data': data}), 200

    except Exception as e:
        current_app.logger.error(f'Get access location error: {str(e)}')
        return jsonify({'error': '获取访问IP数据失败'}), 500


@data_mgmt_bp.route('/access-location', methods=['POST'])
@jwt_required()
def update_access_location():
    """更新访问IP数据"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        user_id = data.get('user_id', current_user_id)

        today = datetime.utcnow().date()
        existing_record = AccessLocationTracker.query.filter(
            AccessLocationTracker.user_id == user_id,
            func.date(AccessLocationTracker.created_at) == today
        ).first()

        if existing_record:
            existing_record.num_nd += data.get('num_nd', 0)
            existing_record.num_ad += data.get('num_ad', 0)
            existing_record.updated_at = datetime.utcnow()
        else:
            record = AccessLocationTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_nd=data.get('num_nd', 0),
                num_ad=data.get('num_ad', 0)
            )
            db.session.add(record)

        db.session.commit()
        return jsonify({'message': '访问IP数据更新成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update access location error: {str(e)}')
        return jsonify({'error': '更新访问IP数据失败'}), 500