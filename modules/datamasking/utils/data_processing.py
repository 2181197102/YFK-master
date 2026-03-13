"""
数据预处理工具
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
import os
import json

class DataProcessor:
    """数据处理器"""

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        加载保存的医疗JSON文件，将其转换为DataFrame

        Args:
            file_path: 文件路径

        Returns:
            数据框
        """
        print(f'=>loading from {file_path}')
        ext = os.path.splitext(file_path)[1].lower()
        if ext != ".json":
            raise ValueError(f"请上传JSON医疗数据文件: {ext}")

        with open(file_path, 'r', encoding='utf-8') as f:
            js_data = json.load(f)

        # 兼容各种结构（从routes.py来，完整json，主要数据在'results'字段）
        if isinstance(js_data, dict) and "results" in js_data:
            records = js_data["results"]
        elif isinstance(js_data, list):
            records = js_data
        else:
            raise ValueError(f"不支持的JSON数据结构: 顶层类型 {type(js_data)}")

        data_raw = pd.DataFrame(records)
        print('=>complete loading')

        # 数据清洗（示例：剔除含有?或全为空的列/行等）
        print('=>start cleaning')
        print('===>before:')
        print(data_raw.shape)

        # 清理: 替换'?'为NaN，丢弃缺失值
        data = data_raw.replace('?', np.nan)
        data = data.dropna(axis=0, how='any')

        print('===>after:')
        print(data.shape)
        print('=>is cleaned\n')

        return data

    def get_data_messages(
        self, file_path: str
    ) -> Tuple[List[str], int, int, List[int], List[int], List[str], List[str], List[str], int]:
        """
        获取JSON医疗数据文件的基本信息（属性、数量等），依据字段描述区分类型和安全等级，
        并统计需要脱敏的字段（security_category != "NON_SENSITIVE"）

        Args:
            file_path: 文件路径

        Returns:
            Tuple[属性列表, 记录数, 属性数, 场景参数, 安全等级, 数值列, 分类列, 需要脱敏的字段列表, 需要脱敏的字段数]
            属性列表顺序、security_level顺序、categorical/numerical与data_code_details保持一致
        """
        # 读取文件
        with open(file_path, "r", encoding="utf-8") as f:
            js_data = json.load(f)

        if not (isinstance(js_data, dict) and "results" in js_data and "data_code_details" in js_data):
            raise ValueError("文件结构错误，缺少'results'或'data_code_details'字段")

        # 提取字段描述和数据
        data_code_details: Dict[str, Any] = js_data["data_code_details"]
        records = js_data["results"]

        attributes = []
        categorical_columns = []
        numerical_columns = []
        security_levels = []
        need_masking_fields = []

        for attr, detail in data_code_details.items():
            attributes.append(attr)
            level = detail.get("security_level", 1)
            security_levels.append(level)
            data_type = detail.get("data_type", 0)
            # 0 = categorical, 1 = numerical
            if data_type == 0:
                categorical_columns.append(attr)
            elif data_type == 1:
                numerical_columns.append(attr)
            # 判断是否需要脱敏
            security_category = detail.get("security_category", "")
            if security_category != "NON_SENSITIVE":
                need_masking_fields.append(attr)

        # 加载 records 到 DataFrame 以确定实际行数
        df = pd.DataFrame(records)
        N = len(df)
        M = len(attributes)

        # TODO: 依据实际场景需要，下面两个参数可定制
        T_d = [5, 0, 0, 0]  # 场景参数例：记录数
        M_d = security_levels  # 按字段顺序的安全等级列表

        # 打印返回参数
        print("get_data_messages 返回参数:")
        print(f"属性列表: {attributes}")
        print(f"记录数: {N}")
        print(f"属性数: {M}")
        print(f"场景参数T_d: {T_d}")
        print(f"安全等级M_d: {M_d}")
        print(f"数值列: {numerical_columns}")
        print(f"分类列: {categorical_columns}")
        print(f"需要脱敏的字段: {need_masking_fields}")
        print(f"需要脱敏的字段数: {len(need_masking_fields)}")

        return attributes, N, M, T_d, M_d, numerical_columns, categorical_columns, need_masking_fields, len(need_masking_fields)

    def get_file_headers(self, file_path: str) -> List[str]:
        """
        获取JSON医疗文件的字段名

        Args:
            file_path: 文件路径

        Returns:
            列名列表
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                js_data = json.load(f)
            # 优先基于data_code_details顺序返回字段
            if isinstance(js_data, dict) and "data_code_details" in js_data:
                return list(js_data["data_code_details"].keys())
            elif isinstance(js_data, dict) and "results" in js_data:
                records = js_data["results"]
            elif isinstance(js_data, list):
                records = js_data
            else:
                raise ValueError(f"不支持的JSON数据结构: 顶层类型 {type(js_data)}")
            if not records:
                return []
            return list(records[0].keys())
        else:
            raise ValueError(f"只支持JSON格式的医疗文件, 当前: {ext}")

    def validate_file(self, file_path: str) -> bool:
        """
        验证上传JSON医疗数据文件有效性

        Args:
            file_path: 文件路径

        Returns:
            是否有效
        """
        try:
            if not os.path.exists(file_path):
                return False

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False

            headers = self.get_file_headers(file_path)
            if not headers:
                return False

            return True

        except Exception as e:
            print(f"文件验证失败: {str(e)}")
            return False

