"""
数据脱敏核心处理类
迁移自E:\\datamasking项目
"""

import numpy as np
import pandas as pd
import os
import time
from typing import Tuple, Dict, Any, List
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.spatial.distance import pdist, squareform
from scipy.stats import chi2_contingency
from collections import Counter
import json

# 导入脱敏方法
from ..methods.dp_method import LaplaceDiffPrivacy, ExponentialMechanism
from ..methods.k_anonymity import KAnonymityProcessor
from ..methods.rsa_encryption import RSAEncryption
from ..methods.gan_method import CTABGANProcessor
from ..utils.data_processing import DataProcessor
from ..utils.safety_scoring import SafetyScorer
from ..utils.evaluation import DataEvaluator


class AntiSensitive:
    """数据脱敏主处理类"""
    
    def __init__(self, file_path: str, record_count: int, method: str, 
                 scenario: str, selected_headers: List[str]) -> None:
        """
        初始化脱敏处理器
        
        Args:
            file_path: 数据文件路径
            record_count: 处理记录数
            method: 脱敏方法 (差分隐私, k-匿名, CTABGAN)
            scenario: 应用场景 (决策, 展示, 分析, 预测)
            selected_headers: 选择的列名
        """
        self.file_path = file_path
        self.record_count = record_count
        self.method = method
        self.scenario = scenario
        self.selected_headers = selected_headers
        
        # 初始化处理器
        self.data_processor = DataProcessor()
        self.safety_scorer = SafetyScorer()
        self.evaluator = DataEvaluator()
        
        # 处理结果
        self.sample_columns = []
        self.new_columns = []
        
    def process_data(self) -> Tuple[float, Tuple[pd.DataFrame, str, pd.DataFrame, pd.DataFrame]]:
        """
        执行数据脱敏处理
        
        Returns:
            Tuple[安全评分, (脱敏数据, 方法信息, 效用评估, 隐私评估)]
        """
        try:
            # 1. 加载和预处理数据
            df = self.data_processor.load_data(self.file_path)
            data = df.sample(n=min(self.record_count, len(df)))
            
            # 2. 分析数据特征
            attributes, N, M, T_d, M_d, numerical_columns, categorical_columns, need_masking_fields, need_masking_fields_count = \
                self.data_processor.get_data_messages(self.file_path)
            
            # 3. 筛选选择的列
            self._filter_selected_columns(numerical_columns, categorical_columns)
            
            # 4. 计算安全评分
            safety_score = self._calculate_safety_score(
                data, attributes, N, M, T_d, M_d, 
                numerical_columns, categorical_columns
            )
            
            # 5. 执行脱敏处理
            mask_data, method_info, eval_df, privacy_df = self._apply_masking_method(
                data, numerical_columns, categorical_columns, safety_score
            )
            
            return safety_score, (mask_data, method_info, eval_df, privacy_df)
            
        except Exception as e:
            raise Exception(f"数据脱敏处理失败: {str(e)}")
    
    def _filter_selected_columns(self, numerical_columns: List[str], 
                                categorical_columns: List[str]) -> None:
        """筛选选择的列"""
        # 识别敏感列
        for col in self.selected_headers:
            if col in ['Phone', 'Id', 'Hospital']:
                self.sample_columns.append(col)
        
        # 筛选数值型和分类型列
        new_numerical_columns = []
        new_categorical_columns = []
        
        for col in self.selected_headers:
            if col in numerical_columns:
                new_numerical_columns.append(col)
                self.new_columns.append(col)
            elif col in categorical_columns:
                new_categorical_columns.append(col)
                self.new_columns.append(col)
            elif col not in self.new_columns:
                # 默认将未知类型字段视为分类字段
                new_categorical_columns.append(col)
                self.new_columns.append(col)
        
        self.new_numerical_columns = new_numerical_columns
        self.new_categorical_columns = new_categorical_columns
    
    def _calculate_safety_score(self, data: pd.DataFrame, attributes: List[str],
                              N: int, M: int, T_d: List[int], M_d: List[int],
                              numerical_columns: List[str], categorical_columns: List[str]) -> float:
        """计算安全评分"""
        try:
            # 获取数值型和分类型数据
            NA = data[self.new_numerical_columns] if self.new_numerical_columns else pd.DataFrame()
            CA = data[self.new_categorical_columns] if self.new_categorical_columns else pd.DataFrame()
            
            # 计算相关性矩阵
            correlation_matrix = self.safety_scorer.calculate_correlation_matrix(
                data.drop(columns=self.sample_columns), attributes
            )
            
            # 设置场景参数
            t_d = self._get_scenario_params()
            
            # 属性聚类：k自适应，避免 n_samples < k 导致报错
            dim = max(2, len(numerical_columns) + len(categorical_columns))
            k = min(6, dim)
            cluster, merged_dataT = self.safety_scorer.kmeans_cluster(
                data, k, numerical_columns, categorical_columns
            )
            
            # 计算各项权重
            n, m = len(NA) + len(CA), len(self.new_columns)
            
            # 1. 数量分析
            w_recode, w_field = self.safety_scorer.w_number(n, m, N, M)
            
            # 2. 关联规则等级
            m_d, M_d = self.safety_scorer.degree_association_rule(
                correlation_matrix, attributes, self.new_columns, M_d, cluster
            )
            
            # 3. 场景分析
            M = self.safety_scorer.operation_matrix(M_d, T_d)
            M_subset = self.safety_scorer.operation_matrix(m_d, t_d)
            w_operation = self.safety_scorer.w_operation(M, M_subset)
            
            # 4. 记录相关性分析
            w_correlation = self.safety_scorer.w_correlation(NA, CA, self.new_categorical_columns)
            
            # 5. 计算总权重
            w = self.safety_scorer.w_total(w_recode, w_field, w_operation, w_correlation)
            
            return np.round(w, 4)
            
        except Exception as e:
            print(f"安全评分计算失败: {str(e)}")
            return 0.5  # 默认中等风险
    
    def _get_scenario_params(self) -> List[int]:
        """根据场景获取参数"""
        scenario_params = {
            '决策': [5, 0, 0, 0],
            '展示': [0, 2, 0, 0],
            '分析': [0, 0, 4, 0],
            '预测': [0, 0, 0, 4]
        }
        return scenario_params.get(self.scenario, [5, 0, 0, 0])
    
    def _apply_masking_method(self, data: pd.DataFrame, numerical_columns: List[str],
                            categorical_columns: List[str], safety_score: float) -> \
                            Tuple[pd.DataFrame, str, pd.DataFrame, pd.DataFrame]:
        """应用脱敏方法"""
        
        # 预处理敏感列
        processed_data = self._preprocess_sensitive_columns(data.copy())
        
        # 智能选择：根据数据类型/规模自动选择
        if self.method == "智能选择":
            has_numeric = len(self.new_numerical_columns) > 0
            self.method = "k-匿名" if (not has_numeric or len(processed_data) < 3) else "差分隐私"
        
        if self.method == "差分隐私":
            return self._apply_differential_privacy(
                processed_data, numerical_columns, categorical_columns, safety_score
            )
        elif self.method == "k-匿名":
            return self._apply_k_anonymity(
                processed_data, numerical_columns, categorical_columns, safety_score
            )
        elif self.method == "CTABGAN":
            return self._apply_ctabgan(
                processed_data, numerical_columns, categorical_columns, safety_score
            )
        else:
            raise ValueError(f"不支持的脱敏方法: {self.method}")
    
    def _preprocess_sensitive_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """预处理敏感列"""
        rsa_processor = RSAEncryption()
        
        if 'Phone' in self.selected_headers and 'Phone' in data.columns:
            data['Phone'] = [self._mask_phone_number(str(i)) for i in data['Phone']]
        
        if 'Id' in self.selected_headers and 'Id' in data.columns:
            private_key_pem, public_key_pem = rsa_processor.generate_rsa_keys()
            data['Id'] = [rsa_processor.encrypt_id_number(public_key_pem, str(i)) 
                         for i in data['Id']]
        
        if 'Hospital' in self.selected_headers and 'Hospital' in data.columns:
            data['Hospital'] = [self._hash_id_number(str(i)) for i in data['Hospital']]
        
        return data
    
    def _mask_phone_number(self, phone: str) -> str:
        """手机号脱敏"""
        if len(phone) >= 11:
            return phone[:3] + '****' + phone[-4:]
        return phone
    
    def _hash_id_number(self, id_number: str) -> str:
        """身份证号哈希"""
        import hashlib
        return hashlib.sha256(id_number.encode()).hexdigest()[:16]
    
    def _apply_differential_privacy(self, data: pd.DataFrame, numerical_columns: List[str],
                                 categorical_columns: List[str], safety_score: float) -> \
                                 Tuple[pd.DataFrame, str, pd.DataFrame, pd.DataFrame]:
        """应用差分隐私"""
        # 根据安全评分确定epsilon值
        if 0 < safety_score < 0.3:
            epsilon = 5
        elif 0.3 <= safety_score < 0.6:
            epsilon = 1
        else:
            epsilon = 0.1
        
        sensitivity = 1
        
        # 处理数值型数据
        NA = data[self.new_numerical_columns] if self.new_numerical_columns else pd.DataFrame()
        CA = data[self.new_categorical_columns] if self.new_categorical_columns else pd.DataFrame()
        
        if not NA.empty:
            # 强制转换为数值，无法转换的置0，避免噪声叠加时报类型错误
            NA = NA.apply(pd.to_numeric, errors='coerce').fillna(0.0)
            dp_processor = LaplaceDiffPrivacy(epsilon, sensitivity)
            noisy_numerical_data = pd.DataFrame(
                dp_processor.add_noise(NA),
                columns=self.new_numerical_columns,
                dtype="float64"
            )
        else:
            noisy_numerical_data = pd.DataFrame()
        
        if not CA.empty:
            exp_processor = ExponentialMechanism(epsilon, sensitivity)
            noisy_categorical_data = pd.DataFrame(
                exp_processor.exponential_mechanism(CA, data, self.new_categorical_columns),
                columns=self.new_categorical_columns,
                dtype="object"
            )
        else:
            noisy_categorical_data = pd.DataFrame()
        
        # 合并数据
        if not noisy_numerical_data.empty and not noisy_categorical_data.empty:
            noisy_data = pd.concat([noisy_numerical_data.reset_index(drop=True), 
                                  noisy_categorical_data.reset_index(drop=True)], axis=1)
        elif not noisy_numerical_data.empty:
            noisy_data = noisy_numerical_data
        elif not noisy_categorical_data.empty:
            noisy_data = noisy_categorical_data
        else:
            noisy_data = pd.DataFrame()

        # 追加上下文字段（如 institution、medical_record_num），保持字段一致性
        context_columns = [c for c in data.columns if c not in set(self.new_numerical_columns + self.new_categorical_columns)]
        context_df = data[context_columns].reset_index(drop=True) if context_columns else pd.DataFrame()
        mask_data = pd.concat([noisy_data.reset_index(drop=True), context_df], axis=1)

        # 按原始列顺序重排，保证脱敏前后字段一致
        ordered_cols = [c for c in data.columns if c in mask_data.columns]
        if ordered_cols:
            mask_data = mask_data[ordered_cols]

        # 按 medical_record_num 升序排序
        if "medical_record_num" in mask_data.columns:
            mrn_numeric = pd.to_numeric(mask_data["medical_record_num"], errors="coerce")
            mask_data = mask_data.assign(_mrn_order=mrn_numeric).sort_values("_mrn_order", kind="mergesort").drop(columns=["_mrn_order"]).reset_index(drop=True)
        
        # 评估效果
        eval_result_df, privacy_results = self.evaluator.evaluate_masking_effect(
            data[self.new_columns], noisy_data, self.new_categorical_columns
        )
        
        method_info = f"差分隐私 (ε={epsilon})"
        return mask_data, method_info, eval_result_df, privacy_results
    
    def _apply_k_anonymity(self, data: pd.DataFrame, numerical_columns: List[str],
                          categorical_columns: List[str], safety_score: float) -> \
                          Tuple[pd.DataFrame, str, pd.DataFrame, pd.DataFrame]:
        """应用k-匿名"""
        # 根据安全评分确定k值
        if 0 < safety_score < 0.2:
            k = 2
        elif 0.2 <= safety_score < 0.5:
            k = 3
        else:
            k = 4
        
        k_processor = KAnonymityProcessor()
        
        # 处理数据
        data_new = data[self.new_columns]
        sensitive_column = 'Income' if 'Income' in data_new.columns else data_new.columns[-1]
        
        feature_columns = [col for col in self.new_columns if col != sensitive_column]
        
        # 执行k-匿名处理
        dm_data = k_processor.process_k_anonymity(
            data_new, feature_columns, sensitive_column, 
            self.new_categorical_columns, k
        )

        # 追加上下文字段（如 institution、medical_record_num），保持字段一致性
        context_columns = [c for c in data.columns if c not in set(self.new_columns)]
        context_df = data[context_columns].reset_index(drop=True) if context_columns else pd.DataFrame()
        mask_data = pd.concat([dm_data.reset_index(drop=True), context_df], axis=1)

        # 按原始列顺序重排
        ordered_cols = [c for c in data.columns if c in mask_data.columns]
        if ordered_cols:
            mask_data = mask_data[ordered_cols]

        # 按 medical_record_num 升序排序
        if "medical_record_num" in mask_data.columns:
            mrn_numeric = pd.to_numeric(mask_data["medical_record_num"], errors="coerce")
            mask_data = mask_data.assign(_mrn_order=mrn_numeric).sort_values("_mrn_order", kind="mergesort").drop(columns=["_mrn_order"]).reset_index(drop=True)
        mask_data = mask_data.dropna(axis=0, how='any')
        
        method_info = f"k-匿名 (k={k})"
        return mask_data, method_info, pd.DataFrame(), pd.DataFrame()
    
    def _apply_ctabgan(self, data: pd.DataFrame, numerical_columns: List[str],
                      categorical_columns: List[str], safety_score: float) -> \
                      Tuple[pd.DataFrame, str, pd.DataFrame, pd.DataFrame]:
        """应用CTABGAN"""
        gan_processor = CTABGANProcessor()
        
        # 准备数据
        new_data = pd.concat([
            data[self.new_numerical_columns] if self.new_numerical_columns else pd.DataFrame(),
            data[self.new_categorical_columns] if self.new_categorical_columns else pd.DataFrame()
        ], axis=1)
        
        # 执行CTABGAN处理
        dm_data = gan_processor.process_ctabgan(
            new_data, self.new_categorical_columns, self.new_numerical_columns
        )

        # 追加上下文字段（如 institution、medical_record_num），保持字段一致性
        context_columns = [c for c in data.columns if c not in set(self.new_numerical_columns + self.new_categorical_columns)]
        context_df = data[context_columns].reset_index(drop=True) if context_columns else pd.DataFrame()
        mask_data = pd.concat([dm_data.reset_index(drop=True), context_df], axis=1)

        # 按原始列顺序重排
        ordered_cols = [c for c in data.columns if c in mask_data.columns]
        if ordered_cols:
            mask_data = mask_data[ordered_cols]

        # 按 medical_record_num 升序排序
        if "medical_record_num" in mask_data.columns:
            mrn_numeric = pd.to_numeric(mask_data["medical_record_num"], errors="coerce")
            mask_data = mask_data.assign(_mrn_order=mrn_numeric).sort_values("_mrn_order", kind="mergesort").drop(columns=["_mrn_order"]).reset_index(drop=True)
        
        # 评估效果
        eval_result_df, privacy_results = self.evaluator.evaluate_masking_effect(
            new_data, dm_data, self.new_categorical_columns
        )
        
        method_info = "CTABGAN"
        return mask_data, method_info, eval_result_df, privacy_results
