"""
技术指标计算模块
Technical Indicators Calculator

计算常用技术指标：
- 移动平均线 (MA, EMA)
- MACD
- RSI
- KDJ
- BOLL
- ATR
- OBV
等
"""

import pandas as pd
import numpy as np
from typing import Optional
import yaml


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """初始化技术指标计算器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.params = self.config['features']['technical']
    
    def calculate_ma(self, df: pd.DataFrame, periods: Optional[list] = None) -> pd.DataFrame:
        """
        计算移动平均线
        
        Args:
            df: 包含close列的DataFrame
            periods: 周期列表，默认从配置读取
        
        Returns:
            添加了MA列的DataFrame
        """
        if periods is None:
            periods = self.params['ma_periods']
        
        for period in periods:
            df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
        
        return df
    
    def calculate_ema(self, df: pd.DataFrame, periods: Optional[list] = None) -> pd.DataFrame:
        """
        计算指数移动平均线
        
        Args:
            df: 包含close列的DataFrame
            periods: 周期列表
        
        Returns:
            添加了EMA列的DataFrame
        """
        if periods is None:
            periods = self.params['ema_periods']
        
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        return df
    
    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算MACD指标
        
        Args:
            df: 包含close列的DataFrame
        
        Returns:
            添加了MACD相关列的DataFrame
        """
        params = self.params['macd_params']
        fast, slow, signal = params[0], params[1], params[2]
        
        # 计算快线和慢线
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        # MACD线
        df['macd'] = ema_fast - ema_slow
        
        # 信号线
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        
        # MACD柱
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: Optional[int] = None) -> pd.DataFrame:
        """
        计算RSI指标
        
        Args:
            df: 包含close列的DataFrame
            period: RSI周期
        
        Returns:
            添加了RSI列的DataFrame
        """
        if period is None:
            period = self.params['rsi_period']
        
        # 计算价格变化
        delta = df['close'].diff()
        
        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # 计算RS和RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def calculate_kdj(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算KDJ指标
        
        Args:
            df: 包含high, low, close列的DataFrame
        
        Returns:
            添加了KDJ列的DataFrame
        """
        params = self.params['kdj_params']
        n, m1, m2 = params[0], params[1], params[2]
        
        # 计算RSV
        low_min = df['low'].rolling(window=n).min()
        high_max = df['high'].rolling(window=n).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        
        # 计算K、D、J
        df['kdj_k'] = rsv.ewm(com=m1-1, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=m2-1, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        return df
    
    def calculate_boll(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算布林带指标
        
        Args:
            df: 包含close列的DataFrame
        
        Returns:
            添加了BOLL列的DataFrame
        """
        params = self.params['boll_params']
        period, std_dev = params[0], params[1]
        
        # 中轨
        df['boll_mid'] = df['close'].rolling(window=period).mean()
        
        # 标准差
        std = df['close'].rolling(window=period).std()
        
        # 上轨和下轨
        df['boll_upper'] = df['boll_mid'] + std_dev * std
        df['boll_lower'] = df['boll_mid'] - std_dev * std
        
        # 布林带宽度
        df['boll_width'] = (df['boll_upper'] - df['boll_lower']) / df['boll_mid']
        
        return df
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算ATR (Average True Range)
        
        Args:
            df: 包含high, low, close列的DataFrame
            period: ATR周期
        
        Returns:
            添加了ATR列的DataFrame
        """
        # 计算True Range
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # 计算ATR
        df['atr'] = tr.rolling(window=period).mean()
        
        return df
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算OBV (On Balance Volume)
        
        Args:
            df: 包含close和volume列的DataFrame
        
        Returns:
            添加了OBV列的DataFrame
        """
        obv = [0]
        
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        df['obv'] = obv
        
        return df
    
    def calculate_volume_ma(self, df: pd.DataFrame, periods: list = [5, 10, 20]) -> pd.DataFrame:
        """
        计算成交量移动平均
        
        Args:
            df: 包含volume列的DataFrame
            periods: 周期列表
        
        Returns:
            添加了成交量MA列的DataFrame
        """
        for period in periods:
            df[f'vol_ma_{period}'] = df['volume'].rolling(window=period).mean()
        
        return df
    
    def calculate_price_change(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算价格变化相关指标
        
        Args:
            df: 包含close列的DataFrame
        
        Returns:
            添加了价格变化列的DataFrame
        """
        # 日涨跌幅
        df['pct_change'] = df['close'].pct_change() * 100
        
        # N日涨跌幅
        for n in [3, 5, 10, 20]:
            df[f'pct_change_{n}d'] = df['close'].pct_change(periods=n) * 100
        
        # 振幅
        df['amplitude'] = (df['high'] - df['low']) / df['close'].shift(1) * 100
        
        return df
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            df: 原始OHLCV数据
        
        Returns:
            包含所有技术指标的DataFrame
        """
        # 确保列名统一
        df = df.copy()
        
        # 标准化列名
        column_mapping = {
            'trade_date': 'date',
            'vol': 'volume'
        }
        df = df.rename(columns=column_mapping)
        
        # 检查必需的列
        required_cols = ['close', 'high', 'low', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"缺少必需的列: {missing_cols}. 当前列: {df.columns.tolist()}")
        
        # 按日期升序排序（技术指标计算需要从旧到新）
        if 'date' in df.columns:
            df = df.sort_values('date', ascending=True).reset_index(drop=True)
        
        # 计算各类指标
        try:
            df = self.calculate_ma(df)
            df = self.calculate_ema(df)
            df = self.calculate_macd(df)
            df = self.calculate_rsi(df)
            df = self.calculate_kdj(df)
            df = self.calculate_boll(df)
            df = self.calculate_atr(df)
            df = self.calculate_obv(df)
            df = self.calculate_volume_ma(df)
            df = self.calculate_price_change(df)
        except Exception as e:
            print(f"计算技术指标时出错: {str(e)}")
            raise
        
        # 计算完成后，按日期降序排列（最新的在前面）
        if 'date' in df.columns:
            df = df.sort_values('date', ascending=False).reset_index(drop=True)
        
        return df
    
    def get_feature_columns(self) -> list:
        """
        获取所有技术指标特征列名
        
        Returns:
            特征列名列表
        """
        features = []
        
        # MA特征
        for period in self.params['ma_periods']:
            features.append(f'ma_{period}')
        
        # EMA特征
        for period in self.params['ema_periods']:
            features.append(f'ema_{period}')
        
        # MACD特征
        features.extend(['macd', 'macd_signal', 'macd_hist'])
        
        # RSI特征
        features.append('rsi')
        
        # KDJ特征
        features.extend(['kdj_k', 'kdj_d', 'kdj_j'])
        
        # BOLL特征
        features.extend(['boll_mid', 'boll_upper', 'boll_lower', 'boll_width'])
        
        # ATR特征
        features.append('atr')
        
        # OBV特征
        features.append('obv')
        
        # 成交量MA
        features.extend(['vol_ma_5', 'vol_ma_10', 'vol_ma_20'])
        
        # 价格变化
        features.extend(['pct_change', 'pct_change_3d', 'pct_change_5d', 
                        'pct_change_10d', 'pct_change_20d', 'amplitude'])
        
        return features


if __name__ == '__main__':
    # 测试代码
    from src.data_acquisition.stock_data import StockDataFetcher
    
    # 获取数据
    fetcher = StockDataFetcher()
    df = fetcher.get_daily_data('600519.SH')
    
    # 计算技术指标
    calculator = TechnicalIndicators()
    df_with_indicators = calculator.calculate_all_indicators(df)
    
    print("技术指标计算完成！")
    print(df_with_indicators.head())
    print(f"\n特征列: {calculator.get_feature_columns()}")
