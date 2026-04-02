# Prometheus 告警配置总结

## 配置完成情况

### ✅ 已创建的配置文件

1. **alerts.yml** - Prometheus 告警规则
   - 9 条告警规则，覆盖 P0/P1/P2 三个优先级
   - 包含服务健康、性能、资源使用等关键指标

2. **alertmanager.yml** - AlertManager 配置
   - 按优先级路由告警
   - 配置 webhook 通知端点
   - 告警抑制规则

3. **prometheus.yml** - Prometheus 主配置
   - 监控目标配置
   - 告警规则引用
   - AlertManager 集成

4. **docker-compose.monitoring.yml** - Docker Compose 配置
   - Prometheus 服务
   - AlertManager 服务
   - Node Exporter 服务
   - Grafana 可视化服务

5. **deploy.sh** - 部署脚本
   - 自动验证配置
   - 备份现有配置
   - 部署并重启服务

6. **validate.sh** - 验证脚本
   - 语法检查
   - 规则统计
   - 阈值分析

7. **README.md** - 完整文档
   - 配置说明
   - 部署步骤
   - 维护指南

## 告警规则详情

### P0 - 关键告警 (3 条)
| 告警名称 | 触发条件 | 持续时间 | 说明 |
|---------|---------|---------|------|
| ServiceDown | API 服务不可用 | 1 分钟 | 服务宕机 |
| DatabaseDown | 数据库连接失败 | 1 分钟 | 数据库故障 |
| HighErrorRate | 5xx 错误率 > 5% | 5 分钟 | 高错误率 |

### P1 - 重要告警 (4 条)
| 告警名称 | 触发条件 | 持续时间 | 说明 |
|---------|---------|---------|------|
| HighResponseTime | P95 响应时间 > 1s | 10 分钟 | 响应慢 |
| HighMemoryUsage | 内存使用率 > 85% | 5 分钟 | 内存不足 |
| HighCPUUsage | CPU 使用率 > 80% | 10 分钟 | CPU 过高 |
| DiskSpaceLow | 磁盘可用 < 15% | 5 分钟 | 磁盘不足 |

### P2 - 次要告警 (2 条)
| 告警名称 | 触发条件 | 持续时间 | 说明 |
|---------|---------|---------|------|
| HighDatabaseConnections | 连接数 > 50 | 10 分钟 | 连接过多 |
| SlowDatabaseQuery | 平均查询 > 500ms | 10 分钟 | 查询变慢 |

## 部署步骤

### 本地验证（已完成）
```bash
cd /c/Users/chunx/Projects/nautilus-core/phase3/monitoring
bash validate.sh
```

### 上传到服务器
```bash
# 上传配置文件
scp -r monitoring/ cloud:/home/ubuntu/nautilus-mvp/phase3/

# 或使用 rsync
rsync -avz monitoring/ cloud:/home/ubuntu/nautilus-mvp/phase3/monitoring/
```

### 服务器端部署
```bash
ssh cloud
cd /home/ubuntu/nautilus-mvp/phase3/monitoring

# 运行部署脚本
bash deploy.sh

# 或手动启动
docker-compose -f docker-compose.monitoring.yml up -d
```

### 验证部署
```bash
# 检查服务状态
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:9093/-/healthy  # AlertManager

# 查看告警规则
curl http://localhost:9090/api/v1/rules | jq

# 查看活跃告警
curl http://localhost:9090/api/v1/alerts | jq
```

## 访问地址

- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Grafana**: http://localhost:3001 (admin/admin123)
- **Node Exporter**: http://localhost:9100/metrics

## 后续任务

### 1. 实现告警 Webhook 端点
需要在后端实现以下 API 端点：

```typescript
// backend/src/routes/alerts.ts
POST /api/alerts/webhook    // 接收所有告警
POST /api/alerts/critical   // 接收 P0 关键告警
POST /api/alerts/warning    // 接收 P1 重要告警
```

### 2. 配置 Grafana 仪表板
- 导入预设仪表板
- 配置 Prometheus 数据源
- 创建自定义面板

### 3. 测试告警流程
```bash
# 测试服务宕机告警
docker-compose stop api

# 测试高错误率告警
for i in {1..100}; do curl http://localhost:8000/api/nonexistent; done

# 测试内存告警
stress --vm 1 --vm-bytes 2G --timeout 60s
```

### 4. 集成通知渠道
- 邮件通知
- Slack/钉钉/企业微信
- 短信通知（关键告警）

## 配置文件位置

所有配置文件已保存在：
```
C:/Users/chunx/Projects/nautilus-core/phase3/monitoring/
├── alerts.yml                          # 告警规则
├── alertmanager.yml                    # AlertManager 配置
├── prometheus.yml                      # Prometheus 配置
├── docker-compose.monitoring.yml       # Docker Compose
├── deploy.sh                           # 部署脚本
├── validate.sh                         # 验证脚本
└── README.md                           # 完整文档
```

## 监控指标说明

### 服务健康指标
- `up{job="nautilus-api"}` - API 服务可用性
- `pg_up` - 数据库连接状态

### 性能指标
- `http_requests_total` - HTTP 请求总数
- `http_request_duration_seconds` - 请求响应时间
- `rate(http_requests_total{status=~"5.."}[5m])` - 错误率

### 资源指标
- `node_memory_*` - 内存使用情况
- `node_cpu_seconds_total` - CPU 使用情况
- `node_filesystem_*` - 磁盘使用情况

### 数据库指标
- `pg_stat_activity_count` - 活跃连接数
- `pg_stat_statements_mean_time_seconds` - 平均查询时间

## 维护建议

1. **定期检查告警规则**
   - 每月审查告警阈值是否合理
   - 根据实际情况调整触发条件

2. **监控告警质量**
   - 跟踪误报率
   - 优化告警规则减少噪音

3. **备份配置**
   - 定期备份监控配置
   - 版本控制所有配置文件

4. **性能优化**
   - 监控 Prometheus 自身资源使用
   - 定期清理过期数据

## 故障排查

### Prometheus 无法启动
```bash
# 检查配置语法
docker run --rm -v $(pwd):/config prom/prometheus:latest \
  promtool check config /config/prometheus.yml

# 查看日志
docker logs nautilus-prometheus
```

### 告警未触发
```bash
# 检查规则是否加载
curl http://localhost:9090/api/v1/rules

# 检查指标是否存在
curl http://localhost:9090/api/v1/query?query=up

# 查看告警状态
curl http://localhost:9090/api/v1/alerts
```

### AlertManager 未收到告警
```bash
# 检查 AlertManager 配置
docker run --rm -v $(pwd):/config prom/alertmanager:latest \
  amtool check-config /config/alertmanager.yml

# 查看 AlertManager 日志
docker logs nautilus-alertmanager
```
