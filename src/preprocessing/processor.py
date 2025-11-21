import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from typing import Tuple, List, Optional, Union
import joblib
import os

class DataProcessor:
    """数据预处理器"""
    
    def __init__(self, sequence_length: int = 60):
        """
        初始化预处理器
        
        Args:
            sequence_length: LSTM序列长度（时间步）
        """
        self.sequence_length = sequence_length
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_columns = []
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗
        
        Args:
            df: 原始DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        df = df.copy()
        
        # 替换无穷大值
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # 处理缺失值
        # 1. 前向填充
        df = df.ffill()
        # 2. 后向填充（处理开头的数据）
        df = df.bfill()
        # 3. 如果还有缺失（通常是整列缺失），填充0
        df = df.fillna(0)
        
        return df
        
    def prepare_features(self, df: pd.DataFrame, target_col: str = 'close') -> Tuple[pd.DataFrame, List[str]]:
        """
        准备特征列
        
        Args:
            df: 包含技术指标的DataFrame
            target_col: 目标列名
            
        Returns:
            (特征DataFrame, 特征列名列表)
        """
        # 排除非数值列和不需要的列
        exclude_cols = ['trade_date', 'ts_code', 'date', 'symbol', 'code', 'name']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # 确保所有特征都是数值型
        for col in feature_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        self.feature_columns = feature_cols
        return df[feature_cols], feature_cols

    def create_sequences(self, data: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        创建时间序列数据 (用于LSTM)
        
        Args:
            data: 特征数据矩阵 (samples, features)
            target: 目标数据向量 (samples,)
            
        Returns:
            (X, y)
            X shape: (samples - seq_len, seq_len, features)
            y shape: (samples - seq_len,)
        """
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(target[i + self.sequence_length])
            
        return np.array(X), np.array(y)
    
    def normalize_data(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        数据归一化
        
        Args:
            df: 特征DataFrame
            is_training: 是否为训练模式（训练模式会fit_transform，预测模式只transform）
            
        Returns:
            归一化后的DataFrame
        """
        if is_training:
            scaled_data = self.scaler.fit_transform(df)
        else:
            scaled_data = self.scaler.transform(df)
            
        return pd.DataFrame(scaled_data, columns=df.columns, index=df.index)
    
    def save_scaler(self, path: str):
        """保存缩放器"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.scaler, path)
        
    def load_scaler(self, path: str):
        """加载缩放器"""
        if os.path.exists(path):
            self.scaler = joblib.load(path)
        else:
            print(f"警告: 缩放器文件 {path} 不存在")

    def generate_labels(self, df: pd.DataFrame, days: int = 5, threshold: float = 0.05) -> pd.DataFrame:
        """
        生成分类标签（用于XGBoost等分类模型）
        
        Args:
            df: 包含close列的DataFrame
            days: 预测未来N天
            threshold: 涨幅阈值 (例如0.05表示5%)
            
        Returns:
            添加了label列的DataFrame
        """
        df = df.copy()
        
        # 计算未来N天的收益率
        df[f'future_return_{days}d'] = df['close'].shift(-days) / df['close'] - 1
        
        # 生成标签：1表示上涨超过阈值，0表示其他
        df['label'] = (df[f'future_return_{days}d'] > threshold).astype(int)
        
        # 移除最后N行（因为没有未来数据）
        df = df.dropna(subset=[f'future_return_{days}d'])
        
        return df
