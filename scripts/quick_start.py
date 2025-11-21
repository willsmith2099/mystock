"""
快速开始脚本
Quick Start Script

快速演示系统核心功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_acquisition.stock_data import StockDataFetcher
from src.data_acquisition.fund_flow import FundFlowFetcher
from src.features.technical import TechnicalIndicators
import warnings
warnings.filterwarnings('ignore')


def main():
    print("="*60)
    print("  股票预测系统 - 快速演示")
    print("="*60)
    
    # 1. 获取股票数据
    print("\n📊 正在获取贵州茅台(600519)数据...")
    fetcher = StockDataFetcher()
    df = fetcher.get_daily_data('600519')
    
    if not df.empty:
        print(f"✓ 成功获取 {len(df)} 条数据")
        print(f"\n最新行情:")
        latest = df.iloc[0]
        print(f"  日期: {latest.get('trade_date', 'N/A')}")
        print(f"  收盘价: {latest.get('close', 0):.2f} 元")
        print(f"  涨跌幅: {latest.get('pct_chg', 0):.2f}%")
        print(f"  成交量: {latest.get('vol', 0):.0f} 手")
        print(f"  成交额: {latest.get('amount', 0)/100000000:.2f} 亿元")
    else:
        print("✗ 未获取到数据，请检查网络连接或数据源")
        return
    
    # 2. 计算技术指标
    print("\n📈 正在计算技术指标...")
    calculator = TechnicalIndicators()
    df_tech = calculator.calculate_all_indicators(df)
    
    latest = df_tech.iloc[0]
    print(f"✓ 技术指标计算完成")
    print(f"  MA5: {latest.get('ma_5', 0):.2f}")
    print(f"  MA20: {latest.get('ma_20', 0):.2f}")
    print(f"  RSI: {latest.get('rsi', 0):.2f}")
    print(f"  MACD: {latest.get('macd', 0):.4f}")
    
    # 3. 获取主力资金排名
    print("\n💰 正在获取主力资金流向...")
    try:
        flow_fetcher = FundFlowFetcher()
        rank = flow_fetcher.get_main_flow_rank(top_n=5)
        
        if not rank.empty:
            print(f"✓ 今日主力资金流向TOP5:")
            for idx, row in rank.head(5).iterrows():
                print(f"  {row.get('名称', 'N/A')}: {row.get('主力净流入', 0):.2f}万")
    except Exception as e:
        print(f"⚠️  资金流向数据获取失败: {str(e)}")
    
    print("\n" + "="*60)
    print("  ✓ 演示完成！")
    print("  运行 python scripts/test_system.py 查看完整测试")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
