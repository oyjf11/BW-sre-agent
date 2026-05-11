# OpsPilot Mock Services

> 测试模拟服务 - 用于 OpsPilot Agent 的自动化测试

## 概述

Mock Services 提供了一套完整的模拟服务，用于测试 OpsPilot Agent 的核心功能。这些服务模拟了从工单入口到 RCA 报告生成的全流程，无需依赖外部真实服务即可进行全面的单元测试和集成测试。

## 目录结构

```
mock/
├── __init__.py           # 包入口
├── data.py               # 测试数据
├── services.py           # 模拟服务实现
├── conftest.py           # Pytest fixtures
└── test_mock_services.py # 测试用例示例
```

## 快速开始

### 安装

```bash
# 确保在正确的 Python 环境中
cd your-project
pip install -e mock/
```

### 基本使用

```python
from mock.services import MockIntakeService, MockTriageService

# 创建服务实例
intake = MockTriageService()

# 异步调用
import asyncio

async def test():
    result = await intake.triage(
        {"description": "支付服务 5xx 错误率飙升"}
    )
    print(result)

asyncio.run(test())
```

## 测试数据

### MockIncidentData

提供各类测试工单数据：

- `TEXT_INCIDENT_NORMAL`: 文本工单（正常流程）
- `STRUCTURED_INCIDENT_NORMAL`: 结构化工单（正常流程）
- `RELEASE_REGRESSION_INCIDENT`: 发布回归工单
- `INCIDENT_EMPTY`: 空输入（异常流程）
- `INCIDENT_INVALID`: 无效格式（异常流程）
- `MULTI_ENTITY_INCIDENT`: 多实体（边界条件）

### MockTriageData

提供分诊结果数据：

- `TRIAGE_ERROR_RATE`: 错误率分诊
- `TRIAGE_PERFORMANCE`: 性能分诊
- `TRIAGE_RELEASE_REGRESSION`: 发布回归分诊
- `TRIAGE_INSUFFICIENT_INFO`: 信息不足（异常）
- `TRIAGE_CONFLICTING_INFO`: 信息冲突（异常）

### MockEvidenceData

提供证据数据：

- `LOGS_EVIDENCE`: 日志证据
- `METRICS_EVIDENCE`: 指标证据
- `DEPLOYMENT_EVIDENCE`: 部署记录证据
- `RUNBOOK_EVIDENCE`: Runbook 证据
- `EVIDENCE_TIMEOUT`: 超时证据（异常）
- `EVIDENCE_INSUFFICIENT`: 证据不足（异常）

## 模拟服务

### MockIntakeService

工单入口服务，负责接收和解析工单。

```python
service = MockIntakeService()

# 正常流程
result = await service.submit_ticket({
    "title": "测试工单",
    "description": "支付服务 5xx 错误"
})

# 异常流程
with pytest.raises(ServiceValidationError):
    await service.submit_ticket({"description": ""})
```

### MockTriageService

智能分诊服务，负责判断事件类型和严重级别。

```python
service = MockTriageService()

# 错误率分诊
result = await service.triage({
    "description": "支付服务 5xx 错误率飙升"
})

# 模拟超时
service = MockTriageService(simulate_timeout=True)
```

### MockInvestigatorService

证据收集服务，负责并行收集各类证据。

```python
service = MockInvestigatorService()

# 正常收集
result = await service.collect_evidence(triage_result, plan)

# 部分超时
service = MockInvestigatorService(simulate_timeout=True)

# 完全失败
service = MockInvestigatorService(simulate_failure=True)
```

### MockDiagnoseService

根因分析服务，负责分析证据并生成根因候选。

```python
service = MockDiagnoseService()

# 正常分析
result = await service.analyze(evidence, ticket_data)

# 证据冲突
service = MockDiagnoseService(simulate_conflict=True)

# 证据不足
service = MockDiagnoseService(simulate_insufficient=True)
```

### MockCriticService

批判与校验服务，负责验证分析质量。

```python
service = MockCriticService()

# 正常校验
result = await service.critique(analysis_result, evidence)

# 模拟超时
service = MockCriticService(simulate_timeout=True)
```

### MockApprovalService

人工审批服务，负责处理审批流程。

```python
# 自动审批
service = MockApprovalService(auto_approve=True)

# 手动审批
service = MockApprovalService(auto_approve=False)
result = await service.request_approval(action, context)

# 审批操作
await service.approve(approval_id, approver)
await service.reject(approval_id, approver, reason)
await service.modify_and_approve(approval_id, approver, params, comment)
```

### MockExecutorService

执行器服务，负责执行修复动作。

```python
service = MockExecutorService()

# 正常执行
result = await service.execute(action)

# 失败
service = MockExecutorService(simulate_failure=True)

# 超时
service = MockExecutorService(simulate_timeout=True)

# 幂等性
result1 = await service.execute({"idempotency_key": "test"})
result2 = await service.execute({"idempotency_key": "test"})  # 返回缓存结果

# 审计日志
logs = service.get_audit_logs()
```

