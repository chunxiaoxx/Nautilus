#!/bin/bash
set -e

echo "=== 部署后端监控端点 ==="

# 停止并删除旧容器
echo "1. 清理旧容器..."
docker stop nautilus-backend 2>/dev/null || true
docker rm nautilus-backend 2>/dev/null || true

# 启动后端容器
echo "2. 启动后端容器..."
docker run -d \
  --name nautilus-backend \
  --network host \
  -v /home/ubuntu/nautilus-mvp/phase3/backend:/app \
  -w /app \
  -e PYTHONPATH=/app \
  -e DATABASE_URL="postgresql://nautilus:nautilus_dev_password@localhost:5432/nautilus_dev" \
  -e REDIS_URL="redis://localhost:6379/0" \
  backend-backend:latest \
  sh -c 'pip install --no-cache-dir prometheus-client && python -m uvicorn main:socket_app_with_fastapi --host 0.0.0.0 --port 8000'

# 等待启动
echo "3. 等待服务启动..."
sleep 15

# 检查服务状态
echo "4. 检查服务状态..."
docker logs nautilus-backend --tail 20

# 测试端点
echo "5. 测试监控端点..."
curl -s http://localhost:8000/metrics | head -20 || echo "Metrics 端点未就绪"
curl -s http://localhost:8000/api/alerts/health || echo "Alerts 端点未就绪"

echo "=== 部署完成 ==="
