# Docker 配置目录 / Docker Configuration Directory

本目录包含所有Docker相关的配置文件。

This directory contains all Docker-related configuration files.

## 文件说明 / Files

- **Dockerfile** - 多阶段构建的Docker镜像定义 / Multi-stage Docker image definition
- **docker-compose.yml** - Docker Compose服务编排配置 / Docker Compose orchestration config
- **docker-entrypoint.sh** - 容器启动脚本 / Container entrypoint script
- **.dockerignore** - Docker构建忽略文件 / Docker build ignore file

## 快速使用 / Quick Usage

### 中文

```bash
# 进入docker目录
cd docker

# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f stock

# 运行演示
docker-compose exec stock python scripts/quick_start.py

# 停止服务
docker-compose down
```

### English

```bash
# Enter docker directory
cd docker

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f stock

# Run demo
docker-compose exec stock python scripts/quick_start.py

# Stop services
docker-compose down
```

## 详细文档 / Detailed Documentation

请查看：[Docker使用指南](../docs/DOCKER.md)

See: [Docker Usage Guide](../docs/DOCKER.md)
