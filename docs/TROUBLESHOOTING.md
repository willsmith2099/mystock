# 故障排除指南

## 常见问题

### 1. 资金流向数据获取失败
**错误信息**: `HTTPSConnectionPool(host='push2.eastmoney.com', ...): Max retries exceeded ... ProxyError`

**原因**: 东方财富网的API接口对网络环境比较敏感，或者您的网络使用了代理导致连接失败。

**解决方案**:
- 尝试关闭VPN或代理软件
- 检查网络连接是否稳定
- 如果在公司网络，尝试切换到个人热点
- 该功能失败不影响其他核心功能（如技术指标计算）

### 2. Tushare Token未配置
**错误信息**: `警告: Tushare token未配置，部分功能将不可用`

**原因**: `configs/config.yaml` 中未填入Tushare Pro的token。

**解决方案**:
1. 注册 [Tushare Pro](https://tushare.pro/) 账号
2. 获取Token
3. 编辑 `configs/config.yaml` 填入Token
4. 或者忽略此警告，系统会自动切换到AkShare数据源

### 3. 依赖安装失败
**错误信息**: `ERROR: Could not find a version that satisfies the requirement mplfinance>=0.12.0`

**原因**: 某些Python版本可能不兼容特定版本的库。

**解决方案**:
- 尝试放宽版本限制，例如修改 `requirements.txt` 中的 `mplfinance>=0.12.0` 为 `mplfinance`
- 使用 `pip install -r requirements.txt --no-deps` 然后手动安装缺失的库

### 4. 数据为空
**错误信息**: `✗ 未获取到数据`

**原因**: 
- 股票代码错误（应为6位数字）
- 非交易日或停牌
- 网络连接问题

**解决方案**:
- 检查股票代码是否正确
- 检查是否在交易时间
- 运行 `python scripts/quick_start.py` 测试基础连接
