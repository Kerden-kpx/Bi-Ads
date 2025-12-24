# Docker 更新指南

## 📋 更新步骤

### 方法一：使用 Docker Compose（推荐）

#### 前端更新

```bash
# 1. 进入前端目录
cd frontend

# 2. 停止并删除旧容器
docker-compose down

# 3. 重新构建镜像（包含最新代码）
docker-compose build --no-cache

# 4. 启动新容器
docker-compose up -d

# 5. 查看日志确认启动成功
docker-compose logs -f frontend
```

#### 后端更新

```bash
# 1. 进入后端目录
cd backend

# 2. 停止并删除旧容器
docker-compose down

# 3. 重新构建镜像（包含最新代码）
docker-compose build --no-cache

# 4. 启动新容器
docker-compose up -d

# 5. 查看日志确认启动成功
docker-compose logs -f backend
```

#### 同时更新前后端

```bash
# 在项目根目录执行（如果有统一的 docker-compose.yml）
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f
```

### 方法二：手动 Docker 命令

#### 前端更新

```bash
cd frontend

# 1. 停止容器
docker stop ads-bi-frontend
docker rm ads-bi-frontend

# 2. 构建新镜像
docker build -t ads-bi-frontend:latest .

# 3. 启动容器
docker run -d \
  --name ads-bi-frontend \
  -p 5173:5173 \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  ads-bi-frontend:latest

# 4. 查看日志
docker logs -f ads-bi-frontend
```

#### 后端更新

```bash
cd backend

# 1. 停止容器
docker stop ads-bi-backend
docker rm ads-bi-backend

# 2. 构建新镜像
docker build -t ads-bi-backend:latest .

# 3. 启动容器（需要 .env 文件）
docker run -d \
  --name ads-bi-backend \
  -p 7800:7800 \
  --env-file .env \
  --add-host=host.docker.internal:host-gateway \
  -e DEBUG=False \
  -e WORKERS=4 \
  --restart unless-stopped \
  ads-bi-backend:latest

# 4. 查看日志
docker logs -f ads-bi-backend
```

### 方法三：快速更新（不重新构建，仅重启）

⚠️ **注意：此方法仅适用于代码已通过其他方式更新到容器内的情况**

```bash
# 前端
cd frontend
docker-compose restart frontend

# 后端
cd backend
docker-compose restart backend
```

## 🔍 验证更新

### 检查容器状态

```bash
# 查看所有容器状态
docker ps

# 查看特定容器状态
docker ps | grep ads-bi

# 查看容器详细信息
docker inspect ads-bi-frontend
docker inspect ads-bi-backend
```

### 检查服务健康

```bash
# 前端健康检查
curl http://localhost:5173

# 后端健康检查
curl http://localhost:7800/health
```

### 查看日志

```bash
# 前端日志
docker logs ads-bi-frontend
docker logs -f ads-bi-frontend  # 实时查看

# 后端日志
docker logs ads-bi-backend
docker logs -f ads-bi-backend  # 实时查看

# 使用 docker-compose
docker-compose logs -f frontend
docker-compose logs -f backend
```

## 🚀 一键更新脚本

### 创建更新脚本

创建 `update.sh`（Linux/Mac）或 `update.bat`（Windows）：

#### Linux/Mac (update.sh)

```bash
#!/bin/bash

echo "🚀 开始更新 Docker 容器..."

# 更新前端
echo "📦 更新前端..."
cd frontend
docker-compose down
docker-compose build --no-cache
docker-compose up -d
cd ..

# 更新后端
echo "📦 更新后端..."
cd backend
docker-compose down
docker-compose build --no-cache
docker-compose up -d
cd ..

echo "✅ 更新完成！"
echo "📊 查看容器状态："
docker ps | grep ads-bi

echo "📝 查看日志："
echo "前端: docker-compose -f frontend/docker-compose.yml logs -f"
echo "后端: docker-compose -f backend/docker-compose.yml logs -f"
```

#### Windows (update.bat)

```batch
@echo off
echo 🚀 开始更新 Docker 容器...

echo 📦 更新前端...
cd frontend
docker-compose down
docker-compose build --no-cache
docker-compose up -d
cd ..

echo 📦 更新后端...
cd backend
docker-compose down
docker-compose build --no-cache
docker-compose up -d
cd ..

echo ✅ 更新完成！
echo 📊 查看容器状态：
docker ps | findstr ads-bi
```

使用脚本：

```bash
# Linux/Mac
chmod +x update.sh
./update.sh

# Windows
update.bat
```

## ⚠️ 注意事项

### 1. 代码同步
确保服务器上的代码是最新的：

```bash
# 如果使用 Git
git pull origin main

# 或者使用 scp/rsync 上传代码
scp -r frontend/src user@server:/path/to/project/frontend/
scp -r backend/app user@server:/path/to/project/backend/
```

### 2. 环境变量
更新后端时，确保 `.env` 文件存在且配置正确：

```bash
cd backend
# 检查 .env 文件
cat .env
```

### 3. 数据持久化
如果使用了数据卷（volumes），确保数据不会丢失：

```bash
# 查看数据卷
docker volume ls

# 备份数据（如需要）
docker run --rm -v volume_name:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

### 4. 端口占用
确保端口未被占用：

```bash
# 检查端口占用
netstat -tuln | grep 5173
netstat -tuln | grep 7800

# 或使用
lsof -i :5173
lsof -i :7800
```

### 5. 构建缓存
如果遇到问题，可以清理 Docker 缓存：

```bash
# 清理构建缓存
docker builder prune

# 清理所有未使用的资源
docker system prune -a
```

## 🔧 常见问题

### 问题1：构建失败

```bash
# 查看详细错误信息
docker-compose build --no-cache --progress=plain

# 清理缓存后重试
docker builder prune
docker-compose build --no-cache
```

### 问题2：容器无法启动

```bash
# 查看容器日志
docker logs ads-bi-frontend
docker logs ads-bi-backend

# 检查容器配置
docker inspect ads-bi-frontend
```

### 问题3：端口冲突

```bash
# 停止占用端口的容器
docker ps | grep 5173
docker stop <container_id>

# 或修改 docker-compose.yml 中的端口映射
```

### 问题4：环境变量未生效

```bash
# 检查 .env 文件
cat backend/.env

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📝 更新检查清单

- [ ] 代码已同步到服务器
- [ ] 环境变量配置正确（.env 文件）
- [ ] 停止旧容器
- [ ] 重新构建镜像（--no-cache）
- [ ] 启动新容器
- [ ] 检查容器状态（docker ps）
- [ ] 检查服务健康（curl /health）
- [ ] 查看日志确认无错误
- [ ] 测试前端页面
- [ ] 测试后端 API

## 🎯 快速参考

```bash
# 前端更新
cd frontend && docker-compose down && docker-compose build --no-cache && docker-compose up -d

# 后端更新
cd backend && docker-compose down && docker-compose build --no-cache && docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker ps
```




