"""
股票预测系统测试脚本
Test Script for Stock Prediction System

测试功能：
1. 数据获取
2. 技术指标计算
3. 机构特征提取
4. 市场情绪分析
5. 综合分析报告
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from src.data_acquisition.stock_data import StockDataFetcher
from src.data_acquisition.institution import InstitutionalDataFetcher
from src.data_acquisition.fund_flow import FundFlowFetcher
from src.features.technical import TechnicalIndicators
from src.features.institutional import InstitutionalFeatures
from src.features.sentiment import MarketSentiment


def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_data_acquisition():
    """测试数据获取功能"""
    print_section("1. 测试数据获取模块")
    
    fetcher = StockDataFetcher()
    
    # 测试股票代码
    test_stocks = ['600519', '000001', '600036']
    
    for stock in test_stocks:
        print(f"\n📊 获取 {stock} 的数据...")
        try:
            # 获取日线数据
            df = fetcher.get_daily_data(stock)
            if not df.empty:
                print(f"✓ 成功获取 {len(df)} 条日线数据")
                print(f"  日期范围: {df['trade_date'].min()} - {df['trade_date'].max()}")
                print(f"  最新收盘价: {df.iloc[0]['close']:.2f}")
            else:
                print(f"✗ 未获取到数据")
        except Exception as e:
            print(f"✗ 获取失败: {str(e)}")
    
    return fetcher


def test_technical_indicators(fetcher):
    """测试技术指标计算"""
    print_section("2. 测试技术指标计算")
    
    stock_code = '600519'
    print(f"\n📈 计算 {stock_code} 的技术指标...")
    
    try:
        # 获取数据
        df = fetcher.get_daily_data(stock_code)
        
        # 计算技术指标
        calculator = TechnicalIndicators()
        df_with_indicators = calculator.calculate_all_indicators(df)
        
        print(f"✓ 技术指标计算完成")
        print(f"\n最新技术指标值:")
        latest = df_with_indicators.iloc[0]
        
        print(f"  MA5: {latest.get('ma_5', 0):.2f}")
        print(f"  MA20: {latest.get('ma_20', 0):.2f}")
        print(f"  MACD: {latest.get('macd', 0):.4f}")
        print(f"  RSI: {latest.get('rsi', 0):.2f}")
        print(f"  KDJ_K: {latest.get('kdj_k', 0):.2f}")
        print(f"  布林上轨: {latest.get('boll_upper', 0):.2f}")
        print(f"  布林下轨: {latest.get('boll_lower', 0):.2f}")
        
        return df_with_indicators
        
    except Exception as e:
        print(f"✗ 计算失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_institutional_features():
    """测试机构特征提取"""
    print_section("3. 测试机构特征提取")
    
    stock_code = '600519.SH'
    print(f"\n🏢 分析 {stock_code} 的机构行为...")
    
    try:
        extractor = InstitutionalFeatures()
        features = extractor.extract_all_features(stock_code, days=30)
        
        print(f"✓ 机构特征提取完成")
        print(f"\n机构行为特征:")
        
        # 资金流向
        print(f"\n  【资金流向】")
        print(f"  主力净流入总额: {features.get('main_net_inflow_total', 0)/10000:.2f} 万元")
        print(f"  连续流入天数: {features.get('consecutive_inflow_days', 0)} 天")
        print(f"  超大单净额: {features.get('super_large_net', 0)/10000:.2f} 万元")
        
        # 机构行为
        print(f"\n  【机构行为】")
        print(f"  龙虎榜出现次数: {features.get('lhb_appear_count', 0)} 次")
        print(f"  龙虎榜机构净买: {features.get('lhb_inst_net', 0)/10000:.2f} 万元")
        print(f"  北向资金变化: {features.get('northbound_change_pct', 0):.2f}%")
        print(f"  机构调研次数: {features.get('research_count', 0)} 次")
        
        return features
        
    except Exception as e:
        print(f"✗ 提取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_fund_flow_analysis():
    """测试资金流向分析"""
    print_section("4. 测试资金流向分析")
    
    print(f"\n💰 获取主力资金流向排名...")
    
    try:
        flow_fetcher = FundFlowFetcher()
        
        # 获取主力资金排名
        rank = flow_fetcher.get_main_flow_rank(indicator="今日", top_n=10)
        
        if not rank.empty:
            print(f"✓ 成功获取主力资金排名")
            print(f"\n今日主力资金流向TOP10:")
            print(rank[['代码', '名称', '主力净流入', '主力净占比']].head(10).to_string(index=False))
        else:
            print(f"✗ 未获取到数据")
            
        return rank
        
    except Exception as e:
        print(f"✗ 获取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_market_sentiment(df):
    """测试市场情绪分析"""
    print_section("5. 测试市场情绪分析")
    
    if df is None:
        print("✗ 无数据可分析")
        return None
    
    print(f"\n📊 计算市场情绪指标...")
    
    try:
        sentiment = MarketSentiment()
        df_with_sentiment = sentiment.calculate_all_sentiment_features(df)
        
        print(f"✓ 市场情绪指标计算完成")
        print(f"\n最新情绪指标:")
        latest = df_with_sentiment.iloc[0]
        
        print(f"  量比: {latest.get('volume_ratio', 0):.2f}")
        print(f"  振幅: {latest.get('amplitude', 0):.2f}%")
        print(f"  5日动量: {latest.get('momentum_5', 0):.2f}%")
        print(f"  20日波动率: {latest.get('volatility_20', 0):.2f}%")
        print(f"  价格位置(20日): {latest.get('price_position_20', 0):.2f}%")
        
        return df_with_sentiment
        
    except Exception as e:
        print(f"✗ 计算失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_analysis_report(stock_code, technical_df, inst_features):
    """生成综合分析报告"""
    print_section("6. 综合分析报告")
    
    print(f"\n📋 {stock_code} 综合分析报告")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if technical_df is not None and not technical_df.empty:
        latest = technical_df.iloc[0]
        
        print(f"\n【技术面分析】")
        
        # 趋势判断
        ma5 = latest.get('ma_5', 0)
        ma20 = latest.get('ma_20', 0)
        close = latest.get('close', 0)
        
        if close > ma5 > ma20:
            trend = "强势上涨趋势 📈"
        elif close > ma20:
            trend = "上涨趋势 ↗️"
        elif close < ma5 < ma20:
            trend = "下跌趋势 ↘️"
        else:
            trend = "震荡整理 ↔️"
        
        print(f"  趋势: {trend}")
        
        # RSI判断
        rsi = latest.get('rsi', 50)
        if rsi > 70:
            rsi_status = "超买 ⚠️"
        elif rsi < 30:
            rsi_status = "超卖 💡"
        else:
            rsi_status = "正常"
        print(f"  RSI状态: {rsi_status} (RSI={rsi:.2f})")
        
        # MACD判断
        macd = latest.get('macd', 0)
        macd_signal = latest.get('macd_signal', 0)
        if macd > macd_signal and macd > 0:
            macd_status = "金叉向上 ✓"
        elif macd < macd_signal and macd < 0:
            macd_status = "死叉向下 ✗"
        else:
            macd_status = "中性"
        print(f"  MACD状态: {macd_status}")
    
    if inst_features:
        print(f"\n【资金面分析】")
        
        # 主力资金判断
        main_inflow = inst_features.get('main_net_inflow_total', 0)
        consecutive_days = inst_features.get('consecutive_inflow_days', 0)
        
        if main_inflow > 10000000:  # 1000万
            fund_status = "主力大幅流入 💰"
        elif main_inflow > 0:
            fund_status = "主力流入 ↗️"
        elif main_inflow < -10000000:
            fund_status = "主力大幅流出 ⚠️"
        else:
            fund_status = "资金平衡 ↔️"
        
        print(f"  资金状态: {fund_status}")
        print(f"  连续流入: {consecutive_days} 天")
        
        # 机构行为判断
        lhb_count = inst_features.get('lhb_appear_count', 0)
        research_count = inst_features.get('research_count', 0)
        
        if lhb_count > 0 or research_count > 5:
            inst_status = "机构关注度高 👀"
        else:
            inst_status = "机构关注度一般"
        
        print(f"  机构关注: {inst_status}")
        
        # 综合评分
        score = 0
        signals = []
        
        if close > ma5 > ma20:
            score += 2
            signals.append("均线多头排列")
        
        if 30 < rsi < 70:
            score += 1
        elif rsi < 30:
            score += 2
            signals.append("RSI超卖")
        
        if macd > macd_signal and macd > 0:
            score += 2
            signals.append("MACD金叉")
        
        if main_inflow > 5000000:
            score += 2
            signals.append("主力资金流入")
        
        if consecutive_days >= 3:
            score += 1
            signals.append(f"连续{consecutive_days}日资金流入")
        
        if lhb_count > 0:
            score += 1
            signals.append("登上龙虎榜")
        
        print(f"\n【综合评分】")
        print(f"  评分: {score}/10")
        
        if score >= 7:
            rating = "强烈看好 ⭐⭐⭐⭐⭐"
        elif score >= 5:
            rating = "看好 ⭐⭐⭐⭐"
        elif score >= 3:
            rating = "中性 ⭐⭐⭐"
        else:
            rating = "谨慎 ⭐⭐"
        
        print(f"  评级: {rating}")
        
        if signals:
            print(f"\n【关键信号】")
            for signal in signals:
                print(f"  • {signal}")
    
    print(f"\n⚠️  风险提示: 以上分析仅供参考，不构成投资建议！")


def main():
    """主测试函数"""
    print("\n" + "🚀 "*20)
    print("  股票爆发预测系统 - 功能测试")
    print("  Stock Outbreak Prediction System - Test")
    print("🚀 "*20)
    
    # 1. 测试数据获取
    fetcher = test_data_acquisition()
    
    # 2. 测试技术指标
    technical_df = test_technical_indicators(fetcher)
    
    # 3. 测试机构特征
    inst_features = test_institutional_features()
    
    # 4. 测试资金流向
    fund_flow_rank = test_fund_flow_analysis()
    
    # 5. 测试市场情绪
    sentiment_df = test_market_sentiment(technical_df)
    
    # 6. 生成综合分析报告
    generate_analysis_report('600519', technical_df, inst_features)
    
    print("\n" + "="*60)
    print("  ✓ 测试完成！")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
