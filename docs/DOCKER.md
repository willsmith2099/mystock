# Docker 使用指南 / Docker Usage Guide

[中文](#中文) | [English](#english)

---

## 中文

### 快速开始

#### 1. 使用 Docker Compose（推荐）

**启动服务**
```bash
# 进入docker目录
cd docker

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f stock

# 查看状态
docker-compose ps
```

**运行演示**
```bash
# 快速演示
docker-compose exec stock python scripts/quick_start.py

# 股票预测
docker-compose exec stock python scripts/predict_stock.py 600519

# 系统测试
docker-compose exec stock python scripts/test_system.py
```

**停止服务**
```bash
docker-compose down

# 同时删除数据卷
docker-compose down -v
```

#### 2. 使用 Docker 命令

**构建镜像**
```bash
cd docker
docker build -f Dockerfile -t mystock:latest ..
```

**运行容器**
```bash
# 运行API服务
docker run -d \
  --name stock-prediction \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  mystock:latest

# 运行演示
docker run --rm mystock:latest demo

# 运行预测
docker run --rm mystock:latest predict 600519

# 进入容器
docker exec -it stock-prediction bash
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_ENV` | 运行环境 | `production` |
| `TZ` | 时区 | `Asia/Shanghai` |
| `PYTHONUNBUFFERED` | Python输出缓冲 | `1` |

### 数据持久化

以下目录通过卷挂载实现数据持久化：
- `/app/data` - 数据文件
- `/app/logs` - 日志文件
- `/app/configs` - 配置文件（只读）

### 运行模式

容器支持多种运行模式：

```bash
# 进入docker目录
cd docker

# API服务模式
docker-compose run stock api

# 后台任务模式
docker-compose run stock worker

# 测试模式
docker-compose run stock test

# 演示模式
docker-compose run stock demo

# 预测模式
docker-compose run stock predict 600519

# 交互式Shell
docker-compose run stock bash
```

### 资源限制

默认资源配置（可在 docker-compose.yml 中修改）：
- CPU: 1-2 核
- 内存: 2-4 GB

### 健康检查

容器包含健康检查功能，每30秒检查一次：
```bash
# 查看健康状态
docker inspect --format='{{.State.Health.Status}}' stock-prediction
```

### 故障排除

**问题1：构建时间过长**
- 原因：首次构建需要编译TA-Lib（5-10分钟）
- 解决：耐心等待，后续构建会使用缓存

**问题2：容器无法启动**
```bash
# 查看日志
docker-compose logs stock

# 检查权限
ls -la data/ logs/
```

**问题3：数据无法持久化**
```bash
# 检查卷挂载
docker inspect stock-prediction | grep Mounts -A 20
```

**问题4：内存不足**
```bash
# 调整docker-compose.yml中的内存限制
deploy:
  resources:
    limits:
      memory: 8G  # 增加到8GB
```

### 生产部署建议

1. **使用环境变量文件**
```bash
# 创建 .env 文件
cat > .env << EOF
APP_ENV=production
TZ=Asia/Shanghai
EOF

# 使用 .env 文件启动
docker-compose --env-file .env up -d
```

2. **配置日志轮转**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "5"
```

3. **使用外部数据库**
- 取消注释 docker-compose.yml 中的数据库服务
- 配置数据库连接信息

4. **监控和告警**
```bash
# 使用 docker stats 监控资源
docker stats stock-prediction

# 配置健康检查告警
# 可以集成 Prometheus + Grafana
```

---

## English

### Quick Start

#### 1. Using Docker Compose (Recommended)

**Start Services**
```bash
# Enter docker directory
cd docker

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f stock

# Check status
docker-compose ps
```

**Run Demos**
```bash
# Quick demo
docker-compose exec stock python scripts/quick_start.py

# Stock prediction
docker-compose exec stock python scripts/predict_stock.py 600519

# System test
docker-compose exec stock python scripts/test_system.py
```

**Stop Services**
```bash
docker-compose down

# Also remove volumes
docker-compose down -v
```

#### 2. Using Docker Commands

**Build Image**
```bash
cd docker
docker build -f Dockerfile -t mystock:latest ..
```

**Run Container**
```bash
# Run API service
docker run -d \
  --name stock-prediction \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  mystock:latest

# Run demo
docker run --rm mystock:latest demo

# Run prediction
docker run --rm mystock:latest predict 600519

# Enter container
docker exec -it stock-prediction bash
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment | `production` |
| `TZ` | Timezone | `Asia/Shanghai` |
| `PYTHONUNBUFFERED` | Python buffering | `1` |

### Data Persistence

The following directories are persisted via volume mounts:
- `/app/data` - Data files
- `/app/logs` - Log files
- `/app/configs` - Configuration files (read-only)

### Run Modes

The container supports multiple run modes:

```bash
# Enter docker directory
cd docker

# API service mode
docker-compose run stock api

# Worker mode
docker-compose run stock worker

# Test mode
docker-compose run stock test

# Demo mode
docker-compose run stock demo

# Prediction mode
docker-compose run stock predict 600519

# Interactive shell
docker-compose run stock bash
```

### Resource Limits

Default resource configuration (can be modified in docker-compose.yml):
- CPU: 1-2 cores
- Memory: 2-4 GB

### Health Check

Container includes health check functionality, checked every 30 seconds:
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' stock-prediction
```

### Troubleshooting

**Issue 1: Long build time**
- Cause: First build needs to compile TA-Lib (5-10 minutes)
- Solution: Be patient, subsequent builds will use cache

**Issue 2: Container won't start**
```bash
# View logs
docker-compose logs stock

# Check permissions
ls -la data/ logs/
```

**Issue 3: Data not persisting**
```bash
# Check volume mounts
docker inspect stock-prediction | grep Mounts -A 20
```

**Issue 4: Out of memory**
```bash
# Adjust memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G  # Increase to 8GB
```

### Production Deployment Tips

1. **Use environment file**
```bash
# Create .env file
cat > .env << EOF
APP_ENV=production
TZ=Asia/Shanghai
EOF

# Start with .env file
docker-compose --env-file .env up -d
```

2. **Configure log rotation**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "5"
```

3. **Use external database**
- Uncomment database service in docker-compose.yml
- Configure database connection

4. **Monitoring and alerting**
```bash
# Monitor resources with docker stats
docker stats stock-prediction

# Configure health check alerts
# Can integrate with Prometheus + Grafana
```

---

**Last Updated**: 2025-11-21  
**Docker Version**: 20.10+  
**Docker Compose Version**: 2.0+
