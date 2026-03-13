"""
数据脱敏模型定义
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from utils.extensions import db
from datetime import datetime
import json


class DataMaskingTask(db.Model):
    """数据脱敏任务模型"""
    __tablename__ = 'data_masking_tasks'
    
    id = Column(Integer, primary_key=True)
    task_name = Column(String(255), nullable=False, comment='任务名称')
    user_id = Column(Integer, ForeignKey('sys_users.id'), nullable=False, comment='用户ID')
    file_path = Column(String(500), nullable=False, comment='原始文件路径')
    file_name = Column(String(255), nullable=False, comment='文件名')
    file_size = Column(Integer, comment='文件大小(字节)')
    
    # 脱敏参数
    selected_headers = Column(Text, comment='选择的列名(JSON格式)')
    record_count = Column(Integer, default=100, comment='处理记录数')
    scenario = Column(String(50), default='决策', comment='应用场景')
    method = Column(String(50), default='k-匿名', comment='脱敏方法')
    
    # 任务状态
    status = Column(String(20), default='pending', comment='任务状态: pending, processing, completed, failed')
    progress = Column(Integer, default=0, comment='进度百分比')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    started_at = Column(DateTime, comment='开始处理时间')
    completed_at = Column(DateTime, comment='完成时间')
    
    # 关联关系
    user = relationship('User', foreign_keys=[user_id], backref='masking_tasks')
    results = relationship('DataMaskingResult', backref='task', cascade='all, delete-orphan')
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_name': self.task_name,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'selected_headers': json.loads(self.selected_headers) if self.selected_headers else [],
            'record_count': self.record_count,
            'scenario': self.scenario,
            'method': self.method,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class DataMaskingResult(db.Model):
    """数据脱敏结果模型"""
    __tablename__ = 'data_masking_results'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('data_masking_tasks.id'), nullable=False, comment='任务ID')
    
    # 结果文件
    output_file_path = Column(String(500), comment='输出文件路径')
    output_file_name = Column(String(255), comment='输出文件名')
    
    # 评估结果
    safety_score = Column(Float, comment='安全评分')
    utility_score = Column(Float, comment='效用评分')
    privacy_score = Column(Float, comment='隐私评分')
    
    # 详细评估数据(JSON格式)
    evaluation_data = Column(Text, comment='效用评估数据')
    privacy_data = Column(Text, comment='隐私评估数据')
    
    # 脱敏参数详情
    method_params = Column(Text, comment='方法参数(JSON格式)')
    
    # 处理统计
    original_records = Column(Integer, comment='原始记录数')
    processed_records = Column(Integer, comment='处理后记录数')
    processing_time = Column(Float, comment='处理时间(秒)')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'output_file_name': self.output_file_name,
            'safety_score': self.safety_score,
            'utility_score': self.utility_score,
            'privacy_score': self.privacy_score,
            'evaluation_data': json.loads(self.evaluation_data) if self.evaluation_data else {},
            'privacy_data': json.loads(self.privacy_data) if self.privacy_data else {},
            'method_params': json.loads(self.method_params) if self.method_params else {},
            'original_records': self.original_records,
            'processed_records': self.processed_records,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
