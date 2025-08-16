# modules/data_management/trust_calculator.py
"""
信任值计算工具类
根据设计文档中的FAHP权重和风险等级计算用户信任值
"""

from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta
from sqlalchemy import func
from utils.extensions import db
from .models import (
    UserLogs, UserAccessSensitiveData, UserAccessLocationTracker,
    UserIps, UserAccessSuccessTracker, UserAccessTimeTracker,
    UserOperationBehaviorTracker
)


class TrustCalculator:
    """信任值计算器"""
    
    # 根据设计文档的FAHP权重配置
    FAHP_WEIGHTS = {
        'weight_disease_similarity': 0.2,
        'weight_success_rate': 0.15,
        'weight_operation_behavior': 0.25,
        'weight_data_sensitivity': 0.2,
        'weight_access_time': 0.1,
        'weight_access_ip': 0.1
    }
    
    # 操作行为风险等级
    OPERATION_RISK = {
        'view_risk': 0.1,
        'copy_download_risk': 0.3,
        'add_modify_delete_risk': 0.6
    }
    
    # 数据敏感度风险等级
    SENSITIVITY_RISK = {
        'quasi_identifier_risk': 0.1,
        'low_sensitivity_risk': 0.2,
        'high_sensitivity_risk': 0.3,
        'explicit_identifier_risk': 0.4
    }

    def __init__(self, id_num: str):
        """
        初始化信任值计算器
        
        Args:
            id_num: 用户身份证号
        """
        self.id_num = id_num

    def calculate_ip_score(self, period_days: int = 30) -> float:
        """
        计算IP地址评分
        
        Args:
            period_days: 统计周期（天数）
            
        Returns:
            IP地址评分 (0-1之间)
        """
        # 获取指定周期内的访问记录
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        total_logs = db.session.query(UserLogs).filter(
            UserLogs.id_num == self.id_num,
            UserLogs.access_timestamp >= start_date
        ).count()
        
        if total_logs == 0:
            return 0.0
        
        # 获取常用IP列表
        common_ips = db.session.query(UserIps.ip_address).filter(
            UserIps.id_num == self.id_num
        ).all()
        common_ip_set = {ip[0] for ip in common_ips}
        
        # 统计在常用IP列表中的访问次数
        common_ip_logs = db.session.query(UserLogs).filter(
            UserLogs.id_num == self.id_num,
            UserLogs.access_timestamp >= start_date,
            UserLogs.access_ip.in_(common_ip_set)
        ).count()
        
        return common_ip_logs / total_logs if total_logs > 0 else 0.0

    def calculate_success_rate_score(self) -> float:
        """
        计算访问成功率评分
        
        Returns:
            成功率评分 (0-1之间)
        """
        success_tracker = db.session.query(UserAccessSuccessTracker).filter(
            UserAccessSuccessTracker.id_num == self.id_num
        ).first()
        
        if not success_tracker:
            return 0.0
            
        return success_tracker.calculate_success_rate()

    def calculate_operation_behavior_score(self) -> float:
        """
        计算操作行为评分
        
        Returns:
            操作行为评分
        """
        behavior_tracker = db.session.query(UserOperationBehaviorTracker).filter(
            UserOperationBehaviorTracker.id_num == self.id_num
        ).first()
        
        if not behavior_tracker:
            return 1.0  # 默认为最高信任度
            
        # 使用设计文档中的风险权重计算
        return behavior_tracker.calculate_behavior_score(self.OPERATION_RISK)

    def calculate_data_sensitivity_score(self) -> float:
        """
        计算数据敏感度评分
        
        Returns:
            数据敏感度评分
        """
        sensitivity_tracker = db.session.query(UserAccessSensitiveData).filter(
            UserAccessSensitiveData.id_num == self.id_num
        ).first()
        
        if not sensitivity_tracker:
            return 1.0  # 默认为最高信任度
            
        # 使用设计文档中的敏感度风险权重计算
        return sensitivity_tracker.calculate_sensitivity_score(self.SENSITIVITY_RISK)

    def calculate_access_time_score(self) -> float:
        """
        计算访问时间评分
        
        Returns:
            访问时间评分 (0-1之间)
        """
        time_tracker = db.session.query(UserAccessTimeTracker).filter(
            UserAccessTimeTracker.id_num == self.id_num
        ).first()
        
        if not time_tracker:
            return 1.0  # 默认为最高信任度
            
        return time_tracker.calculate_normal_time_ratio()

    def calculate_disease_similarity_score(self, target_disease_codes: list) -> float:
        """
        计算疾病相似度评分
        
        Args:
            target_disease_codes: 目标疾病编码列表
            
        Returns:
            疾病相似度评分 (0-1之间)
        """
        if not target_disease_codes:
            return 1.0
            
        # 获取用户历史访问的疾病编码
        historical_logs = db.session.query(UserLogs.target_disease_codes).filter(
            UserLogs.id_num == self.id_num,
            UserLogs.access_status == 'SUCCESS'
        ).all()
        
        if not historical_logs:
            return 0.5  # 无历史记录时给予中等信任度
            
        # 统计历史疾病编码
        historical_codes = set()
        for log in historical_logs:
            try:
                codes = json.loads(log[0]) if log[0] else []
                historical_codes.update(codes)
            except json.JSONDecodeError:
                continue
        
        if not historical_codes:
            return 0.5
            
        # 计算交集比例
        target_codes_set = set(target_disease_codes)
        intersection = historical_codes.intersection(target_codes_set)
        
        # 相似度 = 交集大小 / 目标疾病编码数量
        return len(intersection) / len(target_codes_set) if target_codes_set else 1.0

    def calculate_trust_score(self, target_disease_codes: Optional[list] = None) -> Dict[str, Any]:
        """
        计算综合信任值
        
        Args:
            target_disease_codes: 目标疾病编码列表（用于疾病相似度计算）
            
        Returns:
            包含各项评分和综合信任值的字典
        """
        # 计算各项评分
        ip_score = self.calculate_ip_score()
        success_rate_score = self.calculate_success_rate_score()
        operation_behavior_score = self.calculate_operation_behavior_score()
        data_sensitivity_score = self.calculate_data_sensitivity_score()
        access_time_score = self.calculate_access_time_score()
        disease_similarity_score = self.calculate_disease_similarity_score(target_disease_codes or [])
        
        # 使用FAHP权重计算综合信任值
        trust_score = (
            disease_similarity_score * self.FAHP_WEIGHTS['weight_disease_similarity'] +
            success_rate_score * self.FAHP_WEIGHTS['weight_success_rate'] +
            operation_behavior_score * self.FAHP_WEIGHTS['weight_operation_behavior'] +
            data_sensitivity_score * self.FAHP_WEIGHTS['weight_data_sensitivity'] +
            access_time_score * self.FAHP_WEIGHTS['weight_access_time'] +
            ip_score * self.FAHP_WEIGHTS['weight_access_ip']
        )
        
        return {
            'id_num': self.id_num,
            'trust_score': round(trust_score, 4),
            'components': {
                'disease_similarity_score': round(disease_similarity_score, 4),
                'success_rate_score': round(success_rate_score, 4),
                'operation_behavior_score': round(operation_behavior_score, 4),
                'data_sensitivity_score': round(data_sensitivity_score, 4),
                'access_time_score': round(access_time_score, 4),
                'ip_score': round(ip_score, 4)
            },
            'weights': self.FAHP_WEIGHTS,
            'calculated_at': datetime.utcnow().isoformat()
        }

    @staticmethod
    def is_trusted(trust_score: float, threshold: float = 0.7) -> bool:
        """
        判断用户是否可信
        
        Args:
            trust_score: 信任值
            threshold: 信任阈值
            
        Returns:
            是否可信
        """
        return trust_score >= threshold

    @staticmethod
    def update_user_ips(id_num: str, new_ip: str, threshold_count: int = 5, period_days: int = 7):
        """
        更新用户常用IP列表
        
        Args:
            id_num: 身份证号
            new_ip: 新的IP地址
            threshold_count: 添加到常用IP列表的最小访问次数阈值
            period_days: 统计周期（天数）
        """
        # 检查该IP在指定周期内的使用次数
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        ip_usage_count = db.session.query(UserLogs).filter(
            UserLogs.id_num == id_num,
            UserLogs.access_ip == new_ip,
            UserLogs.access_timestamp >= start_date
        ).count()
        
        # 如果使用次数超过阈值，添加到常用IP列表
        if ip_usage_count >= threshold_count:
            existing_ip = db.session.query(UserIps).filter(
                UserIps.id_num == id_num,
                UserIps.ip_address == new_ip
            ).first()
            
            if existing_ip:
                # 更新现有记录
                existing_ip.access_count = ip_usage_count
                existing_ip.last_seen = datetime.utcnow()
            else:
                # 创建新记录
                new_user_ip = UserIps(
                    id=f"{id_num}_{new_ip}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    id_num=id_num,
                    ip_address=new_ip,
                    access_count=ip_usage_count,
                    last_seen=datetime.utcnow()
                )
                db.session.add(new_user_ip)
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
