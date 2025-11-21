"""
市场情绪特征提取模块
Market Sentiment Features

提取市场情绪相关特征：
- 换手率
- 量比
- 涨跌家数比
- 板块联动性
"""

import pandas as pd
import numpy as np
from typing import Optional
import yaml


class MarketSentiment:
    """市场情绪特征提取器"""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """初始化市场情绪提取器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def calculate_turnover_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算换手率相关特征
        
        Args:
            df: 包含turnover_rate列的DataFrame
        
        Returns:
            添加了换手率特征的DataFrame
        """
        if 'turnover_rate' not in df.columns:
            # 如果没有换手率，尝试计算
            if 'volume' in df.columns and 'total_share' in df.columns:
                df['turnover_rate'] = df['volume'] / df['total_share'] * 100
        
        if 'turnover_rate' in df.columns:
            # 换手率移动平均
            df['turnover_ma_5'] = df['turnover_rate'].rolling(window=5).mean()
            df['turnover_ma_20'] = df['turnover_rate'].rolling(window=20).mean()
            
            # 换手率相对强度
            df['turnover_ratio'] = df['turnover_rate'] / df['turnover_ma_20']
        
        return df
    
    def calculate_volume_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算量比
        
        Args:
            df: 包含volume列的DataFrame
        
        Returns:
            添加了量比特征的DataFrame
        """
        if 'volume' in df.columns:
            # 5日平均成交量
            vol_ma_5 = df['volume'].rolling(window=5).mean()
            
            # 量比 = 当日成交量 / 5日平均成交量
            df['volume_ratio'] = df['volume'] / vol_ma_5
            
            # 成交量变化率
            df['volume_change'] = df['volume'].pct_change() * 100
        
        return df
    
    def calculate_amplitude_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算振幅相关特征
        
        Args:
            df: 包含high, low, close列的DataFrame
        
        Returns:
            添加了振幅特征的DataFrame
        """
        if all(col in df.columns for col in ['high', 'low', 'close']):
            # 日振幅
            df['amplitude'] = (df['high'] - df['low']) / df['close'].shift(1) * 100
            
            # 平均振幅
            df['amplitude_ma_5'] = df['amplitude'].rolling(window=5).mean()
            df['amplitude_ma_20'] = df['amplitude'].rolling(window=20).mean()
            
            # 振幅相对强度
            df['amplitude_ratio'] = df['amplitude'] / df['amplitude_ma_20']
        
        return df
    
    def calculate_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算动量特征
        
        Args:
            df: 包含close列的DataFrame
        
        Returns:
            添加了动量特征的DataFrame
        """
        if 'close' in df.columns:
            # 动量指标（N日涨跌幅）
            for n in [3, 5, 10, 20]:
                df[f'momentum_{n}'] = df['close'].pct_change(periods=n) * 100
            
            # 加速度（动量的变化率）
            df['acceleration_5'] = df['momentum_5'].diff()
        
        return df
    
    def calculate_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算波动率特征
        
        Args:
            df: 包含close列的DataFrame
        
        Returns:
            添加了波动率特征的DataFrame
        """
        if 'close' in df.columns:
            # 收益率
            returns = df['close'].pct_change()
            
            # 历史波动率（标准差）
            df['volatility_5'] = returns.rolling(window=5).std() * np.sqrt(252) * 100
            df['volatility_20'] = returns.rolling(window=20).std() * np.sqrt(252) * 100
            
            # 波动率比率
            df['volatility_ratio'] = df['volatility_5'] / df['volatility_20']
        
        return df
    
    def calculate_price_position(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算价格位置特征
        
        Args:
            df: 包含close, high, low列的DataFrame
        
        Returns:
            添加了价格位置特征的DataFrame
        """
        if all(col in df.columns for col in ['close', 'high', 'low']):
            # 计算N日最高价和最低价
            for n in [5, 10, 20, 60]:
                high_n = df['high'].rolling(window=n).max()
                low_n = df['low'].rolling(window=n).min()
                
                # 价格在N日区间的位置（0-100）
                df[f'price_position_{n}'] = (df['close'] - low_n) / (high_n - low_n) * 100
        
        return df
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算趋势强度
        
        Args:
            df: 包含close列的DataFrame
        
        Returns:
            添加了趋势强度特征的DataFrame
        """
        if 'close' in df.columns:
            # ADX (Average Directional Index) 简化版
            # 使用收盘价的移动平均斜率作为趋势强度
            for n in [5, 10, 20]:
                ma = df['close'].rolling(window=n).mean()
                df[f'trend_strength_{n}'] = (ma - ma.shift(n)) / ma.shift(n) * 100
        
        return df
    
    def calculate_all_sentiment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有市场情绪特征
        
        Args:
            df: 原始数据DataFrame
        
        Returns:
            包含所有情绪特征的DataFrame
        """
        df = df.copy()
        
        # 确保按日期升序排序（计算指标需要从旧到新）
        if 'trade_date' in df.columns:
            df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        elif 'date' in df.columns:
            df = df.sort_values('date', ascending=True).reset_index(drop=True)
        
        df = self.calculate_turnover_features(df)
        df = self.calculate_volume_ratio(df)
        df = self.calculate_amplitude_features(df)
        df = self.calculate_momentum_features(df)
        df = self.calculate_volatility_features(df)
        df = self.calculate_price_position(df)
        df = self.calculate_trend_strength(df)
        
        # 计算完成后，按日期降序排列（最新的在前面）
        if 'trade_date' in df.columns:
            df = df.sort_values('trade_date', ascending=False).reset_index(drop=True)
        elif 'date' in df.columns:
            df = df.sort_values('date', ascending=False).reset_index(drop=True)
        
        return df
    
    def get_feature_columns(self) -> list:
        """
        获取所有市场情绪特征列名
        
        Returns:
            特征列名列表
        """
        features = [
            # 换手率特征
            'turnover_ma_5', 'turnover_ma_20', 'turnover_ratio',
            # 量比特征
            'volume_ratio', 'volume_change',
            # 振幅特征
            'amplitude', 'amplitude_ma_5', 'amplitude_ma_20', 'amplitude_ratio',
            # 动量特征
            'momentum_3', 'momentum_5', 'momentum_10', 'momentum_20', 'acceleration_5',
            # 波动率特征
            'volatility_5', 'volatility_20', 'volatility_ratio',
            # 价格位置特征
            'price_position_5', 'price_position_10', 'price_position_20', 'price_position_60',
            # 趋势强度特征
            'trend_strength_5', 'trend_strength_10', 'trend_strength_20'
        ]
        
        return features


if __name__ == '__main__':
    # 测试代码
    from src.data_acquisition.stock_data import StockDataFetcher
    
    # 获取数据
    fetcher = StockDataFetcher()
    df = fetcher.get_daily_data('600519.SH')
    
    # 计算市场情绪特征
    sentiment = MarketSentiment()
    df_with_sentiment = sentiment.calculate_all_sentiment_features(df)
    
    print("市场情绪特征计算完成！")
    print(df_with_sentiment[sentiment.get_feature_columns()].head())
