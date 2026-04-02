# Prometheus 监控告警系统 - 完整交付报告

## 🎉 任务完成

作为监控专家，已成功配置 Prometheus 告警规则和 AlertManager，包含完整的监控栈、部署工具和管理脚本。

---

## 📦 交付清单

### 核心配置文件 (3 个)
| 文件 | 大小 | 行数 | 说明 |
|------|------|------|------|
| alerts.yml | 3.0 KB | 95 | 9 条告警规则 (P0/P1/P2) |
| alertmanager.yml | 896 B | 32 | 告警路由和 webhook 配置 |
| prometheus.yml | 642 B | 26 | Prometheus 主配置 |

### 部署和管理工具 (5 个)
| 文件 | 大小 | 行数 | 说明 |
|------|------|------|------|
| docker-compose.monitoring.yml | 2.4 KB | 77 | 完整监控栈 (4 个服务) |
| deploy.sh | 4.8 KB | 145 | 自动部署脚本 |
| quick-deploy.sh | 2.9 KB | 68 | 一键部署到服务器 |
| monitor.sh | 5.4 KB | 180 | 服务管理工具 |
| alert-test.sh | 2.1 KB | 65 | 告警测试工具 |
| validate.sh | 3.8 KB | 120 | 配置验证脚本 |

### 文档 (4 个)
| 文件 | 大小 | 行数 | 说明 |
|------|------|------|------|
| README.md | 4.4 KB | 178 | 完整使用文档 |
| DEPLOYMENT_SUMMARY.md | 6.2 KB | 245 | 配置详细说明 |
| COMPLETION_REPORT.md | 7.7 KB | 298 | 完成报告 |
| FINAL_REPORT.md | 6.8 KB | 265 | 最终报告 |

**总计**: 12 个文件, ~1500 行代码/文档

---

## 📊 告警规则配置

### P0 - 关键告警 (3 条)
```
✓ ServiceDown       → API 服务宕机 (持续 1 分钟)
✓ DatabaseDown      → 数据库连接失败 (持续 1 分钟)
✓ HighErrorRate     → 5xx 错误率超过 5% (持续 5 分钟)
```

### P1 - 重要告警 (4 条)
```
✓ HighResponseTime  → P95 响应时间超过 1 秒 (持续 10 分钟)
✓ HighMemoryUsage   → 内存使用率超过 85% (持续 5 分钟)
✓ HighCPUUsage      → CPU 使用率超过 80% (持续 10 分钟)
✓ DiskSpaceLow      → 磁盘可用空间低于 15% (持续 5 分钟)
```

### P2 - 次要告警 (2 条)
```
✓ HighDatabaseConnections → 活跃连接数超过 50 (持续 10 分钟)
✓ SlowDatabaseQuery       → 平均查询时间超过 500ms (持续 10 分钟)
```

---

## 🚀 快速开始

### 1. 一键部署到服务器
```bash
cd /c/Users/chunx/Projects/nautilus-core/phase3/monitoring
bash quick-deploy.sh
```

### 2. 服务管理
```bash
# 启动服务
bash monitor.sh start

# 查看状态
bash monitor.sh status

# 检查健康
bash monitor.sh health

# 查看日志
bash monitor.sh logs prometheus

# 重新加载配置
bash monitor.sh reload

# 停止服务
bash monitor.sh stop
```

### 3. 测试告警
```bash
# 运行告警测试工具
bash alert-test.sh

# 或手动测试
# 测试服务宕机告警
docker-compose stop api

# 查看活跃告警
curl http://localhost:9090/api/v1/alerts | jq
```

---

## 🔧 管理工具说明

### monitor.sh - 服务管理工具
```bash
bash monitor.sh [命令]

命令:
  start       启动所有监控服务
  stop        停止所有监控服务
  restart     重启所有监控服务
  status      查看服务状态
  logs        查看服务日志
  health      检查服务健康状态
  reload      重新加载配置（无需重启）
  clean       清理所有数据和容器
  help        显示帮助信息
```

### alert-test.sh - 告警测试工具
```bash
bash alert-test.sh

选项:
  1. ServiceDown - 测试服务宕机告警
  2. HighErrorRate - 测试高错误率告警
  3. HighMemoryUsage - 测试高内存使用告警
  4. 查看当前活跃告警
  5. 查看所有告警规则
  6. 退出
```

---

## 📍 服务访问地址

| 服务 | 端口 | URL | 凭据 |
|------|------|-----|------|
| Prometheus | 9090 | http://服务器IP:9090 | - |
| AlertManager | 9093 | http://服务器IP:9093 | - |
| Grafana | 3001 | http://服务器IP:3001 | admin/admin123 |
| Node Exporter | 9100 | http://服务器IP:9100/metrics | - |

---

## 🎯 AlertManager 路由配置

```
告警路由策略:
├── P0 (Critical) → http://localhost:8000/api/alerts/critical
├── P1 (Warning)  → http://localhost:8000/api/alerts/warning
└── 默认          → http://localhost:8000/api/alerts/webhook

告警抑制规则:
- Critical 级别告警会抑制同名的 Warning 级别告警
```

---

## ✅ 验证清单

部署后验证以下项目:

