"""
k-匿名方法实现
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Set


class KAnonymityProcessor:
    """k-匿名处理器"""
    
    def get_spans(self, df: pd.DataFrame, categorical_columns: List[str], 
                  partition: pd.Index, scale: dict = None) -> dict:
        """
        获取数值型数据的最大值-最小值，即数据跨度
        
        Args:
            df: 数据框
            categorical_columns: 分类列名
            partition: 分区索引
            scale: 缩放因子
            
        Returns:
            各列的跨度
        """
        spans = {}
        for column in df.columns:
            if column in categorical_columns:
                # 分类字段，获取属性值取值个数
                span = len(df[column][partition].unique())
            else:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                span = df[column][partition].max() - df[column][partition].min()
            
            if scale is not None:
                span = span / scale[column]
            
            spans[column] = span
        
        return spans
    
    def split(self, df: pd.DataFrame, categorical_columns: List[str], 
              partition: pd.Index, column: str) -> Tuple[pd.Index, pd.Index]:
        """
        对数据进行分区
        
        Args:
            df: 数据框
            categorical_columns: 分类列名
            partition: 分区索引
            column: 分割列
            
        Returns:
            分割后的两个分区
        """
        dfp = df[column][partition]
        
        if column in categorical_columns:
            values = dfp.unique()
            lv = set(values[:len(values)//2])
            rv = set(values[len(values)//2:])
            return dfp.index[dfp.isin(lv)], dfp.index[dfp.isin(rv)]
        else:
            median = dfp.median()
            dfl = dfp.index[dfp < median]
            dfr = dfp.index[dfp >= median]
            return dfl, dfr
    
    def is_k_anonymous(self, df: pd.DataFrame, partition: pd.Index, 
                      sensitive_column: str, k: int = 3) -> bool:
        """
        检查分区是否满足k-匿名
        
        Args:
            df: 数据框
            partition: 分区索引
            sensitive_column: 敏感列名
            k: k值
            
        Returns:
            是否满足k-匿名
        """
        return len(partition) >= k
    
    def partition_dataset(self, df: pd.DataFrame, feature_columns: List[str], 
                         sensitive_column: str, categorical_columns: List[str], 
                         scale: dict, k: int) -> List[pd.Index]:
        """
        对数据集进行分区
        
        Args:
            df: 数据框
            feature_columns: 特征列
            sensitive_column: 敏感列
            categorical_columns: 分类列
            scale: 缩放因子
            k: k值
            
        Returns:
            分区列表
        """
        finished_partitions = []
        partitions = [df.index]
        
        while partitions:
            partition = partitions.pop(0)
            spans = self.get_spans(df[feature_columns], categorical_columns, partition, scale)
            
            for column, span in sorted(spans.items(), key=lambda x: -x[1]):
                lp, rp = self.split(df, categorical_columns, partition, column)
                
                if not self.is_k_anonymous(df, lp, sensitive_column, k) or \
                   not self.is_k_anonymous(df, rp, sensitive_column, k):
                    continue
                
                partitions.extend((lp, rp))
                break
            else:
                finished_partitions.append(partition)
        
        return finished_partitions
    
    def agg_categorical_column(self, series: pd.Series) -> List[str]:
        """聚合分类列"""
        return [','.join(set(series))]
    
    def agg_numerical_column(self, series: pd.Series) -> int:
        """聚合数值列"""
        return int(series.mean())
    
    def build_anonymized_dataset(self, df: pd.DataFrame, categorical_columns: List[str], 
                                partitions: List[pd.Index], feature_columns: List[str], 
                                sensitive_column: str) -> pd.DataFrame:
        """
        构建匿名化数据集
        
        Args:
            df: 原始数据框
            categorical_columns: 分类列
            partitions: 分区列表
            feature_columns: 特征列
            sensitive_column: 敏感列
            
        Returns:
            匿名化后的数据框
        """
        rows = []
        
        for i, partition in enumerate(partitions):
            if i % 100 == 1:
                print(f"Finished {i} partitions...")
            
            # 提取当前分区的数据
            partition_df = df.loc[partition]
            
            # 初始化聚合结果
            aggregated_data = {}
            
            # 逐列应用聚合函数
            for column in feature_columns:
                if column in categorical_columns:
                    aggregated_data[column] = self.agg_categorical_column(partition_df[column])
                else:
                    aggregated_data[column] = self.agg_numerical_column(partition_df[column])
            
            # 获取敏感列的值
            sensitive_values = partition_df[sensitive_column].unique()
            
            # 为每个敏感值创建新的行
            for value in sensitive_values:
                current_values = aggregated_data.copy()
                current_values[sensitive_column] = value
                rows.append(current_values)
        
        return pd.DataFrame(rows)
    
    def process_k_anonymity(self, data: pd.DataFrame, feature_columns: List[str], 
                           sensitive_column: str, categorical_columns: List[str], 
                           k: int) -> pd.DataFrame:
        """
        执行k-匿名处理
        
        Args:
            data: 原始数据
            feature_columns: 特征列
            sensitive_column: 敏感列
            categorical_columns: 分类列
            k: k值
            
        Returns:
            处理后的数据
        """
        # 获取数据跨度
        full_spans = self.get_spans(data, categorical_columns, data.index)
        
        # 分区数据集
        finished_partitions = self.partition_dataset(
            data, feature_columns, sensitive_column, 
            categorical_columns, full_spans, k
        )
        
        # 构建匿名化数据集
        anonymized_data = self.build_anonymized_dataset(
            data, categorical_columns, finished_partitions, 
            feature_columns, sensitive_column
        )
        
        # 清理数据
        anonymized_data = anonymized_data.replace('nan', np.nan)
        anonymized_data = anonymized_data.dropna(axis=0)
        
        return anonymized_data
