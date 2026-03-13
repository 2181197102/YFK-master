"""
差分隐私方法实现
"""

import numpy as np
import pandas as pd
from typing import List, Tuple


class LaplaceDiffPrivacy:
    """基于拉普拉斯机制的差分隐私"""
    
    def __init__(self, epsilon: float, sensitivity: float):
        """
        初始化差分隐私处理器
        
        Args:
            epsilon: 隐私预算
            sensitivity: 敏感度
        """
        self.epsilon = epsilon
        self.sensitivity = sensitivity
    
    def add_noise(self, data: pd.DataFrame) -> np.ndarray:
        """
        为数值型数据添加拉普拉斯噪声
        
        Args:
            data: 数值型数据
            
        Returns:
            添加噪声后的数据
        """
        # 计算拉普拉斯噪声的尺度
        lamda = self.sensitivity / self.epsilon
        
        # 生成拉普拉斯噪声
        noise = np.random.laplace(loc=0.0, scale=lamda, size=data.shape)
        
        # 加噪后的数据
        noised_data = data.values + noise
        
        return noised_data


class ExponentialMechanism:
    """基于指数机制的差分隐私"""
    
    def __init__(self, epsilon: float, sensitivity: float):
        """
        初始化指数机制处理器
        
        Args:
            epsilon: 隐私预算
            sensitivity: 敏感度
        """
        self.epsilon = epsilon
        self.sensitivity = sensitivity
    
    def exponential_mechanism(self, categorical_data: pd.DataFrame, 
                            original_data: pd.DataFrame, 
                            categorical_columns: List[str]) -> np.ndarray:
        """
        使用指数机制处理分类数据
        
        Args:
            categorical_data: 分类数据
            original_data: 原始数据
            categorical_columns: 分类列名
            
        Returns:
            处理后的分类数据
        """
        from ..utils.safety_scoring import SafetyScorer
        
        # 分类数据的全局组合唯一性分析
        scorer = SafetyScorer()
        filtered_data, frequencies, w_recode_count = scorer.total_recode_count(
            original_data, categorical_columns
        )
        
        # 计算效用
        utilities = frequencies / np.sum(frequencies)
        
        # 计算概率分布
        exp_scores = [
            np.round(np.exp(self.epsilon * utility / (2 * self.sensitivity)), 5)
            for utility in utilities
        ]
        
        probabilities = exp_scores / np.linalg.norm(exp_scores, ord=1)
        
        # 根据概率分布随机选择值
        chosen_indexes = np.random.choice(
            len(filtered_data), size=len(categorical_data), p=probabilities
        )
        
        chosen_values = np.array([
            filtered_data[chosen_index] for chosen_index in chosen_indexes
        ])
        
        return chosen_values
