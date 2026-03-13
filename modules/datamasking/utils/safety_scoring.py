"""
安全评分计算工具
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.spatial.distance import pdist, squareform
from scipy.stats import chi2_contingency
from collections import Counter
from typing import List, Tuple


class SafetyScorer:
    """安全评分计算器"""
    
    def w_number(self, n: int, m: int, N: int, M: int) -> Tuple[float, float]:
        """
        数量分析权重计算
        
        Args:
            n: 当前记录数
            m: 当前属性数
            N: 总记录数
            M: 总属性数
            
        Returns:
            Tuple[记录权重, 属性权重]
        """
        w_recode = n / N
        w_field = m / M
        return w_recode, w_field
    
    def w_correlation_matrix(self, correlation_matrix: np.ndarray) -> List[float]:
        """
        关联安全等级计算
        
        Args:
            correlation_matrix: 相关性矩阵
            
        Returns:
            关联权重列表
        """
        w_connections = []
        for i in range(correlation_matrix.shape[0]):
            w_connection = 0
            for j in range(correlation_matrix.shape[1]):
                if correlation_matrix[i, j] > 0:
                    if 0.0 < correlation_matrix[i][j] < 0.3:
                        w_connection += 0.3
                    elif 0.3 < correlation_matrix[i][j] < 0.7:
                        w_connection += 0.7
                    else:
                        w_connection += 1
            w_connections.append(round(w_connection, 1))
        return w_connections
    
    def operation_matrix(self, m_d: List[int], t_d: List[int]) -> np.ndarray:
        """
        场景分析矩阵计算
        
        Args:
            m_d: 安全等级列表
            t_d: 场景参数列表
            
        Returns:
            操作矩阵
        """
        m_d_trans = np.array([m_d]).T
        t_d = np.array([t_d])
        M = m_d_trans @ t_d
        return M
    
    def w_operation(self, M: np.ndarray, M_subset: np.ndarray) -> float:
        """
        操作权重计算
        
        Args:
            M: 总操作矩阵
            M_subset: 子集操作矩阵
            
        Returns:
            操作权重
        """
        w_operation_ = np.sum(M_subset) / np.sum(M)
        return w_operation_
    
    def total_recode_count(self, data: pd.DataFrame, categorical_columns: List[str]) -> Tuple[np.ndarray, List[int], np.ndarray]:
        """
        全局记录唯一性分析
        
        Args:
            data: 数据框
            categorical_columns: 分类列名
            
        Returns:
            Tuple[唯一行, 频次, 权重]
        """
        # 对行向量进行唯一性分析并计数
        data_tuples = [tuple(row) for row in data[categorical_columns].values]
        frequency_counter = Counter(data_tuples)
        filtered_data = np.array([list(key) for key, count in frequency_counter.items()])
        frequencies = [count for key, count in frequency_counter.items()]
        unique_rows, counts = filtered_data, frequencies
        w_recode_count = counts / np.sum(counts)
        return unique_rows, counts, w_recode_count
    
    def distance(self, data: pd.DataFrame, flag: bool = True) -> List[float]:
        """
        计算距离
        
        Args:
            data: 数据框
            flag: 是否标准化
            
        Returns:
            距离列表
        """
        distances = []
        
        if flag:
            # 标准化数据
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data)
            # 计算欧氏距离
            distances = (squareform(pdist(scaled_data, metric='euclidean')).sum(axis=1)) / (data.shape[0] * data.shape[1])
        else:
            for c1 in data.values:
                total = 0
                for c2 in data.values:
                    diff = np.where(c1 == c2, 0, 1)
                    sum_diff = np.sum(diff) / data.shape[1]
                    total += sum_diff
                distances.append(total / data.shape[0])
        
        return distances
    
    def w_correlation(self, NA: pd.DataFrame, CA: pd.DataFrame, categorical_columns: List[str]) -> float:
        """
        相似性分析权重计算
        
        Args:
            NA: 数值型数据
            CA: 分类型数据
            categorical_columns: 分类列名
            
        Returns:
            相关性权重
        """
        n_sum, c_sum = 0, 0
        w_n = NA.shape[1] / (NA.shape[1] + CA.shape[1]) if not NA.empty else 0
        w_c = CA.shape[1] / (NA.shape[1] + CA.shape[1]) if not CA.empty else 0
        
        if not NA.empty:
            numerical_distances = self.distance(NA, flag=True)
            n_sum = numerical_distances.sum() / len(numerical_distances)
        
        if not CA.empty:
            unique_rows, counts, w_recode_count = self.total_recode_count(CA, categorical_columns)
            categorical_distances = self.distance(pd.DataFrame(unique_rows), flag=False)
            for i in range(len(w_recode_count)):
                c_sum += w_recode_count[i] * categorical_distances[i]
        
        w_correlation_ = 1 - (n_sum * w_n + c_sum * w_c)
        return w_correlation_
    
    def w_total(self, w_recode: float, w_field: float, w_operation: float, w_correlation: float) -> float:
        """
        计算总的安全分数
        
        Args:
            w_recode: 记录权重
            w_field: 属性权重
            w_operation: 操作权重
            w_correlation: 相关性权重
            
        Returns:
            总权重
        """
        w = w_recode * 0.1 + w_field * 0.1 + w_operation * 0.5 + w_correlation * 0.3
        return w
    
    def cramers_v(self, x: np.ndarray, y: np.ndarray) -> float:
        """计算Cramer's V"""
        confusion_matrix = pd.crosstab(x, y)
        chi2 = chi2_contingency(confusion_matrix)[0]
        n = confusion_matrix.sum().sum()
        r, k = confusion_matrix.shape
        return np.sqrt(chi2 / (n * (min(k - 1, r - 1))))
    
    def correlation_ratio(self, categories: np.ndarray, measurements: np.ndarray) -> float:
        """计算相关性比率"""
        fcat, _ = pd.factorize(categories)
        cat_num = np.max(fcat) + 1
        y_avg_array = np.zeros(cat_num)
        n_array = np.zeros(cat_num)
        
        for i in range(cat_num):
            index = np.argwhere(fcat == i).flatten()
            cat_measures = measurements[index]
            n_array[i] = len(cat_measures)
            y_avg_array[i] = np.mean(cat_measures)
        
        y_total_avg = np.sum(y_avg_array * n_array) / np.sum(n_array)
        numerator = np.sum(n_array * (y_avg_array - y_total_avg) ** 2)
        denominator = np.sum((measurements - y_total_avg) ** 2)
        
        if denominator == 0:
            return 0.0
        else:
            return np.sqrt(numerator / denominator)
    
    def calculate_correlation_matrix(self, df: pd.DataFrame, attributes: List[str]) -> pd.DataFrame:
        """
        计算字段相关性矩阵
        
        Args:
            df: 数据框
            attributes: 属性列表
            
        Returns:
            相关性矩阵
        """
        cols = attributes
        correlation_matrix = pd.DataFrame(index=cols, columns=cols)
        
        # 计算相关性
        for col1 in attributes:
            for col2 in attributes:
                if col1 == col2:
                    corr = 0.0
                else:
                    if df[col1].dtype == 'object' and df[col2].dtype == 'object':
                        corr = self.cramers_v(df[col1].values, df[col2].values)
                    elif df[col1].dtype == 'object' or df[col2].dtype == 'object':
                        if df[col1].dtype == 'object':
                            corr = self.correlation_ratio(df[col1].values, df[col2].values)
                        else:
                            corr = self.correlation_ratio(df[col2].values, df[col1].values)
                    else:
                        corr = df[[col1, col2]].corr().iloc[0, 1]
                correlation_matrix.loc[col1, col2] = round(corr, 2)
        
        correlation_matrix = correlation_matrix.astype(float)
        return correlation_matrix
    
    def degree_association_rule(self, correlation_matrix: pd.DataFrame, attributes: List[str], 
                               sampled_attributes: List[str], M_d: List[int], cluster: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        关联规则等级计算
        
        Args:
            correlation_matrix: 相关性矩阵
            attributes: 属性列表
            sampled_attributes: 采样属性
            M_d: 安全等级
            cluster: 聚类结果
            
        Returns:
            Tuple[子集安全等级, 总安全等级]
        """
        col_labels = ['cluster', 'M_d', 'association_d', 'M_d_new', 'm_d']
        row_labels = attributes
        degree_df = pd.DataFrame(np.zeros((len(row_labels), len(col_labels))), 
                                index=row_labels, columns=col_labels)
        
        degree_df['cluster'] = cluster
        degree_df['M_d'] = M_d
        
        for i in sampled_attributes:
            degree_up = 0
            cluster_row = degree_df.loc[i, 'cluster']
            degree_row = degree_df.loc[i, 'M_d']
            
            for j in sampled_attributes:
                cluster_column = degree_df.loc[j, 'cluster']
                degree_column = degree_df.loc[j, 'M_d']
                
                if cluster_row == cluster_column:
                    corr = correlation_matrix.loc[i, j]
                    if degree_row == degree_column:
                        degree_up += corr * degree_row
                    else:
                        degree_up += corr * abs(degree_column - cluster_column)
            
            degree_df.loc[i, 'association_d'] = round(degree_up, 2)
            degree_df.loc[i, 'm_d'] = degree_df.loc[i, 'M_d'] + degree_df.loc[i, 'association_d']
        
        degree_df['M_d_mew'] = degree_df['M_d'] + degree_df['association_d']
        return degree_df['m_d'].values, degree_df['M_d_mew'].values
    
    def kmeans_cluster(self, data: pd.DataFrame, k: int, numeric_columns: List[str], 
                      categorical_columns: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        K-means聚类
        
        Args:
            data: 数据框
            k: 聚类数
            numeric_columns: 数值列
            categorical_columns: 分类列
            
        Returns:
            Tuple[聚类结果, 合并数据]
        """
        # 对数值型数据进行标准化处理
        scaler = StandardScaler()
        scaled_numeric_data = scaler.fit_transform(data[numeric_columns])
        
        # 对分类型数据进行编码
        label_encoders = {}
        encoded_categorical_data = []
        
        for col in categorical_columns:
            le = LabelEncoder()
            encoded_col = le.fit_transform(data[col])
            encoded_categorical_data.append(encoded_col)
            label_encoders[col] = le
        
        # 将数值数据和编码后的分类数据合并
        merged_data = np.hstack((scaled_numeric_data, np.array(encoded_categorical_data).T))
        merged_dataT = merged_data.T
        
        kmeans = KMeans(n_clusters=k, random_state=42)
        cluster = kmeans.fit_predict(merged_dataT)
        
        return cluster, merged_dataT

