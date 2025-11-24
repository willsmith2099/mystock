# 基于机构探测的股票爆发预测系统 / Stock Breakout Prediction System Based on Institutional Detection

[中文](#中文) | [English](#english)

---

## 中文

### 项目简介

这是一个基于AI和机构行为分析的股票爆发预测系统，通过分析机构资金流向、持仓变化、交易行为等多维度数据，预测股票是否会出现爆发性上涨。

**当前状态**: ✅ 基础功能开发完成，数据获取和特征工程模块已验证可用

### 核心功能

#### 🔍 机构探测
- **机构持仓监控**：追踪基金、QFII、社保等机构持仓变化
- **龙虎榜分析**：分析机构席位买卖行为
- **主力资金流向**：实时监控超大单、大单资金动向
- **北向资金追踪**：陆股通资金流入流出分析

#### 🤖 AI预测模型 (开发中)
- **LSTM时序模型**：捕捉股价时间序列规律
- **XGBoost分类模型**：基于特征的爆发分类
- **Transformer注意力模型**：长期依赖关系学习
- **集成模型**：多模型融合提高准确率

#### 📊 数据分析 (已完成 ✅)
- **技术指标**：MA、MACD、RSI、KDJ、BOLL等 15+ 指标
- **机构行为特征**：持仓变化率、资金流向强度等 10+ 特征
- **市场情绪**：换手率、振幅、涨跌幅排名等 20+ 特征

#### 📈 可视化展示 (开发中)
- K线图 + 资金流向叠加
- 机构持仓变化趋势
- 预测概率热力图
- 回测收益曲线

### 项目结构

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
├── configs/                # ✅ 配置文件
├── docs/                   # ✅ 文档
└── scripts/                # ✅ 脚本工具
```

### 技术栈

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

### 快速开始

#### 方式1：使用 Docker（推荐）

```bash
# 进入docker目录
cd docker

# 启动服务
docker-compose up -d

# 运行演示
docker-compose exec stock python scripts/quick_start.py

# 股票预测
docker-compose exec stock python scripts/predict_stock.py 600519
```

📖 详细文档：[Docker使用指南](docs/DOCKER.md)

#### 方式2：本地安装

**1. 安装依赖**
```bash
pip install -r requirements.txt
```

**2. 配置数据源（可选）**
编辑 `configs/config.yaml`：
```yaml
data_sources:
  tushare:
    token: "your_tushare_token_here"  # 可选
```

**3. 运行快速演示**
```bash
python scripts/quick_start.py
```

**4. 股票预测**
```bash
# 单次预测
python scripts/predict_stock.py 600519

# 交互模式
python scripts/predict_stock.py
```

### 使用示例

#### 获取股票数据
```python
from src.data_acquisition.stock_data import StockDataFetcher

fetcher = StockDataFetcher()
df = fetcher.get_daily_data('600519')  # 贵州茅台
```

#### 计算技术指标
```python
from src.features.technical import TechnicalIndicators

calculator = TechnicalIndicators()
df_with_indicators = calculator.calculate_all_indicators(df)
```

#### 分析机构行为
```python
from src.features.institutional import InstitutionalFeatures

extractor = InstitutionalFeatures()
features = extractor.extract_all_features('600519.SH', days=30)
```

### 已实现功能 ✅

**数据获取层**
- ✅ 股票行情数据（日线、分钟线、实时）
- ✅ 机构持仓、龙虎榜、大宗交易数据
- ✅ 北向资金、融资融券数据
- ✅ 资金流向数据

**特征工程层**
- ✅ 技术指标计算（15+ 指标）
- ✅ 机构行为特征（10+ 特征）
- ✅ 市场情绪特征（20+ 特征）

### 开发中功能 🚧

- ⏳ LSTM/XGBoost/Transformer AI模型
- ⏳ 预测接口与回测系统
- ⏳ 可视化图表
- ⏳ Web界面

### 风险提示

⚠️ **重要声明**
- 本系统仅供学习和研究使用
- 不构成任何投资建议
- 股市有风险，投资需谨慎

### 许可证

MIT License

---

## English

### Project Overview

An AI-powered stock breakout prediction system based on institutional behavior analysis. It analyzes institutional fund flows, position changes, and trading behaviors to predict potential stock breakouts.

**Current Status**: ✅ Core features completed, data acquisition and feature engineering modules verified

### Core Features

#### 🔍 Institutional Detection
- **Institutional Position Monitoring**: Track holdings of funds, QFII, social security, etc.
- **Dragon-Tiger List Analysis**: Analyze institutional trading behaviors
- **Main Fund Flow**: Real-time monitoring of large order flows
- **Northbound Capital Tracking**: Stock Connect fund flow analysis

#### 🤖 AI Prediction Models (In Development)
- **LSTM Time Series Model**: Capture stock price patterns
- **XGBoost Classification Model**: Feature-based breakout classification
- **Transformer Attention Model**: Long-term dependency learning
- **Ensemble Model**: Multi-model fusion for improved accuracy

#### 📊 Data Analysis (Completed ✅)
- **Technical Indicators**: 15+ indicators including MA, MACD, RSI, KDJ, BOLL
- **Institutional Features**: 10+ features including position changes, fund flow intensity
- **Market Sentiment**: 20+ features including turnover rate, amplitude, price rankings

#### 📈 Visualization (In Development)
- K-line charts with fund flow overlay
- Institutional position trend charts
- Prediction probability heatmaps
- Backtesting return curves

### Project Structure

```
stock/
├── data/                    # Data directory
│   ├── raw/                # Raw data
│   ├── processed/          # Processed data
│   └── models/             # Trained models
├── src/                    # Source code
│   ├── data_acquisition/   # ✅ Data acquisition
│   │   ├── stock_data.py      # Stock market data
│   │   ├── institution.py     # Institutional data
│   │   └── fund_flow.py       # Fund flow data
│   ├── preprocessing/      # Data preprocessing
│   ├── features/           # ✅ Feature engineering
│   │   ├── technical.py       # Technical indicators
│   │   ├── institutional.py   # Institutional features
│   │   └── sentiment.py       # Market sentiment
│   ├── models/             # ⏳ AI models
│   ├── training/           # ⏳ Model training
│   ├── prediction/         # ⏳ Prediction service
│   ├── visualization/      # ⏳ Visualization
│   └── api/                # ⏳ API endpoints
├── configs/                # ✅ Configuration files
├── docs/                   # ✅ Documentation
└── scripts/                # ✅ Utility scripts
```

### Technology Stack

**Backend**
- Python 3.12
- FastAPI / Flask
- pandas, numpy
- scikit-learn
- TensorFlow / PyTorch
- XGBoost
- TA-Lib

**Frontend**
- HTML5, CSS3, JavaScript
- ECharts (Chart visualization)
- Bootstrap

**Data Sources**
- ✅ **AkShare** (Free, verified)
- Tushare Pro (Token required)
- East Money

### Quick Start

#### Option 1: Using Docker (Recommended)

```bash
# Enter docker directory
cd docker

# Start services
docker-compose up -d

# Run demo
docker-compose exec stock python scripts/quick_start.py

# Stock prediction
docker-compose exec stock python scripts/predict_stock.py 600519
```

📖 Detailed docs: [Docker Usage Guide](docs/DOCKER.md)

#### Option 2: Local Installation

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure Data Sources (Optional)**
Edit `configs/config.yaml`:
```yaml
data_sources:
  tushare:
    token: "your_tushare_token_here"  # Optional
```

**3. Run Quick Demo**
```bash
python scripts/quick_start.py
```

**4. Stock Prediction**
```bash
# Single prediction
python scripts/predict_stock.py 600519

# Interactive mode
python scripts/predict_stock.py
```

### Usage Examples

#### Fetch Stock Data
```python
from src.data_acquisition.stock_data import StockDataFetcher

fetcher = StockDataFetcher()
df = fetcher.get_daily_data('600519')  # Kweichow Moutai
```

#### Calculate Technical Indicators
```python
from src.features.technical import TechnicalIndicators

calculator = TechnicalIndicators()
df_with_indicators = calculator.calculate_all_indicators(df)
```

#### Analyze Institutional Behavior
```python
from src.features.institutional import InstitutionalFeatures

extractor = InstitutionalFeatures()
features = extractor.extract_all_features('600519.SH', days=30)
```

### Implemented Features ✅

**Data Acquisition Layer**
- ✅ Stock market data (daily, minute, real-time)
- ✅ Institutional holdings, dragon-tiger list, block trades
- ✅ Northbound capital, margin trading data
- ✅ Fund flow data

**Feature Engineering Layer**
- ✅ Technical indicators (15+ indicators)
- ✅ Institutional behavior features (10+ features)
- ✅ Market sentiment features (20+ features)

### Features In Development 🚧

- ⏳ LSTM/XGBoost/Transformer AI models
- ⏳ Prediction API and backtesting system
- ⏳ Visualization charts
- ⏳ Web interface

### Risk Disclaimer

⚠️ **Important Notice**
- This system is for educational and research purposes only
- Does not constitute investment advice
- Stock market involves risks, invest cautiously

### License

MIT License

---

**Last Updated**: 2025-11-20  
**Project Status**: Core features completed ✅  
**Next Step**: AI model development
