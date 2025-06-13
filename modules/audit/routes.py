from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.data_management.models import db, AccessSuccessTracker, OperationBehaviorTracker, DataSensitivityTracker, AccessTimeTracker, AccessLocationTracker
from modules.auth.decorators import admin_required, researcher_or_admin
import uuid

audit_bp = Blueprint('audit', __name__)


@audit_bp.route('/record-access', methods=['POST'])
@jwt_required()
def record_access():
    """记录访问行为"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        # 记录访问成功率
        access_success = data.get('success', True)
        ast_record = AccessSuccessTracker.query.filter_by(user_id=user_id).first()

        if not ast_record:
            ast_record = AccessSuccessTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_as=1 if access_success else 0,
                num_af=0 if access_success else 1
            )
            db.session.add(ast_record)
        else:
            if access_success:
                ast_record.num_as += 1
            else:
                ast_record.num_af += 1

        # 记录操作行为
        operation_type = data.get('operation_type', 'view')
        ob_record = OperationBehaviorTracker.query.filter_by(user_id=user_id).first()

        if not ob_record:
            ob_record = OperationBehaviorTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_view=1 if operation_type == 'view' else 0,
                num_copy=1 if operation_type == 'copy' else 0,
                num_download=1 if operation_type == 'download' else 0,
                num_add=1 if operation_type == 'add' else 0,
                num_revise=1 if operation_type == 'revise' else 0,
                num_delete=1 if operation_type == 'delete' else 0,
                a=0.3,
                b=0.3,
                c=0.4
            )
            db.session.add(ob_record)
        else:
            if operation_type == 'view':
                ob_record.num_view += 1
            elif operation_type == 'copy':
                ob_record.num_copy += 1
            elif operation_type == 'download':
                ob_record.num_download += 1
            elif operation_type == 'add':
                ob_record.num_add += 1
            elif operation_type == 'revise':
                ob_record.num_revise += 1
            elif operation_type == 'delete':
                ob_record.num_delete += 1

        # 记录数据敏感度
        sensitivity_level = data.get('sensitivity_level', 1)
        ds_record = DataSensitivityTracker.query.filter_by(user_id=user_id).first()

        if not ds_record:
            ds_record = DataSensitivityTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num1=1 if sensitivity_level == 1 else 0,
                num2=1 if sensitivity_level == 2 else 0,
                num3=1 if sensitivity_level == 3 else 0,
                num4=1 if sensitivity_level == 4 else 0,
                a=1.0,
                b=1.0,
                c=1.0,
                d=1.0
            )
            db.session.add(ds_record)
        else:
            if sensitivity_level == 1:
                ds_record.num1 += 1
            elif sensitivity_level == 2:
                ds_record.num2 += 1
            elif sensitivity_level == 3:
                ds_record.num3 += 1
            elif sensitivity_level == 4:
                ds_record.num4 += 1

        # 记录访问时间
        is_unusual_time = data.get('is_unusual_time', False)
        ap_record = AccessTimeTracker.query.filter_by(user_id=user_id).first()

        if not ap_record:
            ap_record = AccessTimeTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_ni=0 if is_unusual_time else 1,
                num_ui=1 if is_unusual_time else 0
            )
            db.session.add(ap_record)
        else:
            if is_unusual_time:
                ap_record.num_ui += 1
            else:
                ap_record.num_ni += 1

        # 记录访问IP
        is_abnormal_ip = data.get('is_abnormal_ip', False)
        at_record = AccessLocationTracker.query.filter_by(user_id=user_id).first()

        if not at_record:
            at_record = AccessLocationTracker(
                id=str(uuid.uuid4()),
                user_id=user_id,
                num_nd=0 if is_abnormal_ip else 1,
                num_ad=1 if is_abnormal_ip else 0
            )
            db.session.add(at_record)
        else:
            if is_abnormal_ip:
                at_record.num_ad += 1
            else:
                at_record.num_nd += 1

        db.session.commit()

        return jsonify({'message': '访问记录成功'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Record access error: {str(e)}')
        return jsonify({'error': '记录访问失败'}), 500


@audit_bp.route('/user-stats/<user_id>', methods=['GET'])
@researcher_or_admin
def get_user_stats(user_id):
    """获取用户统计信息"""
    try:
        # 访问成功率
        ast = AccessSuccessTracker.query.filter_by(user_id=user_id).first()
        ast_data = {
            'num_as': ast.num_as if ast else 0,
            'num_af': ast.num_af if ast else 0
        }

        # 操作行为
        ob = OperationBehaviorTracker.query.filter_by(user_id=user_id).first()
        ob_data = {
            'num_view': ob.num_view if ob else 0,
            'num_copy': ob.num_copy if ob else 0,
            'num_download': ob.num_download if ob else 0,
            'num_add': ob.num_add if ob else 0,
            'num_revise': ob.num_revise if ob else 0,
            'num_delete': ob.num_delete if ob else 0
        }

        # 数据敏感度
        ds = DataSensitivityTracker.query.filter_by(user_id=user_id).first()
        ds_data = {
            'num1': ds.num1 if ds else 0,
            'num2': ds.num2 if ds else 0,
            'num3': ds.num3 if ds else 0,
            'num4': ds.num4 if ds else 0
        }

        # 访问时间
        ap = AccessTimeTracker.query.filter_by(user_id=user_id).first()
        ap_data = {
            'num_ni': ap.num_ni if ap else 0,
            'num_ui': ap.num_ui if ap else 0
        }

        # 访问IP
        at = AccessLocationTracker.query.filter_by(user_id=user_id).first()
        at_data = {
            'num_nd': at.num_nd if at else 0,
            'num_ad': at.num_ad if at else 0
        }

        return jsonify({
            'user_id': user_id,
            'access_success': ast_data,
            'operation_behavior': ob_data,
            'data_sensitivity': ds_data,
            'access_period': ap_data,
            'access_location': at_data
        }), 200

    except Exception as e:
        current_app.logger.error(f'Get user stats error: {str(e)}')
        return jsonify({'error': '获取用户统计信息失败'}), 500


@audit_bp.route('/my-stats', methods=['GET'])
@jwt_required()
def get_my_stats():
    """获取当前用户统计信息"""
    user_id = get_jwt_identity()
    return get_user_stats(user_id)


@audit_bp.route('/all-stats', methods=['GET'])
@admin_required
def get_all_stats():
    """获取所有用户统计信息"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 获取所有用户的访问成功率记录
        ast_records = AccessSuccessTracker.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        stats_list = []
        for ast in ast_records.items:
            # 获取对应的其他记录
            ob = OperationBehaviorTracker.query.filter_by(user_id=ast.user_id).first()
            ds = DataSensitivityTracker.query.filter_by(user_id=ast.user_id).first()
            ap = AccessTimeTracker.query.filter_by(user_id=ast.user_id).first()
            at = AccessLocationTracker.query.filter_by(user_id=ast.user_id).first()

            stats_list.append({
                'user_id': ast.user_id,
                'access_success': {
                    'num_as': ast.num_as,
                    'num_af': ast.num_af
                },
                'operation_behavior': {
                    'num_view': ob.num_view if ob else 0,
                    'num_copy': ob.num_copy if ob else 0,
                    'num_download': ob.num_download if ob else 0,
                    'num_add': ob.num_add if ob else 0,
                    'num_revise': ob.num_revise if ob else 0,
                    'num_delete': ob.num_delete if ob else 0
                },
                'data_sensitivity': {
                    'num1': ds.num1 if ds else 0,
                    'num2': ds.num2 if ds else 0,
                    'num3': ds.num3 if ds else 0,
                    'num4': ds.num4 if ds else 0
                },
                'access_period': {
                    'num_ni': ap.num_ni if ap else 0,
                    'num_ui': ap.num_ui if ap else 0
                },
                'access_location': {
                    'num_nd': at.num_nd if at else 0,
                    'num_ad': at.num_ad if at else 0
                }
            })

        return jsonify({
            'stats': stats_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': ast_records.total,
                'pages': ast_records.pages,
                'has_next': ast_records.has_next,
                'has_prev': ast_records.has_prev
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f'Get all stats error: {str(e)}')
        return jsonify({'error': '获取统计信息失败'}), 500