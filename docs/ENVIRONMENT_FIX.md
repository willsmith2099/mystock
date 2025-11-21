# 股票预测系统 - 环境问题修复指南

## 当前发现的问题

### 1. XGBoost 缺少 OpenMP 运行时库

**错误信息**:
```
Library not loaded: @rpath/libomp.dylib
```

**解决方案**:
```bash
# 安装 OpenMP 运行时库
brew install libomp

# 如果没有 Homebrew，先安装：
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. TensorFlow 导入卡住（mutex 锁定问题）

**原因**: 
- TensorFlow 在某些 macOS 环境下可能与系统线程库冲突
- 这是一个已知的兼容性问题

**解决方案**:

**方案 A**: 使用轻量级替代方案（推荐）
```bash
# 卸载 TensorFlow
pip uninstall tensorflow

# 使用 PyTorch 替代（可选）
pip install torch torchvision
```

**方案 B**: 使用 TensorFlow 的 macOS 优化版本
```bash
pip uninstall tensorflow
pip install tensorflow-macos tensorflow-metal
```

**方案 C**: 暂时跳过深度学习模型
- 系统的核心功能（数据获取、特征工程、XGBoost）不依赖 TensorFlow
- 可以先使用 XGBoost 模型进行预测

## 快速修复步骤

### 步骤 1: 修复 XGBoost
```bash
brew install libomp
```

### 步骤 2: 处理 TensorFlow（选择一个方案）

**如果不需要 LSTM 模型**（推荐）:
```bash
pip uninstall tensorflow
```

**如果需要深度学习功能**:
```bash
pip uninstall tensorflow
pip install tensorflow-macos tensorflow-metal
```

### 步骤 3: 验证修复
```bash
python -c "import xgboost; print('XGBoost OK')"
```

## 系统当前可用功能

即使不安装 TensorFlow，以下功能仍然完全可用：

✅ **数据获取**
- 股票行情数据
- 机构数据
- 资金流向

✅ **特征工程**
- 技术指标计算
- 机构行为特征
- 市场情绪特征

✅ **预测功能**
- 基于规则的综合评分
- XGBoost 分类模型（修复后）

⏳ **暂不可用**
- LSTM 时序预测（需要 TensorFlow）

## 建议

1. **立即可用**: 当前的预测脚本 (`predict_stock.py`) 不依赖深度学习，可以直接使用
2. **修复 XGBoost**: 运行 `brew install libomp` 即可
3. **TensorFlow**: 如果不需要 LSTM，可以暂时不安装

## 测试命令

```bash
# 测试预测功能（不需要 TensorFlow）
python scripts/predict_stock.py 600519

# 测试完整系统
python scripts/test_system.py
```
