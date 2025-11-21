#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票爆发预测脚本
Stock Outbreak Prediction Script

功能：
- 接受用户输入的股票代码
- 获取实时数据和历史数据
- 计算技术指标和特征
- 生成综合分析报告
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_acquisition.stock_data import StockDataFetcher
from src.data_acquisition.fund_flow import FundFlowFetcher
from src.data_acquisition.institution import InstitutionalDataFetcher
from src.features.technical import TechnicalIndicators
from src.features.institutional import InstitutionalFeatures
from src.features.sentiment import MarketSentiment

def analyze_stock(stock_code: str):
    """
    分析单只股票
    """
    print(f"\n🔍 正在分析股票: {stock_code} ...")
    print("=" * 50)
    
    # 1. 获取数据
    print("1. 获取行情数据...")
    data_fetcher = StockDataFetcher()
    df = data_fetcher.get_daily_data(stock_code)
    
    if df.empty:
        print(f"❌ 无法获取股票 {stock_code} 的数据，请检查代码是否正确。")
        return
    
    latest = df.iloc[0]
    print(f"   最新日期: {latest['trade_date']}")
    print(f"   最新收盘: {latest['close']:.2f}")
    print(f"   今日涨跌: {latest['pct_chg']:.2f}%")
    
    # 2. 技术面分析
    print("\n2. 技术面分析...")
    tech_calc = TechnicalIndicators()
    df_tech = tech_calc.calculate_all_indicators(df)
    latest_tech = df_tech.iloc[0]
    
    # 简单的趋势判断
    ma5 = latest_tech.get('ma_5', 0)
    ma20 = latest_tech.get('ma_20', 0)
    macd = latest_tech.get('macd', 0)
    rsi = latest_tech.get('rsi', 50)
    
    trend = "震荡"
    if ma5 > ma20 and macd > 0:
        trend = "上涨 📈"
    elif ma5 < ma20 and macd < 0:
        trend = "下跌 📉"
        
    print(f"   趋势判断: {trend}")
    print(f"   MACD信号: {'金叉/强势' if macd > 0 else '死叉/弱势'} ({macd:.4f})")
    print(f"   RSI指标: {rsi:.2f} ({'超买' if rsi>80 else '超卖' if rsi<20 else '正常'})")
    
    # 3. 资金面分析
    print("\n3. 资金面分析...")
    inst_fetcher = InstitutionalFeatures()
    # 注意：这里可能会因为网络问题失败，做个简单的容错
    try:
        inst_features = inst_fetcher.extract_all_features(stock_code)
        net_inflow = inst_features.get('main_net_inflow_total', 0)
        print(f"   主力净流入(近5日): {net_inflow/10000:.2f} 万元")
        print(f"   连续流入天数: {inst_features.get('consecutive_inflow_days', 0)} 天")
    except Exception as e:
        print(f"   ⚠️ 资金数据获取受限: {str(e)}")
        
    # 4. 情绪面分析
    print("\n4. 情绪面分析...")
    sent_calc = MarketSentiment()
    df_sent = sent_calc.calculate_all_sentiment_features(df)
    latest_sent = df_sent.iloc[0]
    
    vol_ratio = latest_sent.get('volume_ratio', 0)
    amplitude = latest_sent.get('amplitude', 0)
    
    print(f"   量比: {vol_ratio:.2f} ({'放量' if vol_ratio > 1.5 else '缩量' if vol_ratio < 0.8 else '正常'})")
    print(f"   振幅: {amplitude:.2f}%")

    # 5. 综合评分
    print("\n" + "=" * 50)
    print("📊 综合预测结果")
    print("=" * 50)
    
    score = 0
    reasons = []
    
    # 技术面打分
    if ma5 > ma20: score += 2
    if macd > 0: score += 2
    if 30 < rsi < 70: score += 1
    
    # 情绪面打分
    if vol_ratio > 1.2: 
        score += 2
        reasons.append("成交量放大")
    
    # 资金面打分
    if 'net_inflow' in locals() and net_inflow > 0:
        score += 2
        reasons.append("主力资金净流入")
        
    print(f"综合评分: {score}/10")
    
    if score >= 7:
        print("预测结论: 🚀 极高爆发潜力")
    elif score >= 5:
        print("预测结论: 📈 具备上涨潜力")
    else:
        print("预测结论: 👀 建议观望")
        
    if reasons:
        print(f"关键驱动: {', '.join(reasons)}")
    
    print("\n⚠️ 免责声明: 结果仅供参考，不构成投资建议。")

def main():
    parser = argparse.ArgumentParser(description='股票爆发预测工具')
    parser.add_argument('code', nargs='*', help='股票代码 (例如: 600519)')
    args = parser.parse_args()
    
    # 处理传入的参数列表
    if args.code:
        # 过滤掉非数字的参数（比如注释或多余文字）
        valid_codes = [c for c in args.code if c.strip().isdigit() and len(c.strip()) == 6]
        
        if not valid_codes:
            # 尝试处理包含非数字字符的单个参数 (如 "600519.SH")
            raw_input = " ".join(args.code)
            import re
            # 提取6位数字
            match = re.search(r'\d{6}', raw_input)
            if match:
                valid_codes = [match.group(0)]
        
        if valid_codes:
            for code in valid_codes:
                analyze_stock(code)
        else:
            print(f"❌ 未识别到有效的股票代码。请输入6位数字代码。")
    else:
        # 交互模式
        while True:
            try:
                code = input("\n请输入股票代码 (输入 q 退出): ").strip()
                if code.lower() in ['q', 'quit', 'exit']:
                    break
                if not code:
                    continue
                
                # 提取代码
                import re
                match = re.search(r'\d{6}', code)
                if match:
                    analyze_stock(match.group(0))
                else:
                    print("❌ 请输入有效的6位股票代码")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
