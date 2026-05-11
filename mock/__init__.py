"""
OpsPilot Mock Services - 测试模拟服务

提供用于测试的模拟服务，模拟以下功能:
- 模拟工单入口
- 模拟智能分诊
- 模拟证据收集
- 模拟根因分析
- 模拟审批流程
- 模拟执行器
- 模拟 RCA 报告生成
"""

from .data import (
    MockIncidentData,
    MockTriageData,
    MockEvidenceData,
    MockRootCauseData,
    MockActionData,
    MockApprovalData,
    MockRCAData,
)
from .services import (
    MockIntakeService,
    MockTriageService,
    MockInvestigatorService,
    MockDiagnoseService,
    MockCriticService,
    MockApprovalService,
    MockExecutorService,
    MockRCAService,
    MockKnowledgeService,
)

__all__ = [
    # Data
    "MockIncidentData",
    "MockTriageData",
    "MockEvidenceData",
    "MockRootCauseData",
    "MockActionData",
    "MockApprovalData",
    "MockRCAData",
    # Services
    "MockIntakeService",
    "MockTriageService",
    "MockInvestigatorService",
    "MockDiagnoseService",
    "MockCriticService",
    "MockApprovalService",
    "MockExecutorService",
    "MockRCAService",
    "MockKnowledgeService",
]
