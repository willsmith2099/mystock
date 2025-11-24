"""
股票行情数据获取模块
Stock Market Data Fetcher

支持多数据源：
- Tushare Pro
- AkShare
- yfinance
"""

import pandas as pd
import tushare as ts
import akshare as ak
from datetime import datetime, timedelta
from typing import Optional, List
import yaml


class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """
        初始化数据获取器
        
        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化Tushare
        tushare_token = self.config['data_sources']['tushare']['token']
        if tushare_token and tushare_token != 'your_tushare_token_here':
            ts.set_token(tushare_token)
            self.pro = ts.pro_api()
        else:
            self.pro = None
            print("警告: Tushare token未配置，部分功能将不可用")
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            股票列表DataFrame
        """
        if self.pro:
            # 使用Tushare获取
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
        else:
            # 使用AkShare获取
            df = ak.stock_info_a_code_name()
            df.columns = ['ts_code', 'name']
        
        return df
    
    def get_daily_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            stock_code: 股票代码（如：600519.SH 或 600519）
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            日线数据DataFrame
        """
        # 标准化股票代码
        if '.' not in stock_code:
            stock_code = self._normalize_stock_code(stock_code)
        
        # 默认获取最近1年数据
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        if self.pro:
            # 使用Tushare获取
            df = self.pro.daily(
                ts_code=stock_code,
                start_date=start_date,
                end_date=end_date
            )
        else:
            # 使用AkShare获取
            symbol = stock_code.split('.')[0]
            
            try:
                # 优先尝试东方财富 (Eastmoney)
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period='daily',
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                
                # 标准化列名：中文 -> 英文
                if not df.empty:
                    column_mapping = {
                        '日期': 'trade_date',
                        '股票代码': 'ts_code',
                        '开盘': 'open',
                        '收盘': 'close',
                        '最高': 'high',
                        '最低': 'low',
                        '成交量': 'vol',
                        '成交额': 'amount',
                        '振幅': 'amplitude',
                        '涨跌幅': 'pct_chg',
                        '涨跌额': 'change',
                        '换手率': 'turnover_rate'
                    }
                    df = df.rename(columns=column_mapping)
            except Exception as e:
                print(f"Eastmoney获取失败，尝试Sina: {str(e)}")
                try:
                    # 备用：新浪财经 (Sina)
                    # 转换代码格式: 600519.SH -> sh600519
                    sina_symbol = stock_code.lower().replace('.', '')
                    if sina_symbol.endswith('bj'):
                        # Sina可能不支持北交所或者格式不同，暂时忽略
                        raise ValueError("Sina不支持北交所")
                    
                    # 调整sina_symbol顺序: 600519sh -> sh600519
                    if sina_symbol.endswith('sh'):
                        sina_symbol = 'sh' + sina_symbol[:-2]
                    elif sina_symbol.endswith('sz'):
                        sina_symbol = 'sz' + sina_symbol[:-2]
                    
                    df = ak.stock_zh_a_daily(
                        symbol=sina_symbol,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # 标准化列名
                    if not df.empty:
                        # Sina返回: date, open, high, low, close, volume, amount, outstanding_share, turnover
                        df = df.rename(columns={
                            'date': 'trade_date',
                            'volume': 'vol'
                        })
                        # 计算涨跌幅等缺失字段
                        df['pct_chg'] = df['close'].pct_change() * 100
                        df['change'] = df['close'].diff()
                        df['ts_code'] = stock_code
                        
                        # 填充第一天的NaN (如果需要)
                        df = df.fillna(0)
                        
                except Exception as e2:
                    print(f"Sina获取失败: {str(e2)}")
                    return pd.DataFrame()
            
            # 通用处理
            if not df.empty:
                # 转换日期格式为 YYYYMMDD
                if 'trade_date' in df.columns:
                    df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
                
                # 确保数值列为float类型
                numeric_cols = ['open', 'close', 'high', 'low', 'vol', 'amount']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 按日期降序排列（最新的在前面）
                df = df.sort_values('trade_date', ascending=False).reset_index(drop=True)
        
        return df
    
    def get_realtime_data(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取实时行情数据
        
        Args:
            stock_codes: 股票代码列表
        
        Returns:
            实时行情DataFrame
        """
        if self.pro:
            # 使用Tushare获取
            codes_str = ','.join(stock_codes)
            df = self.pro.realtime_quote(ts_code=codes_str)
        else:
            # 使用AkShare获取
            df = ak.stock_zh_a_spot_em()
            df = df[df['代码'].isin([code.split('.')[0] for code in stock_codes])]
        
        return df
    
    def get_minute_data(
        self,
        stock_code: str,
        freq: str = '5min',
        start_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取分钟级数据
        
        Args:
            stock_code: 股票代码
            freq: 频率 (1min, 5min, 15min, 30min, 60min)
            start_date: 开始日期
        
        Returns:
            分钟数据DataFrame
        """
        symbol = stock_code.split('.')[0]
        
        # 使用AkShare获取分钟数据
        period_map = {
            '1min': '1',
            '5min': '5',
            '15min': '15',
            '30min': '30',
            '60min': '60'
        }
        
        period = period_map.get(freq, '5')
        df = ak.stock_zh_a_hist_min_em(
            symbol=symbol,
            period=period,
            adjust="qfq"
        )
        
        return df
    
    def get_financial_data(self, stock_code: str, report_type: str = 'balance') -> pd.DataFrame:
        """
        获取财务数据
        
        Args:
            stock_code: 股票代码
            report_type: 报表类型 (balance: 资产负债表, income: 利润表, cashflow: 现金流量表)
        
        Returns:
            财务数据DataFrame
        """
        if not self.pro:
            raise ValueError("财务数据需要Tushare Pro权限")
        
        report_map = {
            'balance': self.pro.balancesheet,
            'income': self.pro.income,
            'cashflow': self.pro.cashflow
        }
        
        func = report_map.get(report_type)
        if func:
            df = func(ts_code=stock_code)
            return df
        else:
            raise ValueError(f"不支持的报表类型: {report_type}")
    
    def _normalize_stock_code(self, code: str) -> str:
        """
        标准化股票代码
        
        Args:
            code: 股票代码
        
        Returns:
            标准化后的代码 (如: 600519.SH)
        """
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith('0') or code.startswith('3'):
            return f"{code}.SZ"
        elif code.startswith('8') or code.startswith('4'):
            return f"{code}.BJ"
        else:
            return code
    
    def get_index_data(
        self,
        index_code: str = '000001.SH',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取指数数据
        
        Args:
            index_code: 指数代码 (000001.SH: 上证指数, 399001.SZ: 深证成指)
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            指数数据DataFrame
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        if self.pro:
            df = self.pro.index_daily(
                ts_code=index_code,
                start_date=start_date,
                end_date=end_date
            )
        else:
            # 使用AkShare获取指数数据
            symbol = index_code.split('.')[0]
            df = ak.stock_zh_index_daily(symbol=f"sh{symbol}")
        
        return df


if __name__ == '__main__':
    # 测试代码
    fetcher = StockDataFetcher()
    
    # 获取股票列表
    print("获取股票列表...")
    stock_list = fetcher.get_stock_list()
    print(f"共有 {len(stock_list)} 只股票")
    print(stock_list.head())
    
    # 获取贵州茅台日线数据
    print("\n获取贵州茅台日线数据...")
    df = fetcher.get_daily_data('600519')
    print(df.head())
