# CLAUDE.md - Nautilus Project Configuration

> 这个文件会被所有Claude Code会话自动加载

## 项目信息

**项目名称**: Nautilus - AI Agent生态系统
**目标**: 让AI Agent真正"活"起来 - 能赚钱、能进化、能繁衍
**当前阶段**: Week 2 - 性能优化 + 生存机制实施

## 核心规则（必须遵守）

### 1. 响应风格
- 简洁直接，不重复
- 不使用emoji（除非明确要求）
- 不输出代码，直接用工具编辑
- 完成后简短确认，不解释

### 2. 并行执行
- 独立任务必须在单个消息中并行调用
- 不等待不必要的中间结果
- 最大化并行效率

### 3. 工具优先级
- Read > cat
- Edit > sed
- Write > echo
- Glob > find
- Grep > grep
- 只在必要时使用Bash（git、npm、系统命令）

### 4. 任务管理
- 复杂任务（≥3步）使用TaskCreate
- 开始工作前标记in_progress
- 完成后立即标记completed

## 技术栈

### Backend
- Python 3.11+, FastAPI, PostgreSQL, Redis
- SQLAlchemy (async), Alembic
- Web3.py, eth-account

### Frontend
- React 19, TypeScript, Vite
- TailwindCSS, MetaMask

### Blockchain
- Base Chain (8453)
- USDC: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

## 质量标准

### 代码质量
- 测试覆盖率 ≥ 80%
- 代码评分 ≥ 9.0/10
- 无CRITICAL/HIGH问题

### 性能目标
- 单用户P95 < 500ms
- 并发P95 < 1000ms
- 吞吐量 > 10 req/s
- 缓存命中率 > 60%

## 协作模式

### 三对话框系统
- **Dialog A**: 开发执行（团队模式）
- **Dialog B**: 架构协调（战略决策）
- **Dialog C**: 质量保证（Phase审查）

### 工作流程
1. 创建任务
2. 并行执行
3. 持续审查
4. Phase验收

## 关键约定

### 钱包认证
```python
# 必须使用encode_defunct
from eth_account.messages import encode_defunct
message_hash = encode_defunct(text=message)
recovered = w3.eth.account.recover_message(message_hash, signature)

# 地址小写比较
if recovered.lower() != address.lower():
    raise Exception("Invalid signature")
```

### API响应格式
```python
{
    "success": true,
    "data": {},
    "error": null,
    "meta": {}
}
```

### 错误处理
```python
raise HTTPException(
    status_code=400,
    detail={
        "error": {
            "code": "ERROR_CODE",
            "message": "User friendly message",
            "details": {}
        }
    }
)
```

## 快速命令

```bash
# Backend
cd backend && uvicorn main:app --reload
pytest --cov=. --cov-report=html
alembic upgrade head

# Frontend
cd frontend && npm run dev
npm run build
npm test

# Performance
python backend/tests/test_wallet_performance.py
```

## 重要文档

- `WEEK2_IMPLEMENTATION_PLAN.md` - Week 2计划
- `SURVIVAL_MECHANISM_DESIGN.md` - 生存机制设计
- `API_CONTRACT_SPEC.md` - API规范
- `CLAUDE_CODE_ENHANCEMENT_PLAN.md` - Claude Code强化

## 当前状态

**Week 1**: ✅ 完成，已部署
**Week 2 Phase 1**: 🚀 进行中（性能优化，2天）
**Week 2 Phase 2**: 📋 待启动（生存机制，3天）

## 联系方式

- Dialog A: 开发执行
- Dialog B: 架构协调
- Dialog C: 质量保证

---

**详细规则**: 参见 `~/.claude/rules/` 目录
