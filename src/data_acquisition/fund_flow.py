"""
资金流向数据获取模块
Fund Flow Data Fetcher

功能：
- 主力资金流向
- 超大单、大单、中单、小单分析
- 行业资金流向
- 概念板块资金流向
- 个股资金流向详情
"""

import pandas as pd
import tushare as ts
import akshare as ak
from datetime import datetime, timedelta
from typing import Optional, List
import yaml


class FundFlowFetcher:
    """资金流向数据获取器"""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """初始化资金流向获取器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化Tushare
        tushare_token = self.config['data_sources']['tushare']['token']
        if tushare_token and tushare_token != 'your_tushare_token_here':
            ts.set_token(tushare_token)
            self.pro = ts.pro_api()
        else:
            self.pro = None
    
    def get_individual_flow(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取个股资金流向
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            资金流向DataFrame
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        try:
            if self.pro:
                # 使用Tushare获取
                df = self.pro.moneyflow(
                    ts_code=stock_code,
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                # 使用AkShare获取
                symbol = stock_code.split('.')[0]
                
                # 自动判断市场
                market = "sh"
                if symbol.startswith(('0', '3')):
                    market = "sz"
                elif symbol.startswith(('4', '8')):
                    market = "bj"
                
                try:
                    df = ak.stock_individual_fund_flow(stock=symbol, market=market)
                except:
                    # 如果指定市场失败，尝试不传market参数或使用另一种方式
                    df = ak.stock_individual_fund_flow(stock=symbol, market="sh" if market=="sz" else "sz")
            return df
        except Exception as e:
            print(f"获取个股资金流向失败: {str(e)}")
            return pd.DataFrame()
    
    def get_realtime_flow(self, stock_codes: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取实时资金流向
        
        Args:
            stock_codes: 股票代码列表（可选）
        
        Returns:
            实时资金流向DataFrame
        """
        try:
            # 使用AkShare获取实时资金流向
            df = ak.stock_individual_fund_flow_rank(indicator="今日")
            
            if stock_codes:
                symbols = [code.split('.')[0] for code in stock_codes]
                df = df[df['代码'].isin(symbols)]
            return df
        except Exception as e:
            print(f"获取实时资金流向失败: {str(e)}")
            return pd.DataFrame()
    
    def get_main_flow_rank(
        self,
        indicator: str = "今日",
        top_n: int = 100
    ) -> pd.DataFrame:
        """
        获取主力资金流向排名
        
        Args:
            indicator: 时间指标 (今日, 3日, 5日, 10日)
            top_n: 返回前N名
        
        Returns:
            主力资金排名DataFrame
        """
        try:
            # 使用AkShare获取
            df = ak.stock_individual_fund_flow_rank(indicator=indicator)
            return df.head(top_n)
        except Exception as e:
            print(f"获取主力资金排名失败: {str(e)}")
            # 返回空DataFrame而不是抛出异常
            return pd.DataFrame()
    
    def get_sector_flow(
        self,
        sector_type: str = "industry"
    ) -> pd.DataFrame:
        """
        获取板块资金流向
        
        Args:
            sector_type: 板块类型 (industry: 行业, concept: 概念)
        
        Returns:
            板块资金流向DataFrame
        """
        try:
            if sector_type == "industry":
                # 行业资金流向
                df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
            elif sector_type == "concept":
                # 概念资金流向
                df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="概念资金流")
            else:
                raise ValueError(f"不支持的板块类型: {sector_type}")
            
            return df
        except Exception as e:
            print(f"获取板块资金流向失败: {str(e)}")
            return pd.DataFrame()
    
    def get_market_flow(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取市场整体资金流向
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            市场资金流向DataFrame
        """
        try:
            # 使用AkShare获取大盘资金流向
            df = ak.stock_market_fund_flow()
            return df
        except Exception as e:
            print(f"获取市场资金流向失败: {str(e)}")
            return pd.DataFrame()
    
    def analyze_fund_flow(
        self,
        stock_code: str,
        days: int = 5
    ) -> dict:
        """
        分析个股资金流向特征
        
        Args:
            stock_code: 股票代码
            days: 分析天数
        
        Returns:
            资金流向分析结果
        """
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        # 获取资金流向数据
        df = self.get_individual_flow(stock_code, start_date, end_date)
        
        if df.empty:
            return {
                'stock_code': stock_code,
                'status': '无数据',
                'signals': []
            }
        
        result = {
            'stock_code': stock_code,
            'analysis_period': f"近{days}日",
            'signals': []
        }
        
        # 计算主力资金净流入
        if 'net_mf_amount' in df.columns:
            total_net_inflow = df['net_mf_amount'].sum()
            result['total_main_net_inflow'] = total_net_inflow
            
            # 连续净流入天数
            consecutive_inflow = 0
            for value in df['net_mf_amount']:
                if value > 0:
                    consecutive_inflow += 1
                else:
                    break
            result['consecutive_inflow_days'] = consecutive_inflow
            
            # 判断信号
            threshold = self.config['institutional_detection']['fund_flow_threshold'] * 10000
            if total_net_inflow > threshold:
                result['signals'].append(f'主力资金大幅净流入 {total_net_inflow/10000:.2f}万元')
            
            if consecutive_inflow >= 3:
                result['signals'].append(f'主力资金连续{consecutive_inflow}日净流入')
        
        # 分析超大单和大单
        if 'buy_elg_amount' in df.columns and 'buy_lg_amount' in df.columns:
            super_large_buy = df['buy_elg_amount'].sum()
            large_buy = df['buy_lg_amount'].sum()
            result['super_large_buy'] = super_large_buy
            result['large_buy'] = large_buy
            
            if super_large_buy > 0:
                result['signals'].append('超大单持续买入')
        
        # 资金流向强度评分
        signal_count = len(result['signals'])
        if signal_count >= 2:
            result['flow_strength'] = '强'
        elif signal_count >= 1:
            result['flow_strength'] = '中'
        else:
            result['flow_strength'] = '弱'
        
        return result
    
    def get_dragon_tiger_flow(
        self,
        trade_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取龙虎榜资金流向
        
        Args:
            trade_date: 交易日期
        
        Returns:
            龙虎榜资金流向DataFrame
        """
        if not trade_date:
            trade_date = datetime.now().strftime('%Y%m%d')
        
        try:
            # 使用AkShare获取龙虎榜资金流向
            df = ak.stock_lhb_detail_em(date=trade_date)
            return df
        except Exception as e:
            print(f"获取龙虎榜资金流向失败: {str(e)}")
            return pd.DataFrame()
    
    def screen_strong_inflow_stocks(
        self,
        min_inflow: float = 5000,  # 最小净流入（万元）
        consecutive_days: int = 3,
        top_n: int = 50
    ) -> pd.DataFrame:
        """
        筛选主力资金强势流入股票
        
        Args:
            min_inflow: 最小净流入金额（万元）
            consecutive_days: 连续流入天数
            top_n: 返回前N只股票
        
        Returns:
            筛选结果DataFrame
        """
        # 获取今日主力资金排名
        df = self.get_main_flow_rank(indicator="今日", top_n=500)
        
        # 筛选条件
        if '主力净流入' in df.columns:
            df = df[df['主力净流入'] > min_inflow]
        
        # 按主力净流入排序
        if '主力净流入' in df.columns:
            df = df.sort_values('主力净流入', ascending=False)
        
        return df.head(top_n)
    
    def get_fund_flow_history(
        self,
        stock_code: str,
        days: int = 30
    ) -> pd.DataFrame:
        """
        获取资金流向历史趋势
        
        Args:
            stock_code: 股票代码
            days: 历史天数
        
        Returns:
            资金流向历史DataFrame
        """
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = self.get_individual_flow(stock_code, start_date, end_date)
        
        # 计算累计净流入
        if not df.empty and 'net_mf_amount' in df.columns:
            df['cumulative_inflow'] = df['net_mf_amount'].cumsum()
        
        return df


if __name__ == '__main__':
    # 测试代码
    fetcher = FundFlowFetcher()
    
    # 获取主力资金排名
    print("获取主力资金流向排名...")
    rank = fetcher.get_main_flow_rank(top_n=20)
    print(rank.head())
    
    # 分析个股资金流向
    print("\n分析贵州茅台资金流向...")
    analysis = fetcher.analyze_fund_flow('600519.SH', days=5)
    print(analysis)
    
    # 筛选强势流入股票
    print("\n筛选主力资金强势流入股票...")
    strong_stocks = fetcher.screen_strong_inflow_stocks(min_inflow=3000, top_n=10)
    print(strong_stocks)
