"""
机构数据获取模块
Institutional Data Fetcher

功能：
- 机构持仓数据
- 龙虎榜数据
- 大宗交易数据
- 北向资金数据
- 融资融券数据
- 机构调研数据
"""

import pandas as pd
import tushare as ts
import akshare as ak
from datetime import datetime, timedelta
from typing import Optional, List
import yaml


class InstitutionalDataFetcher:
    """机构数据获取器"""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """初始化机构数据获取器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化Tushare
        tushare_token = self.config['data_sources']['tushare']['token']
        if tushare_token and tushare_token != 'your_tushare_token_here':
            ts.set_token(tushare_token)
            self.pro = ts.pro_api()
        else:
            self.pro = None
    
    def get_institutional_holdings(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取机构持仓数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            机构持仓DataFrame
        """
        if not self.pro:
            # 使用AkShare获取
            df = ak.stock_institute_hold_detail(symbol=stock_code.split('.')[0])
            return df
        
        # 使用Tushare获取基金持仓
        df = self.pro.fund_portfolio(ts_code=stock_code)
        return df
    
    def get_top_list(
        self,
        trade_date: Optional[str] = None,
        stock_code: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取龙虎榜数据
        
        Args:
            trade_date: 交易日期 (YYYYMMDD)
            stock_code: 股票代码（可选）
        
        Returns:
            龙虎榜DataFrame
        """
        if not trade_date:
            trade_date = datetime.now().strftime('%Y%m%d')
        
        if self.pro:
            # 使用Tushare获取
            if stock_code:
                df = self.pro.top_list(ts_code=stock_code, trade_date=trade_date)
            else:
                df = self.pro.top_list(trade_date=trade_date)
        else:
            # 使用AkShare获取
            df = ak.stock_lhb_detail_em(date=trade_date)
        
        return df
    
    def get_top_inst(
        self,
        trade_date: Optional[str] = None,
        stock_code: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取龙虎榜机构席位数据
        
        Args:
            trade_date: 交易日期
            stock_code: 股票代码
        
        Returns:
            机构席位DataFrame
        """
        if not trade_date:
            trade_date = datetime.now().strftime('%Y%m%d')
        
        if self.pro:
            df = self.pro.top_inst(trade_date=trade_date, ts_code=stock_code)
        else:
            # 使用AkShare获取机构龙虎榜
            df = ak.stock_lhb_jgmmtj_em()
            if stock_code:
                symbol = stock_code.split('.')[0]
                df = df[df['代码'] == symbol]
        
        return df
    
    def get_block_trade(
        self,
        stock_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取大宗交易数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            大宗交易DataFrame
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        if self.pro:
            df = self.pro.block_trade(
                ts_code=stock_code,
                start_date=start_date,
                end_date=end_date
            )
        else:
            # 使用AkShare获取
            df = ak.stock_dzjy_mrmx(symbol=stock_code.split('.')[0])
        
        return df
    
    def get_northbound_holdings(
        self,
        stock_code: Optional[str] = None,
        trade_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取北向资金持股数据（陆股通）
        
        Args:
            stock_code: 股票代码
            trade_date: 交易日期
        
        Returns:
            北向资金持股DataFrame
        """
        if not trade_date:
            trade_date = datetime.now().strftime('%Y%m%d')
        
        if self.pro:
            # 获取沪股通持股
            df_sh = self.pro.hk_hold(
                ts_code=stock_code,
                trade_date=trade_date,
                exchange='SH'
            )
            # 获取深股通持股
            df_sz = self.pro.hk_hold(
                ts_code=stock_code,
                trade_date=trade_date,
                exchange='SZ'
            )
            df = pd.concat([df_sh, df_sz], ignore_index=True)
        else:
            # 使用AkShare获取
            df = ak.stock_em_hsgt_hold_stock(symbol="北向")
            if stock_code:
                symbol = stock_code.split('.')[0]
                df = df[df['代码'] == symbol]
        
        return df
    
    def get_northbound_flow(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取北向资金流向数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            北向资金流向DataFrame
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        if self.pro:
            df = self.pro.moneyflow_hsgt(
                start_date=start_date,
                end_date=end_date
            )
        else:
            # 使用AkShare获取
            df = ak.stock_em_hsgt_hist()
        
        return df
    
    def get_margin_detail(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取融资融券明细数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            融资融券DataFrame
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        
        if self.pro:
            df = self.pro.margin_detail(
                ts_code=stock_code,
                start_date=start_date,
                end_date=end_date
            )
        else:
            # 使用AkShare获取
            symbol = stock_code.split('.')[0]
            df = ak.stock_margin_detail_em(symbol=symbol)
        
        return df
    
    def get_institutional_research(
        self,
        stock_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取机构调研数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            机构调研DataFrame
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        
        # 使用AkShare获取机构调研数据
        df = ak.stock_jgdy_tj_em(symbol="全部")
        
        if stock_code:
            symbol = stock_code.split('.')[0]
            df = df[df['代码'] == symbol]
        
        return df
    
    def get_institutional_rating(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取机构评级数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            机构评级DataFrame
        """
        # 使用AkShare获取
        symbol = stock_code.split('.')[0]
        df = ak.stock_institute_recommend(symbol=symbol)
        
        return df
    
    def analyze_institutional_behavior(
        self,
        stock_code: str,
        days: int = 30
    ) -> dict:
        """
        综合分析机构行为
        
        Args:
            stock_code: 股票代码
            days: 分析天数
        
        Returns:
            机构行为分析结果字典
        """
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        result = {
            'stock_code': stock_code,
            'analysis_period': f"{start_date} - {end_date}",
            'institutional_signals': []
        }
        
        # 1. 龙虎榜机构席位分析
        try:
            lhb_data = self.get_top_inst(stock_code=stock_code)
            if not lhb_data.empty:
                inst_buy = lhb_data['buy'].sum() if 'buy' in lhb_data.columns else 0
                inst_sell = lhb_data['sell'].sum() if 'sell' in lhb_data.columns else 0
                result['lhb_inst_net_buy'] = inst_buy - inst_sell
                
                if inst_buy > inst_sell * 1.5:
                    result['institutional_signals'].append('龙虎榜机构大幅净买入')
        except:
            pass
        
        # 2. 北向资金分析
        try:
            nb_holdings = self.get_northbound_holdings(stock_code=stock_code)
            if not nb_holdings.empty and len(nb_holdings) > 1:
                latest_hold = nb_holdings.iloc[0]['hold_amount'] if 'hold_amount' in nb_holdings.columns else 0
                prev_hold = nb_holdings.iloc[-1]['hold_amount'] if 'hold_amount' in nb_holdings.columns else 0
                change_pct = (latest_hold - prev_hold) / prev_hold * 100 if prev_hold > 0 else 0
                result['northbound_change_pct'] = change_pct
                
                threshold = self.config['institutional_detection']['northbound_change_threshold']
                if change_pct > threshold:
                    result['institutional_signals'].append(f'北向资金增持 {change_pct:.2f}%')
        except:
            pass
        
        # 3. 融资融券分析
        try:
            margin_data = self.get_margin_detail(stock_code, start_date, end_date)
            if not margin_data.empty:
                avg_margin_balance = margin_data['rzye'].mean() if 'rzye' in margin_data.columns else 0
                result['avg_margin_balance'] = avg_margin_balance
        except:
            pass
        
        # 4. 机构调研频次
        try:
            research_data = self.get_institutional_research(stock_code, start_date, end_date)
            if not research_data.empty:
                research_count = len(research_data)
                result['research_count'] = research_count
                
                if research_count > 5:
                    result['institutional_signals'].append(f'近{days}日机构调研{research_count}次')
        except:
            pass
        
        # 综合评分
        signal_count = len(result['institutional_signals'])
        if signal_count >= 3:
            result['institutional_activity'] = '高'
        elif signal_count >= 1:
            result['institutional_activity'] = '中'
        else:
            result['institutional_activity'] = '低'
        
        return result


if __name__ == '__main__':
    # 测试代码
    fetcher = InstitutionalDataFetcher()
    
    # 测试龙虎榜数据
    print("获取龙虎榜数据...")
    lhb = fetcher.get_top_list()
    print(lhb.head())
    
    # 测试北向资金
    print("\n获取北向资金流向...")
    nb_flow = fetcher.get_northbound_flow()
    print(nb_flow.head())
    
    # 综合分析
    print("\n分析贵州茅台机构行为...")
    analysis = fetcher.analyze_institutional_behavior('600519.SH')
    print(analysis)
