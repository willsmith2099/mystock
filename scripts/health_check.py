#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统健康检查脚本
System Health Check
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_module(module_name, import_statement):
    """检查模块是否可以导入"""
    try:
        exec(import_statement)
        print(f"✓ {module_name} 导入成功")
        return True
    except Exception as e:
        print(f"✗ {module_name} 导入失败: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("  股票预测系统 - 健康检查")
    print("=" * 60)
    
    results = {}
    
    # 基础库检查
    print("\n【基础库检查】")
    results['pandas'] = check_module("pandas", "import pandas")
    results['numpy'] = check_module("numpy", "import numpy")
    results['yaml'] = check_module("yaml", "import yaml")
    
    # 数据获取库
    print("\n【数据获取库】")
    results['akshare'] = check_module("akshare", "import akshare")
    results['tushare'] = check_module("tushare", "import tushare")
    
    # 机器学习库
    print("\n【机器学习库】")
    results['sklearn'] = check_module("scikit-learn", "import sklearn")
    results['xgboost'] = check_module("xgboost", "import xgboost")
    
    # 深度学习库（可选）
    print("\n【深度学习库（可选）】")
    results['tensorflow'] = check_module("tensorflow", "import tensorflow")
    
    # 自定义模块
    print("\n【自定义模块】")
    results['data_acquisition'] = check_module(
        "数据获取模块", 
        "from src.data_acquisition.stock_data import StockDataFetcher"
    )
    results['features'] = check_module(
        "特征工程模块",
        "from src.features.technical import TechnicalIndicators"
    )
    results['preprocessing'] = check_module(
        "数据预处理模块",
        "from src.preprocessing.processor import DataProcessor"
    )
    
    # 统计结果
    print("\n" + "=" * 60)
    print("  检查结果统计")
    print("=" * 60)
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"总计: {total} 项")
    print(f"通过: {passed} 项 ✓")
    print(f"失败: {failed} 项 ✗")
    
    if failed == 0:
        print("\n🎉 所有检查通过！系统运行正常。")
    elif failed <= 2:
        print("\n⚠️  部分可选组件未安装，核心功能正常。")
    else:
        print("\n❌ 多个组件缺失，请检查环境配置。")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
