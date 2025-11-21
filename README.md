# 基于机构探测的股票爆发预测系统

## 项目简介

这是一个基于AI和机构行为分析的股票爆发预测系统，通过分析机构资金流向、持仓变化、交易行为等多维度数据，预测股票是否会出现爆发性上涨。

**当前状态**: ✅ 基础功能开发完成，数据获取和特征工程模块已验证可用

## 核心功能

### 🔍 机构探测
- **机构持仓监控**：追踪基金、QFII、社保等机构持仓变化
- **龙虎榜分析**：分析机构席位买卖行为
- **主力资金流向**：实时监控超大单、大单资金动向
- **北向资金追踪**：陆股通资金流入流出分析

### 🤖 AI预测模型 (开发中)
- **LSTM时序模型**：捕捉股价时间序列规律
- **XGBoost分类模型**：基于特征的爆发分类
- **Transformer注意力模型**：长期依赖关系学习
- **集成模型**：多模型融合提高准确率

### 📊 数据分析 (已完成 ✅)
- **技术指标**：MA、MACD、RSI、KDJ、BOLL等 15+ 指标
- **机构行为特征**：持仓变化率、资金流向强度等 10+ 特征
- **市场情绪**：换手率、振幅、涨跌幅排名等 20+ 特征

### 📈 可视化展示 (开发中)
- K线图 + 资金流向叠加
- 机构持仓变化趋势
- 预测概率热力图
- 回测收益曲线

## 项目结构

```
stock/
├── data/                    # 数据目录
│   ├── raw/                # 原始数据
│   ├── processed/          # 处理后的数据
│   └── models/             # 训练好的模型
├── src/                    # 源代码
│   ├── data_acquisition/   # ✅ 数据获取模块
│   │   ├── stock_data.py      # 股票行情数据
│   │   ├── institution.py     # 机构数据
│   │   └── fund_flow.py       # 资金流向
│   ├── preprocessing/      # 数据预处理
│   ├── features/           # ✅ 特征工程
│   │   ├── technical.py       # 技术指标
│   │   ├── institutional.py   # 机构特征
│   │   └── sentiment.py       # 市场情绪
│   ├── models/             # ⏳ AI模型
│   ├── training/           # ⏳ 模型训练
│   ├── prediction/         # ⏳ 预测服务
│   ├── visualization/      # ⏳ 可视化
│   └── api/                # ⏳ API接口
├── web/                    # Web前端
├── notebooks/              # Jupyter notebooks
├── tests/                  # 测试文件
├── configs/                # ✅ 配置文件
│   └── config.yaml
├── docs/                   # ✅ 文档
│   └── PROJECT_SUMMARY.md
└── scripts/                # ✅ 脚本工具
    ├── quick_start.py
    └── test_system.py
```

## 技术栈

**后端**
- Python 3.12
- FastAPI / Flask
- pandas, numpy
- scikit-learn
- TensorFlow / PyTorch
- XGBoost
- TA-Lib

**前端**
- HTML5, CSS3, JavaScript
- ECharts (图表可视化)
- Bootstrap

**数据源**
- ✅ **AkShare** (免费，已验证可用)
- Tushare Pro (需要token)
- 东方财富网

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据源（可选）
编辑 `configs/config.yaml`，如果有Tushare Pro token可以填入：
```yaml
data_sources:
  tushare:
    token: "your_tushare_token_here"  # 可选，不填也能用AkShare
```

### 3. 运行快速演示
```bash
python scripts/quick_start.py
```

**实际运行效果**：
```
============================================================
  股票预测系统 - 快速演示
============================================================

📊 正在获取贵州茅台(600519)数据...
✓ 成功获取 244 条数据

最新行情:
  日期: 20251120
  收盘价: 1466.83 元
  涨跌幅: -0.28%
  成交量: 8423 手
  成交额: 12.38 亿元

📈 正在计算技术指标...
✓ 技术指标计算完成
  MA5: 1468.29
  MA20: 1448.74
  RSI: 64.99
  MACD: 4.9167

============================================================
  ✓ 演示完成！
============================================================
```

### 4. 股票预测 (新功能 ✨)
您可以直接输入股票代码，获取综合分析报告：

```bash
# 单次预测
python scripts/predict_stock.py 600519

# 交互模式
python scripts/predict_stock.py
```

**输出示例**：
```
🔍 正在分析股票: 600519 ...
==================================================
1. 获取行情数据...
   最新日期: 20251120
   最新收盘: 1470.01
   今日涨跌: -0.07%

2. 技术面分析...
   趋势判断: 上涨 📈
   MACD信号: 金叉/强势 (5.1703)
   RSI指标: 66.72 (正常)

==================================================
📊 综合预测结果
==================================================
综合评分: 5/10
预测结论: 📈 具备上涨潜力
```

### 5. 运行完整测试
```bash
python scripts/test_system.py
```

## 使用示例

### 获取股票数据
```python
from src.data_acquisition.stock_data import StockDataFetcher

fetcher = StockDataFetcher()
df = fetcher.get_daily_data('600519')  # 贵州茅台

print(f"获取 {len(df)} 条数据")
print(df[['trade_date', 'close', 'vol']].head())
```

