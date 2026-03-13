"""
数据脱敏API路由
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from utils.extensions import db
from utils.response import success_response, error_response, server_error_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.auth.decorators import role_required
from .models import DataMaskingTask, DataMaskingResult
from .core.anti_sensitive import AntiSensitive
from .utils.data_processing import DataProcessor
import threading
import time
import pandas as pd
from typing import Optional, Tuple

# 创建蓝图
datamasking_bp = Blueprint('datamasking', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'txt'}

# 上传文件夹
UPLOAD_FOLDER = 'uploads/datamasking'
OUTPUT_FOLDER = 'outputs/datamasking'


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 注意：此函数已废弃，不再生成模拟数据
# 现在直接使用前端传递的 results 数据
def create_mock_data_file(selected_headers: list, record_count: int, data_code_details: dict = None) -> str:
    """
    已废弃：不再生成模拟数据
    现在直接使用前端传递的 results 数据
    """
    raise NotImplementedError("不再支持生成模拟数据，请使用前端传递的 results 数据")


def ensure_directories():
    """确保必要的目录存在"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@datamasking_bp.route('/upload', methods=['POST'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def upload_file():
    """上传数据文件"""
    try:
        ensure_directories()
        
        if 'file' not in request.files:
            return error_response("没有选择文件", 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response("没有选择文件", 400)
        
        if not allowed_file(file.filename):
            return error_response("不支持的文件格式", 400)
        
        # 保存文件
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        
        # 获取文件列名
        processor = DataProcessor()
        try:
            headers = processor.get_file_headers(file_path)
        except Exception as e:
            os.remove(file_path)  # 删除无效文件
            return error_response(f"文件解析失败: {str(e)}", 400)
        
        return success_response(
            result={
                'file_path': file_path,
                'file_name': filename,
                'file_size': file_size,
                'headers': headers
            },
            message="文件上传成功"
        )
        
    except Exception as e:
        return server_error_response(f"文件上传失败: {str(e)}")


@datamasking_bp.route('/start', methods=['POST'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def start_masking():
    """
    接收前端传递的医疗数据 JSON，保存原始文件并执行脱敏流程：
    1. 计算隐私风险系数
    2. 根据风险和指定策略执行脱敏
    3. 进行效用评估与风险评估
    4. 返回处理结果和脱敏数据预览
    """
    try:
        data = request.get_json()
        if not data:
            return error_response("请求体不能为空", 400)

        results = data.get('results', [])
        if not results:
            return error_response("缺少医疗数据（results）", 400)

        ensure_directories()

        # 基础字段提取
        selected_headers = data.get('selected_headers') or list(data.get('data_code_details', {}).keys())
        if isinstance(selected_headers, dict):
            selected_headers = list(selected_headers.keys())
        if not selected_headers:
            selected_headers = list(results[0].keys())

        record_count = data.get('record_count') or len(results)
        try:
            record_count = int(record_count)
        except ValueError:
            return error_response("record_count 必须为整数", 400)

        scenario = data.get('scenario', '决策')
        method = data.get('method', 'k-匿名')

        # 保存完整请求数据为 JSON 文件
        filename = f"medical_data_{uuid.uuid4().hex[:8]}.json"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        data_to_save = dict(data)
        data_to_save['saved_file_path'] = file_path
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

        # 执行脱敏流程
        anti_sensitive = AntiSensitive(
            file_path=file_path,
            record_count=record_count,
            method=method,
            scenario=scenario,
            selected_headers=selected_headers
        )

        safety_score, (masked_df, method_info, utility_df, privacy_df) = anti_sensitive.process_data()

        # 打印脱敏后数据预览
        try:
            print("\n=== 脱敏后数据预览（前5行） ===")
            if masked_df is not None and not masked_df.empty:
                print(masked_df.head())
            else:
                print("脱敏结果为空")
        except Exception as preview_error:
            print(f"脱敏数据预览打印失败: {preview_error}")

        # 保存脱敏后的数据（JSON）
        masked_records = masked_df.to_dict(orient='records') if not masked_df.empty else []
        masked_filename = f"masked_{uuid.uuid4().hex[:8]}.json"
        masked_path = os.path.join(OUTPUT_FOLDER, masked_filename)
        with open(masked_path, 'w', encoding='utf-8') as f:
            json.dump(masked_records, f, ensure_ascii=False, indent=2)

        # 另存为 CSV，便于前端点击下载
        masked_csv_filename = f"masked_{uuid.uuid4().hex[:8]}.csv"
        masked_csv_path = os.path.join(OUTPUT_FOLDER, masked_csv_filename)
        try:
            if masked_df is not None and not masked_df.empty:
                masked_df.to_csv(masked_csv_path, index=False, encoding="utf-8-sig")
            else:
                # 空结果也返回一个空CSV文件，保持接口一致性
                pd.DataFrame().to_csv(masked_csv_path, index=False, encoding="utf-8-sig")
        except Exception as e:
            print(f"保存CSV失败: {str(e)}")
            masked_csv_path = ""

        # 评估结果转换为可序列化格式
        if not utility_df.empty:
            utility_df2 = utility_df.reset_index().rename(columns={'index': 'model'})
            # 确保列顺序: model, Acc, AUC, F1_Score
            cols_order = [c for c in ["model", "Acc", "AUC", "F1_Score"] if c in utility_df2.columns]
            utility_df2 = utility_df2[cols_order]
            utility_metrics = utility_df2.to_dict(orient='records')
            utility_columns = cols_order
        else:
            utility_metrics = []
            utility_columns = ["model", "Acc", "AUC", "F1_Score"]

        if not privacy_df.empty:
            # 确保列顺序：先 DCR（真实-脱敏、真实-真实、脱敏-脱敏），再 NNDR（真实-脱敏、真实-真实、脱敏-脱敏）
            desired_privacy_cols = [
                "真实-脱敏 DCR(5%)",
                "真实-真实 DCR(5%)",
                "脱敏-脱敏 DCR(5%)",
                "真实-脱敏 NNDR(5%)",
                "真实-真实 NNDR(5%)",
                "脱敏-脱敏 NNDR(5%)",
            ]
            privacy_df2 = privacy_df.copy()
            # 仅重排已存在的列，防御性处理
            cols_order = [c for c in desired_privacy_cols if c in privacy_df2.columns]
            if cols_order:
                privacy_df2 = privacy_df2[cols_order]
            privacy_metrics = privacy_df2.to_dict(orient='records')
            privacy_columns = cols_order if cols_order else list(privacy_df.columns)
        else:
            privacy_metrics = []
            privacy_columns = [
                "真实-脱敏 DCR(5%)",
                "真实-真实 DCR(5%)",
                "脱敏-脱敏 DCR(5%)",
                "真实-脱敏 NNDR(5%)",
                "真实-真实 NNDR(5%)",
                "脱敏-脱敏 NNDR(5%)",
            ]

        # 原始数据预览（直接来自请求）与完整脱敏数据（直接随响应返回给前端）
        original_preview = results[:10] if isinstance(results, list) else []

        response_payload = {
            'original_file': {
                'path': file_path,
                'name': filename,
                'record_count': len(results)
            },
            'masked_file': {
                'path': masked_path,
                'name': masked_filename,
                'record_count': len(masked_records)
            },
            'masked_csv_file': {
                'path': masked_csv_path,
                'name': masked_csv_filename
            },
            'original_preview': original_preview,
            'masked_data': masked_records,
            'privacy_risk_score': safety_score,
            'selected_method': method_info,
            'masked_preview': masked_records[:10],
            'utility_columns': utility_columns,
            'utility_metrics': utility_metrics,
            'privacy_columns': privacy_columns,
            'privacy_metrics': privacy_metrics
        }

        return success_response(
            result=response_payload,
            message="脱敏处理完成"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return server_error_response(f"脱敏处理失败: {str(e)}")

@datamasking_bp.route('/download/masked', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def download_masked_csv():
    """下载指定路径的脱敏CSV文件；前端从 start 接口的 masked_csv_file.path 获取路径后调用此接口。"""
    try:
        path = request.args.get('path', '').strip()
        if not path:
            return error_response("缺少参数: path", 400)
        # 支持相对路径
        if not os.path.isabs(path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            abs_path = os.path.join(base_dir, path)
        else:
            abs_path = path
        if not os.path.exists(abs_path):
            return error_response("文件不存在", 404)
        from flask import send_file
        return send_file(abs_path, as_attachment=True, download_name=os.path.basename(abs_path))
    except Exception as e:
        return server_error_response(f"下载文件失败: {str(e)}")


def _get_latest_file(directory: str, prefix: str, suffix: str) -> Optional[str]:
    """返回目录下最近修改的、匹配指定前后缀的文件路径。"""
    try:
        if not os.path.exists(directory):
            return None
        candidates = [
            os.path.join(directory, name)
            for name in os.listdir(directory)
            if name.startswith(prefix) and name.endswith(suffix)
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return candidates[0]
    except Exception:
        return None


@datamasking_bp.route('/view/original', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def view_original():
    """查看最近一次保存的原始医疗数据（完整JSON + 预览）。"""
    try:
        path = _get_latest_file(UPLOAD_FOLDER, 'medical_data_', '.json')
        if not path:
            return error_response("未找到原始数据文件", 404)
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        # 兼容完整请求结构或仅 results 数组
        if isinstance(payload, dict) and 'results' in payload:
            records = payload['results']
        else:
            records = payload
        preview = records[:10] if isinstance(records, list) else []
        return success_response(
            result={
                'path': path,
                'preview': preview,
                'data': payload
            },
            message="获取原始数据成功"
        )
    except Exception as e:
        return server_error_response(f"读取原始数据失败: {str(e)}")


@datamasking_bp.route('/view/masked', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def view_masked():
    """查看最近一次脱敏后的数据（完整JSON + 预览）。"""
    try:
        path = _get_latest_file(OUTPUT_FOLDER, 'masked_', '.json')
        if not path:
            return error_response("未找到脱敏结果文件", 404)
        with open(path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        preview = records[:10] if isinstance(records, list) else []
        return success_response(
            result={
                'path': path,
                'preview': preview,
                'data': records
            },
            message="获取脱敏数据成功"
        )
    except Exception as e:
        return server_error_response(f"读取脱敏数据失败: {str(e)}")


def execute_masking_task(task_id: int, file_path: str, selected_headers: list, 
                        record_count: int, scenario: str, method: str):
    """执行脱敏任务"""
    try:
        # 更新任务状态
        task = DataMaskingTask.query.get(task_id)
        if not task:
            return
        
        task.status = 'processing'
        task.started_at = datetime.utcnow()
        task.progress = 0
        db.session.commit()
        
        # 执行脱敏处理
        anti_sensitive = AntiSensitive(
            file_path=file_path,
            record_count=record_count,
            method=method,
            scenario=scenario,
            selected_headers=selected_headers
        )
        
        # 更新进度
        task.progress = 20
        db.session.commit()
        
        # 执行脱敏
        safety_score, (mask_data, method_info, eval_df, privacy_df) = anti_sensitive.process_data()
        
        # 更新进度
        task.progress = 80
        db.session.commit()
        
        # 保存结果文件
        ensure_directories()
        output_filename = f"masked_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        mask_data.to_csv(output_path, index=False)
        
        # 创建结果记录
        result = DataMaskingResult(
            task_id=task_id,
            output_file_path=output_path,
            output_file_name=output_filename,
            safety_score=float(safety_score),
            utility_score=float(eval_df['Acc'].mean()) if not eval_df.empty else 0.0,
            privacy_score=float(privacy_df.iloc[0, 0]) if not privacy_df.empty else 0.0,
            evaluation_data=eval_df.to_json() if not eval_df.empty else '{}',
            privacy_data=privacy_df.to_json() if not privacy_df.empty else '{}',
            method_params=json.dumps({'method': method, 'info': method_info}),
            original_records=len(mask_data),
            processed_records=len(mask_data),
            processing_time=0.0  # 可以计算实际处理时间
        )
        
        db.session.add(result)
        
        # 更新任务状态
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        task.progress = 100
        db.session.commit()
        
    except Exception as e:
        # 更新任务状态为失败
        task = DataMaskingTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.completed_at = datetime.utcnow()
            db.session.commit()
        
        print(f"脱敏任务执行失败: {str(e)}")


@datamasking_bp.route('/tasks', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def get_tasks():
    """获取脱敏任务列表"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询任务
        query = DataMaskingTask.query.filter_by(user_id=user_id)
        tasks = query.order_by(DataMaskingTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 转换为字典格式
        task_list = [task.to_dict() for task in tasks.items]
        
        return success_response(
            result={
                'tasks': task_list,
                'total': tasks.total,
                'pages': tasks.pages,
                'current_page': page,
                'per_page': per_page
            },
            message="获取任务列表成功"
        )
        
    except Exception as e:
        return server_error_response(f"获取任务列表失败: {str(e)}")


@datamasking_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def get_task_detail(task_id: int):
    """获取任务详情"""
    try:
        user_id = get_jwt_identity()
        
        # 查询任务
        task = DataMaskingTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return error_response("任务不存在", 404)
        
        # 获取结果
        result = DataMaskingResult.query.filter_by(task_id=task_id).first()
        
        task_data = task.to_dict()
        if result:
            task_data['result'] = result.to_dict()
        
        return success_response(
            result=task_data,
            message="获取任务详情成功"
        )
        
    except Exception as e:
        return server_error_response(f"获取任务详情失败: {str(e)}")


@datamasking_bp.route('/tasks/<int:task_id>/download', methods=['GET'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def download_result(task_id: int):
    """下载脱敏结果文件"""
    try:
        user_id = get_jwt_identity()
        
        # 查询任务
        task = DataMaskingTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return error_response("任务不存在", 404)
        
        if task.status != 'completed':
            return error_response("任务未完成", 400)
        
        # 获取结果文件路径
        result = DataMaskingResult.query.filter_by(task_id=task_id).first()
        if not result or not result.output_file_path:
            return error_response("结果文件不存在", 404)
        
        # 检查文件是否存在
        if not os.path.exists(result.output_file_path):
            return error_response("结果文件不存在", 404)
        
        from flask import send_file
        return send_file(
            result.output_file_path,
            as_attachment=True,
            download_name=result.output_file_name
        )
        
    except Exception as e:
        return server_error_response(f"下载文件失败: {str(e)}")


@datamasking_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
@role_required('ADMIN', 'RESEARCHER', 'FAMILY_DOCTOR', 'ATTENDING_DOCTOR')
def delete_task(task_id: int):
    """删除脱敏任务"""
    try:
        user_id = get_jwt_identity()
        
        # 查询任务
        task = DataMaskingTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return error_response("任务不存在", 404)
        
        # 删除相关文件
        if task.file_path and os.path.exists(task.file_path):
            os.remove(task.file_path)
        
        result = DataMaskingResult.query.filter_by(task_id=task_id).first()
        if result and result.output_file_path and os.path.exists(result.output_file_path):
            os.remove(result.output_file_path)
        
        # 删除数据库记录
        db.session.delete(task)
        db.session.commit()
        
        return success_response(message="任务删除成功")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return server_error_response(f"数据库操作失败: {str(e)}")
    except Exception as e:
        return server_error_response(f"删除任务失败: {str(e)}")


@datamasking_bp.route('/methods', methods=['GET'])
@jwt_required()
def get_masking_methods():
    """获取可用的脱敏方法"""
    try:
        methods = [
            {
                'id': 'k-匿名',
                'name': 'k-匿名',
                'description': '通过泛化和抑制技术实现k-匿名，保护个体隐私',
                'parameters': [
                    {'name': 'k', 'type': 'integer', 'description': '匿名参数k值', 'default': 3}
                ]
            },
            {
                'id': '差分隐私',
                'name': '差分隐私',
                'description': '通过添加噪声实现差分隐私，提供严格的隐私保护',
                'parameters': [
                    {'name': 'epsilon', 'type': 'float', 'description': '隐私预算', 'default': 1.0}
                ]
            },
            {
                'id': 'CTABGAN',
                'name': 'CTABGAN',
                'description': '使用条件表格生成对抗网络生成合成数据',
                'parameters': []
            },
            {
                'id': '智能选择',
                'name': '智能选择',
                'description': '智能选择脱敏方法',
                'parameters': []
            }
        ]
        
        scenarios = [
            {'id': '决策', 'name': '决策支持', 'description': '用于决策支持系统'},
            {'id': '展示', 'name': '数据展示', 'description': '用于数据可视化展示'},
            {'id': '分析', 'name': '数据分析', 'description': '用于统计分析'},
            {'id': '预测', 'name': '预测建模', 'description': '用于机器学习预测'}
        ]
        
        return success_response(
            result={
                'methods': methods,
                'scenarios': scenarios
            },
            message="获取脱敏方法成功"
        )
        
    except Exception as e:
        return server_error_response(f"获取脱敏方法失败: {str(e)}")
