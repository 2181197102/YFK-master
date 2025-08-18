from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.data_management.models import db, UserAccessSuccessTracker, UserOperationBehaviorTracker, UserAccessSensitiveData, UserAccessTimeTracker, UserAccessLocationTracker
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
        ast_record = UserAccessSuccessTracker.query.filter_by(id_num=user_id).first()

        if not ast_record:
            ast_record = UserAccessSuccessTracker(
                id=str(uuid.uuid4()),
                id_num=user_id,
                ast_num_as=1 if access_success else 0,
                ast_num_af=0 if access_success else 1
            )
            db.session.add(ast_record)
        else:
            if access_success:
                ast_record.ast_num_as += 1
            else:
                ast_record.ast_num_af += 1

        # 记录操作行为
        operation_type = data.get('operation_type', 'view')
        ob_record = UserOperationBehaviorTracker.query.filter_by(id_num=user_id).first()

        if not ob_record:
            ob_record = UserOperationBehaviorTracker(
                id=str(uuid.uuid4()),
                id_num=user_id,
                ob_num_view=1 if operation_type == 'view' else 0,
                ob_num_copy=1 if operation_type == 'copy' else 0,
                ob_num_download=1 if operation_type == 'download' else 0,
                ob_num_add=1 if operation_type == 'add' else 0,
                ob_num_revise=1 if operation_type == 'revise' else 0,
                ob_num_delet=1 if operation_type == 'delete' else 0
            )
            db.session.add(ob_record)
        else:
            if operation_type == 'view':
                ob_record.ob_num_view += 1
            elif operation_type == 'copy':
                ob_record.ob_num_copy += 1
            elif operation_type == 'download':
                ob_record.ob_num_download += 1
            elif operation_type == 'add':
                ob_record.ob_num_add += 1
            elif operation_type == 'revise':
                ob_record.ob_num_revise += 1
            elif operation_type == 'delete':
                ob_record.ob_num_delet += 1

        # 记录数据敏感度
        sensitivity_level = data.get('sensitivity_level', 1)
        ds_record = UserAccessSensitiveData.query.filter_by(id_num=user_id).first()

        if not ds_record:
            ds_record = UserAccessSensitiveData(
                id=str(uuid.uuid4()),
                id_num=user_id,
                ds_num1=1 if sensitivity_level == 1 else 0,
                ds_num2=1 if sensitivity_level == 2 else 0,
                ds_num3=1 if sensitivity_level == 3 else 0,
                ds_num4=1 if sensitivity_level == 4 else 0
            )
            db.session.add(ds_record)
        else:
            if sensitivity_level == 1:
                ds_record.ds_num1 += 1
            elif sensitivity_level == 2:
                ds_record.ds_num2 += 1
            elif sensitivity_level == 3:
                ds_record.ds_num3 += 1
            elif sensitivity_level == 4:
                ds_record.ds_num4 += 1

        # 记录访问时间
        is_unusual_time = data.get('is_unusual_time', False)
        ap_record = UserAccessTimeTracker.query.filter_by(id_num=user_id).first()

        if not ap_record:
            ap_record = UserAccessTimeTracker(
                id=str(uuid.uuid4()),
                id_num=user_id,
                ap_num_ni=0 if is_unusual_time else 1,
                ap_num_ui=1 if is_unusual_time else 0
            )
            db.session.add(ap_record)
        else:
            if is_unusual_time:
                ap_record.ap_num_ui += 1
            else:
                ap_record.ap_num_ni += 1

        # 记录访问IP
        is_abnormal_ip = data.get('is_abnormal_ip', False)
        at_record = UserAccessLocationTracker.query.filter_by(id_num=user_id).first()

        if not at_record:
            at_record = UserAccessLocationTracker(
                id=str(uuid.uuid4()),
                id_num=user_id,
                at_num_nd=0 if is_abnormal_ip else 1,
                at_num_ad=1 if is_abnormal_ip else 0
            )
            db.session.add(at_record)
        else:
            if is_abnormal_ip:
                at_record.at_num_ad += 1
            else:
                at_record.at_num_nd += 1

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
        ast = UserAccessSuccessTracker.query.filter_by(id_num=user_id).first()
        ast_data = {
            'num_as': ast.ast_num_as if ast else 0,
            'num_af': ast.ast_num_af if ast else 0
        }

        # 操作行为
        ob = UserOperationBehaviorTracker.query.filter_by(id_num=user_id).first()
        ob_data = {
            'num_view': ob.ob_num_view if ob else 0,
            'num_copy': ob.ob_num_copy if ob else 0,
            'num_download': ob.ob_num_download if ob else 0,
            'num_add': ob.ob_num_add if ob else 0,
            'num_revise': ob.ob_num_revise if ob else 0,
            'num_delete': ob.ob_num_delet if ob else 0
        }

        # 数据敏感度
        ds = UserAccessSensitiveData.query.filter_by(id_num=user_id).first()
        ds_data = {
            'num1': ds.ds_num1 if ds else 0,
            'num2': ds.ds_num2 if ds else 0,
            'num3': ds.ds_num3 if ds else 0,
            'num4': ds.ds_num4 if ds else 0
        }

        # 访问时间
        ap = UserAccessTimeTracker.query.filter_by(id_num=user_id).first()
        ap_data = {
            'num_ni': ap.ap_num_ni if ap else 0,
            'num_ui': ap.ap_num_ui if ap else 0
        }

        # 访问IP
        at = UserAccessLocationTracker.query.filter_by(id_num=user_id).first()
        at_data = {
            'num_nd': at.at_num_nd if at else 0,
            'num_ad': at.at_num_ad if at else 0
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
        ast_records = UserAccessSuccessTracker.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        stats_list = []
        for ast in ast_records.items:
            # 获取对应的其他记录
            ob = UserOperationBehaviorTracker.query.filter_by(id_num=ast.id_num).first()
            ds = UserAccessSensitiveData.query.filter_by(id_num=ast.id_num).first()
            ap = UserAccessTimeTracker.query.filter_by(id_num=ast.id_num).first()
            at = UserAccessLocationTracker.query.filter_by(id_num=ast.id_num).first()

            stats_list.append({
                'user_id': ast.id_num,
                'access_success': {
                    'num_as': ast.ast_num_as,
                    'num_af': ast.ast_num_af
                },
                'operation_behavior': {
                    'num_view': ob.ob_num_view if ob else 0,
                    'num_copy': ob.ob_num_copy if ob else 0,
                    'num_download': ob.ob_num_download if ob else 0,
                    'num_add': ob.ob_num_add if ob else 0,
                    'num_revise': ob.ob_num_revise if ob else 0,
                    'num_delete': ob.ob_num_delet if ob else 0
                },
                'data_sensitivity': {
                    'num1': ds.ds_num1 if ds else 0,
                    'num2': ds.ds_num2 if ds else 0,
                    'num3': ds.ds_num3 if ds else 0,
                    'num4': ds.ds_num4 if ds else 0
                },
                'access_period': {
                    'num_ni': ap.ap_num_ni if ap else 0,
                    'num_ui': ap.ap_num_ui if ap else 0
                },
                'access_location': {
                    'num_nd': at.at_num_nd if at else 0,
                    'num_ad': at.at_num_ad if at else 0
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