### MockRCAService

RCA 报告服务，负责生成复盘报告。

```python
service = MockRCAService()

# 生成报告
result = await service.generate_rca(
    ticket_data=ticket,
    triage_result=triage,
    evidence=evidence,
    analysis_result=analysis,
    execution_result=execution
)

# 获取报告
rca = await service.get_rca(rca_id)

# 确认报告
await service.confirm_rca(rca_id, confirmed_by)
```

### MockKnowledgeService

知识沉淀服务，负责知识的写入和检索。

```python
service = MockKnowledgeService()

# 写入知识（需要确认）
await service.write_knowledge(rca_data, confirmed=True)

# 检索知识
results = await service.retrieve_knowledge({
    "service": "payment-service",
    "incident_type": "error_rate"
})
```

### MockWorkflowService

完整工作流服务，编排所有服务。

```python
service = MockWorkflowService()

# 运行完整流程
result = await service.run_full_workflow(ticket_data)

# 结果包含所有阶段
# {
#     "intake": {...},
#     "triage": {...},
#     "evidence": {...},
#     "diagnose": {...},
#     "critic": {...},
#     "approval": {...},
#     "execution": {...},
#     "rca": {...}
# }
```

## Pytest Fixtures

使用 `conftest.py` 中的 fixtures 简化测试：

```python
# 使用 fixtures
@pytest.mark.asyncio
async def test_intake(mock_intake_service, sample_ticket):
    result = await mock_intake_service.submit_ticket(sample_ticket)
    assert result["status"] == "success"

# 使用错误场景 fixtures
@pytest.mark.asyncio
async def test_timeout(mock_triage_timeout):
    with pytest.raises(ServiceTimeoutError):
        await mock_triage_timeout.triage({})
```

### 可用 Fixtures

**服务 Fixtures**:
- `mock_intake_service`: 工单入口服务
- `mock_triage_service`: 分诊服务
- `mock_investigator_service`: 证据收集服务
- `mock_diagnose_service`: 根因分析服务
- `mock_critic_service`: 批判校验服务
- `mock_approval_service`: 审批服务
- `mock_executor_service`: 执行器服务
- `mock_rca_service`: RCA 服务
- `mock_knowledge_service`: 知识服务
- `mock_workflow_service`: 完整工作流服务

**数据 Fixtures**:
- `sample_ticket`: 示例工单
- `sample_triage`: 示例分诊结果
- `sample_evidence`: 示例证据列表
- `sample_root_cause`: 示例根因
- `sample_action`: 示例动作
- `sample_approval`: 示例审批
- `sample_rca`: 示例 RCA

**错误场景 Fixtures**:
- `mock_intake_error`: 模拟错误
- `mock_triage_timeout`: 分诊超时
- `mock_investigator_timeout`: 证据收集超时
- `mock_investigator_failure`: 证据收集失败
- `mock_diagnose_conflict`: 证据冲突
- `mock_diagnose_insufficient`: 证据不足
- `mock_critic_timeout`: Critic 超时
- `mock_executor_failure`: 执行失败
- `mock_executor_timeout`: 执行超时

## 测试场景覆盖

基于 `document/ops-agent-testing-scenarios.md` 设计，Mock Services 覆盖以下测试场景：

| 功能模块 | 正常流程 | 异常流程 | 边界条件 |
|---------|---------|---------|----------|
| 工单入口 | ✅ | ✅ | ✅ |
| 智能分诊 | ✅ | ✅ | ✅ |
| 排查计划 | ✅ | ✅ | ✅ |
| 证据收集 | ✅ | ✅ | ✅ |
| 根因分析 | ✅ | ✅ | ✅ |
| 批判校验 | ✅ | ✅ | - |
| 人工审批 | ✅ | ✅ | ✅ |
| 执行器 | ✅ | ✅ | ✅ |
| RCA 报告 | ✅ | ✅ | - |
| 知识沉淀 | ✅ | ✅ | - |

## 运行测试

```bash
# 运行所有测试
pytest mock/ -v

# 运行特定测试类
pytest mock/test_mock_services.py::TestMockIntakeService -v

# 运行特定测试
pytest mock/test_mock_services.py::TestMockIntakeService::test_submit_ticket_normal -v
```

## 扩展自定义数据

在 `data.py` 中添加自定义测试数据：

```python
@dataclass
class MyCustomData:
    MY_CUSTOM_INCIDENT = {
        "ticket_id": "INC-MY-001",
        "title": "自定义测试工单",
        # ... 其他字段
    }
```

然后在服务中引用：

```python
service = MockIntakeService()
result = await service.submit_ticket(MyCustomData.MY_CUSTOM_INCIDENT)
```

## 贡献指南

添加新的 Mock 服务时，请遵循以下模式：

1. 在 `data.py` 中添加测试数据类
2. 在 `services.py` 中添加服务实现
3. 在 `conftest.py` 中添加 fixtures
4. 在 `test_mock_services.py` 中添加测试用例

## 许可证

MIT License
