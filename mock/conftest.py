"""
Mock Services Pytest Fixtures

提供 pytest fixtures 用于测试
"""

import pytest
import asyncio
from typing import Generator

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
    MockWorkflowService,
)
from .data import (
    MockIncidentData,
    MockTriageData,
    MockEvidenceData,
    MockRootCauseData,
    MockActionData,
    MockApprovalData,
    MockRCAData,
)


@pytest.fixture
def event_loop():
    """事件循环 fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Service Fixtures ====================

@pytest.fixture
def mock_intake_service() -> MockIntakeService:
    """工单入口服务 fixture"""
    return MockIntakeService()


@pytest.fixture
def mock_triage_service() -> MockTriageService:
    """分诊服务 fixture"""
    return MockTriageService()


@pytest.fixture
def mock_investigator_service() -> MockInvestigatorService:
    """证据收集服务 fixture"""
    return MockInvestigatorService()


@pytest.fixture
def mock_diagnose_service() -> MockDiagnoseService:
    """根因分析服务 fixture"""
    return MockDiagnoseService()


@pytest.fixture
def mock_critic_service() -> MockCriticService:
    """批判校验服务 fixture"""
    return MockCriticService()


@pytest.fixture
def mock_approval_service() -> MockApprovalService:
    """审批服务 fixture"""
    return MockApprovalService(auto_approve=False)


@pytest.fixture
def mock_executor_service() -> MockExecutorService:
    """执行器服务 fixture"""
    return MockExecutorService()


@pytest.fixture
def mock_rca_service() -> MockRCAService:
    """RCA 服务 fixture"""
    return MockRCAService()


@pytest.fixture
def mock_knowledge_service() -> MockKnowledgeService:
    """知识服务 fixture"""
    return MockKnowledgeService()


@pytest.fixture
def mock_workflow_service() -> MockWorkflowService:
    """完整工作流服务 fixture"""
    return MockWorkflowService()


# ==================== Data Fixtures ====================

@pytest.fixture
def sample_ticket() -> dict:
    """示例工单 fixture"""
    return MockIncidentData.TEXT_INCIDENT_NORMAL


@pytest.fixture
def sample_triage() -> dict:
    """示例分诊结果 fixture"""
    return MockTriageData.TRIAGE_ERROR_RATE


@pytest.fixture
def sample_evidence() -> list:
    """示例证据 fixture"""
    return [MockEvidenceData.LOGS_EVIDENCE, MockEvidenceData.METRICS_EVIDENCE]


@pytest.fixture
def sample_root_cause() -> dict:
    """示例根因 fixture"""
    return MockRootCauseData.SINGLE_ROOT_CAUSE


@pytest.fixture
def sample_action() -> dict:
    """示例动作 fixture"""
    return MockRootCauseData.REMEDIATION_SUGGESTION


@pytest.fixture
def sample_approval() -> dict:
    """示例审批 fixture"""
    return MockApprovalData.APPROVAL_APPROVED


@pytest.fixture
def sample_rca() -> dict:
    """示例 RCA fixture"""
    return MockRCAData.RCA_COMPLETE


# ==================== Error Scenario Fixtures ====================

@pytest.fixture
def mock_intake_error() -> MockIntakeService:
    """错误场景 - 工单入口服务"""
    return MockIntakeService(simulate_error=True)


@pytest.fixture
def mock_triage_timeout() -> MockTriageService:
    """错误场景 - 分诊服务超时"""
    return MockTriageService(simulate_timeout=True)


@pytest.fixture
def mock_investigator_timeout() -> MockInvestigatorService:
    """错误场景 - 证据收集服务超时"""
    return MockInvestigatorService(simulate_timeout=True)


@pytest.fixture
def mock_investigator_failure() -> MockInvestigatorService:
    """错误场景 - 证据收集服务失败"""
    return MockInvestigatorService(simulate_failure=True)


@pytest.fixture
def mock_diagnose_conflict() -> MockDiagnoseService:
    """错误场景 - 根因分析证据冲突"""
    return MockDiagnoseService(simulate_conflict=True)


@pytest.fixture
def mock_diagnose_insufficient() -> MockDiagnoseService:
    """错误场景 - 根因分析证据不足"""
    return MockDiagnoseService(simulate_insufficient=True)


@pytest.fixture
def mock_critic_timeout() -> MockCriticService:
    """错误场景 - Critic 服务超时"""
    return MockCriticService(simulate_timeout=True)


@pytest.fixture
def mock_executor_failure() -> MockExecutorService:
    """错误场景 - 执行器失败"""
    return MockExecutorService(simulate_failure=True)


@pytest.fixture
def mock_executor_timeout() -> MockExecutorService:
    """错误场景 - 执行器超时"""
    return MockExecutorService(simulate_timeout=True)


# ==================== All Test Data ====================

@pytest.fixture
def all_incidents() -> list:
    """所有测试工单数据"""
    return MockIncidentData.get_all_incidents()


@pytest.fixture
def all_triages() -> list:
    """所有测试分诊数据"""
    return MockTriageData.get_all_triages()


@pytest.fixture
def all_evidence() -> list:
    """所有测试证据数据"""
    return MockEvidenceData.get_all_evidence()


@pytest.fixture
def all_root_causes() -> list:
    """所有测试根因数据"""
    return MockRootCauseData.get_all_root_causes()


@pytest.fixture
def all_actions() -> list:
    """所有测试动作数据"""
    return MockActionData.get_all_actions()


@pytest.fixture
def all_rcas() -> list:
    """所有测试 RCA 数据"""
    return MockRCAData.get_all_rcas()
