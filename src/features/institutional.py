"""
机构行为特征提取模块
Institutional Behavior Features

提取机构相关特征：
- 机构持仓变化特征
- 资金流向特征
- 龙虎榜特征
- 北向资金特征
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import yaml
import sys
sys.path.append('.')

from src.data_acquisition.institution import InstitutionalDataFetcher
from src.data_acquisition.fund_flow import FundFlowFetcher


class InstitutionalFeatures:
    """机构行为特征提取器"""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """初始化机构特征提取器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.inst_fetcher = InstitutionalDataFetcher(config_path)
        self.flow_fetcher = FundFlowFetcher(config_path)
    
    def extract_fund_flow_features(
        self,
        stock_code: str,
        days: int = 30
    ) -> dict:
        """
        提取资金流向特征
        
        Args:
            stock_code: 股票代码
            days: 历史天数
        
        Returns:
            资金流向特征字典
        """
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        # 获取资金流向数据
        df = self.flow_fetcher.get_individual_flow(stock_code, start_date, end_date)
        
        features = {}
        
        if df.empty:
            return self._get_empty_flow_features()
        
        # 主力资金净流入特征
        if 'net_mf_amount' in df.columns:
            features['main_net_inflow_total'] = df['net_mf_amount'].sum()
            features['main_net_inflow_mean'] = df['net_mf_amount'].mean()
            features['main_net_inflow_std'] = df['net_mf_amount'].std()
            
            # 连续净流入天数
            consecutive_days = 0
            for value in df['net_mf_amount']:
                if value > 0:
                    consecutive_days += 1
                else:
                    break
            features['consecutive_inflow_days'] = consecutive_days
            
            # 净流入占比（正值天数/总天数）
            features['inflow_ratio'] = (df['net_mf_amount'] > 0).sum() / len(df)
        
        # 超大单特征
        if 'buy_elg_amount' in df.columns:
            features['super_large_buy_total'] = df['buy_elg_amount'].sum()
            features['super_large_sell_total'] = df['sell_elg_amount'].sum() if 'sell_elg_amount' in df.columns else 0
            features['super_large_net'] = features['super_large_buy_total'] - features['super_large_sell_total']
        
        # 大单特征
        if 'buy_lg_amount' in df.columns:
            features['large_buy_total'] = df['buy_lg_amount'].sum()
            features['large_sell_total'] = df['sell_lg_amount'].sum() if 'sell_lg_amount' in df.columns else 0
            features['large_net'] = features['large_buy_total'] - features['large_sell_total']
        
        return features
    
    def extract_institutional_features(
        self,
        stock_code: str,
        days: int = 30
    ) -> dict:
        """
        提取机构行为特征
        
        Args:
            stock_code: 股票代码
            days: 历史天数
        
        Returns:
            机构特征字典
        """
        features = {}
        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        # 1. 龙虎榜特征
        try:
            lhb_data = self.inst_fetcher.get_top_inst(stock_code=stock_code)
            if not lhb_data.empty:
                features['lhb_appear_count'] = len(lhb_data)
                features['lhb_inst_buy'] = lhb_data['buy'].sum() if 'buy' in lhb_data.columns else 0
                features['lhb_inst_sell'] = lhb_data['sell'].sum() if 'sell' in lhb_data.columns else 0
                features['lhb_inst_net'] = features['lhb_inst_buy'] - features['lhb_inst_sell']
            else:
                features['lhb_appear_count'] = 0
                features['lhb_inst_buy'] = 0
                features['lhb_inst_sell'] = 0
                features['lhb_inst_net'] = 0
        except:
            features['lhb_appear_count'] = 0
            features['lhb_inst_buy'] = 0
            features['lhb_inst_sell'] = 0
            features['lhb_inst_net'] = 0
        
        # 2. 北向资金特征
        try:
            nb_holdings = self.inst_fetcher.get_northbound_holdings(stock_code=stock_code)
            if not nb_holdings.empty:
                latest_hold = nb_holdings.iloc[0]['hold_amount'] if 'hold_amount' in nb_holdings.columns else 0
                features['northbound_holdings'] = latest_hold
                
                if len(nb_holdings) > 1:
                    prev_hold = nb_holdings.iloc[-1]['hold_amount'] if 'hold_amount' in nb_holdings.columns else 0
                    features['northbound_change'] = latest_hold - prev_hold
                    features['northbound_change_pct'] = (latest_hold - prev_hold) / prev_hold * 100 if prev_hold > 0 else 0
                else:
                    features['northbound_change'] = 0
                    features['northbound_change_pct'] = 0
            else:
                features['northbound_holdings'] = 0
                features['northbound_change'] = 0
                features['northbound_change_pct'] = 0
        except:
            features['northbound_holdings'] = 0
            features['northbound_change'] = 0
            features['northbound_change_pct'] = 0
        
        # 3. 融资融券特征
        try:
            margin_data = self.inst_fetcher.get_margin_detail(stock_code, start_date, end_date)
            if not margin_data.empty:
                features['margin_balance_mean'] = margin_data['rzye'].mean() if 'rzye' in margin_data.columns else 0
                features['margin_buy_mean'] = margin_data['rzmre'].mean() if 'rzmre' in margin_data.columns else 0
            else:
                features['margin_balance_mean'] = 0
                features['margin_buy_mean'] = 0
        except:
            features['margin_balance_mean'] = 0
            features['margin_buy_mean'] = 0
        
        # 4. 机构调研特征
        try:
            research_data = self.inst_fetcher.get_institutional_research(stock_code, start_date, end_date)
            features['research_count'] = len(research_data) if not research_data.empty else 0
        except:
            features['research_count'] = 0
        
        return features
    
    def extract_all_features(
        self,
        stock_code: str,
        days: int = 30
    ) -> dict:
        """
        提取所有机构相关特征
        
        Args:
            stock_code: 股票代码
            days: 历史天数
        
        Returns:
            所有特征字典
        """
        features = {}
        
        # 资金流向特征
        flow_features = self.extract_fund_flow_features(stock_code, days)
        features.update(flow_features)
        
        # 机构行为特征
        inst_features = self.extract_institutional_features(stock_code, days)
        features.update(inst_features)
        
        return features
    
    def _get_empty_flow_features(self) -> dict:
        """返回空的资金流向特征"""
        return {
            'main_net_inflow_total': 0,
            'main_net_inflow_mean': 0,
            'main_net_inflow_std': 0,
            'consecutive_inflow_days': 0,
            'inflow_ratio': 0,
            'super_large_buy_total': 0,
            'super_large_sell_total': 0,
            'super_large_net': 0,
            'large_buy_total': 0,
            'large_sell_total': 0,
            'large_net': 0
        }
    
    def get_feature_columns(self) -> list:
        """
        获取所有机构特征列名
        
        Returns:
            特征列名列表
        """
        return [
            # 资金流向特征
            'main_net_inflow_total',
            'main_net_inflow_mean',
            'main_net_inflow_std',
            'consecutive_inflow_days',
            'inflow_ratio',
            'super_large_buy_total',
            'super_large_sell_total',
            'super_large_net',
            'large_buy_total',
            'large_sell_total',
            'large_net',
            # 机构行为特征
            'lhb_appear_count',
            'lhb_inst_buy',
            'lhb_inst_sell',
            'lhb_inst_net',
            'northbound_holdings',
            'northbound_change',
            'northbound_change_pct',
            'margin_balance_mean',
            'margin_buy_mean',
            'research_count'
        ]


if __name__ == '__main__':
    # 测试代码
    extractor = InstitutionalFeatures()
    
    print("提取贵州茅台机构特征...")
    features = extractor.extract_all_features('600519.SH', days=30)
    
    print("\n机构特征:")
    for key, value in features.items():
        print(f"{key}: {value}")