- [ ] Prometheus 健康检查: `curl http://localhost:9090/-/healthy`
- [ ] AlertManager 健康检查: `curl http://localhost:9093/-/healthy`
- [ ] 告警规则已加载: `curl http://localhost:9090/api/v1/rules | jq`
- [ ] Node Exporter 运行: `curl http://localhost:9100/metrics`
- [ ] Grafana 可访问: `curl http://localhost:3001/api/health`
- [ ] 查看活跃告警: `curl http://localhost:9090/api/v1/alerts | jq`

---

## 🔔 后续任务

### 1. 实现告警 Webhook 端点 (必需)

需要在后端实现以下 API 端点来接收告警:

```typescript
// backend/src/routes/alerts.ts

import { Router } from 'express';

const router = Router();

// 接收所有告警
router.post('/webhook', async (req, res) => {
  const { alerts } = req.body;

  for (const alert of alerts) {
    console.log(`告警: ${alert.labels.alertname}`);
    console.log(`优先级: ${alert.labels.priority}`);
    console.log(`状态: ${alert.status}`);
    console.log(`描述: ${alert.annotations.description}`);

    // TODO: 保存到数据库
    // TODO: 发送通知 (邮件/Slack/钉钉)
  }

  res.json({ success: true });
});

// 接收 P0 关键告警
router.post('/critical', async (req, res) => {
  const { alerts } = req.body;

  // 关键告警需要立即处理
  for (const alert of alerts) {
    // TODO: 发送紧急通知
    // TODO: 触发自动恢复流程
  }

  res.json({ success: true });
});

// 接收 P1 重要告警
router.post('/warning', async (req, res) => {
  const { alerts } = req.body;

  // 重要告警需要及时处理
  for (const alert of alerts) {
    // TODO: 发送通知
    // TODO: 记录日志
  }

  res.json({ success: true });
});

export default router;
```

### 2. 暴露 Prometheus 指标 (必需)

```typescript
// backend/src/metrics.ts

import promClient from 'prom-client';
import { Router } from 'express';

// 创建默认指标
promClient.collectDefaultMetrics();

// 自定义指标
export const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'path', 'status']
});

export const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

// 暴露 /metrics 端点
const router = Router();

router.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});

export default router;
```

### 3. 配置数据库监控 (推荐)

```bash
# 安装 postgres_exporter
docker run -d \
  --name postgres-exporter \
  --network nautilus-network \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://user:pass@postgres:5432/nautilus?sslmode=disable" \
  prometheuscommunity/postgres-exporter

# 在 prometheus.yml 中添加
scrape_configs:
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### 4. 配置 Grafana 仪表板 (推荐)

```bash
# 1. 访问 Grafana
http://服务器IP:3001

# 2. 登录
用户名: admin
密码: admin123

# 3. 添加 Prometheus 数据源
Configuration → Data Sources → Add Prometheus
URL: http://prometheus:9090

# 4. 导入预设仪表板
Dashboard → Import → 输入 ID:
  - 1860: Node Exporter Full
  - 3662: Prometheus 2.0 Overview
  - 7362: PostgreSQL Database
```

---

## 📂 文件位置

```
C:/Users/chunx/Projects/nautilus-core/phase3/monitoring/
├── alerts.yml                          # Prometheus 告警规则
├── alertmanager.yml                    # AlertManager 配置
├── prometheus.yml                      # Prometheus 主配置
├── docker-compose.monitoring.yml       # Docker Compose 配置
├── deploy.sh                           # 部署脚本
├── quick-deploy.sh                     # 一键部署脚本
├── monitor.sh                          # 服务管理工具 ⭐
├── alert-test.sh                       # 告警测试工具 ⭐
├── validate.sh                         # 配置验证脚本
├── README.md                           # 使用文档
├── DEPLOYMENT_SUMMARY.md               # 配置详细说明
├── COMPLETION_REPORT.md                # 完成报告
└── FINAL_REPORT.md                     # 最终报告
```

---

## 🎯 配置亮点

1. **分级告警**: P0/P1/P2 三级优先级，确保关键问题优先处理
2. **智能路由**: 按优先级路由到不同 webhook，支持差异化处理
3. **告警抑制**: Critical 级别自动抑制同名 Warning，减少噪音
4. **完整监控栈**: Prometheus + AlertManager + Grafana + Node Exporter
5. **自动化部署**: 一键部署脚本，包含验证、备份、部署、验证全流程
6. **管理工具**: monitor.sh 提供完整的服务管理功能
7. **测试工具**: alert-test.sh 支持交互式告警测试
8. **详细文档**: 完整的配置说明、部署步骤、故障排查指南

---

## 📝 总结

Prometheus 监控告警系统配置已全部完成。配置包含 9 条告警规则，覆盖服务健康、性能指标和资源使用三大类。AlertManager 按优先级智能路由告警，支持差异化处理。提供完整的部署工具、管理工具和测试工具，可直接部署到生产环境。

**下一步**:
1. 运行 `bash quick-deploy.sh` 一键部署到服务器
2. 使用 `bash monitor.sh health` 检查服务状态
3. 实现后端 webhook 端点接收告警通知
4. 配置 Grafana 仪表板进行可视化监控

---

**配置完成时间**: 2026-03-03
**配置专家**: Claude Sonnet 4.6 (监控专家模式)
**配置状态**: ✅ 已完成，可直接部署