### 计算技术指标
```python
from src.features.technical import TechnicalIndicators

calculator = TechnicalIndicators()
df_with_indicators = calculator.calculate_all_indicators(df)

# 查看最新指标
latest = df_with_indicators.iloc[0]
print(f"MA5: {latest['ma_5']:.2f}")
print(f"MA20: {latest['ma_20']:.2f}")
print(f"RSI: {latest['rsi']:.2f}")
print(f"MACD: {latest['macd']:.4f}")
```

### 分析机构行为
```python
from src.features.institutional import InstitutionalFeatures

extractor = InstitutionalFeatures()
features = extractor.extract_all_features('600519.SH', days=30)

print(f"主力净流入: {features['main_net_inflow_total']/10000:.2f} 万元")
print(f"连续流入天数: {features['consecutive_inflow_days']} 天")
print(f"龙虎榜出现: {features['lhb_appear_count']} 次")
```

### 批量筛选股票
```python
from src.data_acquisition.fund_flow import FundFlowFetcher

flow_fetcher = FundFlowFetcher()
top_stocks = flow_fetcher.screen_strong_inflow_stocks(
    min_inflow=3000,  # 最小净流入3000万
    top_n=20
)

print("主力资金强势流入股票TOP20:")
print(top_stocks[['代码', '名称', '主力净流入']].head())
```

## 已实现功能 ✅

### 数据获取层
- ✅ 股票行情数据（日线、分钟线、实时）
- ✅ 机构持仓数据
- ✅ 龙虎榜数据
- ✅ 大宗交易数据
- ✅ 北向资金数据
- ✅ 融资融券数据
- ✅ 机构调研数据
- ✅ 资金流向数据

### 特征工程层
- ✅ 技术指标计算（15+ 指标）
- ✅ 机构行为特征（10+ 特征）
- ✅ 市场情绪特征（20+ 特征）

### 基础设施
- ✅ 配置文件系统
- ✅ 数据标准化
- ✅ 错误处理
- ✅ 测试脚本
- ✅ 文档

## 开发中功能 🚧

### AI模型层
- ⏳ LSTM时序预测模型
- ⏳ XGBoost分类模型
- ⏳ Transformer注意力模型
- ⏳ 集成模型

### 预测服务
- ⏳ 预测接口
- ⏳ 股票筛选器
- ⏳ 回测系统

### 可视化
- ⏳ K线图表
- ⏳ 资金流向图表
- ⏳ 预测结果展示

### Web界面
- ⏳ FastAPI后端
- ⏳ 前端界面
- ⏳ 实时数据更新

## 爆发定义

系统将以下情况定义为"爆发"：
- 未来5日涨幅 > 15%
- 未来10日涨幅 > 25%
- 伴随成交量放大（> 5日均量2倍）

## 测试结果

### 数据获取测试
- ✅ 股票列表获取：正常
- ✅ 日线数据获取：正常（244条）
- ✅ 技术指标计算：正常
- ✅ 列名标准化：正常
- ⚠️ 资金流向：部分网络限制（不影响核心功能）

### 功能验证
- ✅ MA、EMA计算正确
- ✅ MACD、RSI、KDJ计算正确
- ✅ 布林带计算正确
- ✅ 数据排序处理正确
- ✅ 特征提取功能完善

## 已修复问题 🔧

1. ✅ **AkShare数据获取问题**
   - 添加 `period='daily'` 参数
   - 修复日期格式处理
   - 添加列名标准化（中文→英文）

2. ✅ **技术指标计算问题**
   - 修复数据排序逻辑（升序计算→降序输出）
   - 添加必需列检查
   - 改进错误处理

3. ✅ **数据标准化**
   - 统一列名（trade_date, close, high, low, vol）
   - 数值类型转换
   - 日期格式标准化

## 风险提示

⚠️ **重要声明**
- 本系统仅供学习和研究使用
- 不构成任何投资建议
- 股市有风险，投资需谨慎
- 历史表现不代表未来收益

## 开发路线图

### ✅ Phase 1: 基础架构（已完成）
- [x] 项目结构设计
- [x] 配置文件系统
- [x] 数据获取模块
- [x] 特征工程模块

### 🚧 Phase 2: AI模型（进行中）
- [ ] LSTM模型实现
- [ ] XGBoost模型实现
- [ ] Transformer模型实现
- [ ] 模型训练和评估

### ⏳ Phase 3: 预测服务
- [ ] 预测接口开发
- [ ] 股票筛选器
- [ ] 回测系统

### ⏳ Phase 4: 可视化和Web
- [ ] 图表组件
- [ ] Web后端API
- [ ] 前端界面

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或查看文档：
- 项目总结：`docs/PROJECT_SUMMARY.md`
- 故障排除：`docs/TROUBLESHOOTING.md`
- 配置说明：`configs/config.yaml`

---

**最后更新**: 2025-11-20  
**项目状态**: 基础功能开发完成 ✅  
**下一步**: AI模型开发
