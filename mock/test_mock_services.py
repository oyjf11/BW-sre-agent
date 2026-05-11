"""
Mock Services Tests - 测试用例示例

展示如何使用 Mock Services 进行测试
"""

import pytest
import asyncio

from mock.services import (
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
    ServiceValidationError,
    ServiceTimeoutError,
)
from mock.data import (
    MockIncidentData,
    MockTriageData,
    MockEvidenceData,
    MockRootCauseData,
)


# ==================== 工单入口测试 ====================

class TestMockIntakeService:
    """工单入口服务测试"""
    
    @pytest.mark.asyncio
    async def test_submit_ticket_normal(self):
        """测试正常工单提交"""
        service = MockIntakeService()
        ticket_data = MockIncidentData.TEXT_INCIDENT_NORMAL
        
        result = await service.submit_ticket(ticket_data)
        
        assert result["status"] == "success"
        assert "ticket" in result
    
    @pytest.mark.asyncio
    async def test_submit_ticket_empty(self):
        """测试空输入 - 应抛出验证错误"""
        service = MockIntakeService()
        ticket_data = {"description": ""}
        
        with pytest.raises(ServiceValidationError, match="不能为空"):
            await service.submit_ticket(ticket_data)
    
    @pytest.mark.asyncio
    async def test_submit_ticket_too_long(self):
        """测试超长输入 - 应抛出验证错误"""
        service = MockIntakeService()
        ticket_data = {"description": "a" * 10001}
        
        with pytest.raises(ServiceValidationError, match="超过最大长度"):
            await service.submit_ticket(ticket_data)
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self):
        """测试实体抽取"""
        service = MockIntakeService()
        ticket_data = {
            "description": "支付服务 5xx 错误率飙升",
            "service": "payment-service"
        }
        
        result = await service.submit_ticket(ticket_data)
        
        assert "extracted_entities" in result["ticket"]
        assert "services" in result["ticket"]["extracted_entities"]


# ==================== 分诊服务测试 ====================

class TestMockTriageService:
    """分诊服务测试"""
    
    @pytest.mark.asyncio
    async def test_triage_error_rate(self):
        """测试错误率分诊"""
        service = MockTriageService()
        ticket_data = {"description": "支付服务 5xx 错误率飙升到 20%"}
        
        result = await service.triage(ticket_data)
        
        assert result["status"] == "success"
        assert result["triage"]["incident_type"] == "error_rate"
    
    @pytest.mark.asyncio
    async def test_triage_performance(self):
        """测试性能分诊"""
        service = MockTriageService()
        ticket_data = {"description": "订单服务 p95 延迟从 200ms 增加到 3000ms"}
        
        result = await service.triage(ticket_data)
        
        assert result["status"] == "success"
        assert result["triage"]["incident_type"] == "performance"
    
    @pytest.mark.asyncio
    async def test_triage_release_regression(self):
        """测试发布回归分诊"""
        service = MockTriageService()
        ticket_data = {"description": "今天 14:00 发布了订单服务 v2.1.0，之后用户反馈页面加载失败"}
        
        result = await service.triage(ticket_data)
        
        assert result["status"] == "success"
        assert result["triage"]["incident_type"] == "release_regression"
    
    @pytest.mark.asyncio
    async def test_triage_insufficient_info(self):
        """测试信息不足"""
        service = MockTriageService()
        ticket_data = {"description": "服务出问题了"}
        
        result = await service.triage(ticket_data)
        
        assert result["status"] == "insufficient_info"
    
    @pytest.mark.asyncio
    async def test_triage_conflicting_info(self):
        """测试信息冲突"""
        service = MockTriageService()
        ticket_data = {"description": "错误率很高但是服务运行正常"}
        
        result = await service.triage(ticket_data)
        
        assert result["status"] == "conflicting_info"
    
    @pytest.mark.asyncio
    async def test_triage_timeout(self):
        """测试分诊超时"""
        service = MockTriageService(simulate_timeout=True)
        
        with pytest.raises(ServiceTimeoutError):
            await service.triage({"description": "测试超时"})


# ==================== 证据收集服务测试 ====================

class TestMockInvestigatorService:
    """证据收集服务测试"""
    
    @pytest.mark.asyncio
    async def test_collect_evidence_normal(self):
        """测试正常证据收集"""
        service = MockInvestigatorService()
        triage_result = MockTriageData.TRIAGE_ERROR_RATE
        
        result = await service.collect_evidence(triage_result, [])
        
        assert result["status"] == "success"
        assert len(result["evidence"]) > 0
    
    @pytest.mark.asyncio
    async def test_collect_evidence_partial_timeout(self):
        """测试部分超时"""
        service = MockInvestigatorService(simulate_timeout=True)
        triage_result = MockTriageData.TRIAGE_ERROR_RATE
        
        result = await service.collect_evidence(triage_result, [])
        
        assert result["status"] == "partial"
        assert "failed_tools" in result
    
    @pytest.mark.asyncio
    async def test_parallel_collection(self):
        """测试并行收集"""
        service = MockInvestigatorService()
        triage_result = MockTriageData.TRIAGE_ERROR_RATE
        
        import time
        start = time.time()
        result = await service.collect_evidence(triage_result, [])
        duration = time.time() - start
        
        # 并行执行应该比串行快
        assert duration < 0.5  # 4个任务串行需要 0.4s，并行应该更快


# ==================== 根因分析服务测试 ====================

class TestMockDiagnoseService:
    """根因分析服务测试"""
    
    @pytest.mark.asyncio
    async def test_analyze_normal(self):
        """测试正常分析"""
        service = MockDiagnoseService()
        evidence = [MockEvidenceData.LOGS_EVIDENCE, MockEvidenceData.METRICS_EVIDENCE]
        
        result = await service.analyze(evidence, {})
        
        assert result["status"] == "success"
        assert "root_cause_candidates" in result
        assert "remediation" in result
    
    @pytest.mark.asyncio
    async def test_analyze_conflict(self):
        """测试证据冲突"""
        service = MockDiagnoseService(simulate_conflict=True)
        
        result = await service.analyze([], {})
        
        assert result["status"] == "conflict"
    
    @pytest.mark.asyncio
    async def test_analyze_insufficient(self):
        """测试证据不足"""
        service = MockDiagnoseService(simulate_insufficient=True)
        
        result = await service.analyze([], {})
        
        assert result["status"] == "insufficient"
    
    @pytest.mark.asyncio
    async def test_assess_risk_level(self):
        """测试风险等级评估"""
        service = MockDiagnoseService()
        
        # 低风险
        action = {"action_type": "refresh_cache"}
        risk = await service.assess_risk_level(action)
        assert risk == "LOW"
        
        # 高风险
        action = {"action_type": "rollback"}
        risk = await service.assess_risk_level(action)
        assert risk == "HIGH"
        
        # 中等风险
        action = {"action_type        risk = await service.assess": "restart"}
_risk_level(action)
        assert risk == "MEDIUM"


# ==================== 批判校验服务测试 ====================

class TestMockCriticService:
    """批判校验服务测试"""
    
    @pytest.mark.asyncio
    async def test_critique_normal(self):
        """测试正常批判"""
        service = MockCriticService()
        analysis_result = {"confidence": 0.85}
        evidence = [
            MockEvidenceData.LOGS_EVIDENCE,
            MockEvidenceData.METRICS_EVIDENCE,
            MockEvidenceData.DEPLOYMENT_EVIDENCE
        ]
        
        result = await service.critique(analysis_result, evidence)
        
        assert result["can_proceed"] is True
        assert result["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_critique_insufficient_evidence(self):
        """测试证据不足"""
        service = MockCriticService()
        analysis_result = {"confidence": 0.8}
        evidence = [MockEvidenceData.LOGS_EVIDENCE]  # 只有一条证据
        
        result = await service.critique(analysis_result, evidence)
        
        assert result["can_proceed"] is False
        assert len(result["issues"]) > 0
    
    @pytest.mark.asyncio
    async def test_critique_timeout(self):
        """测试超时"""
        service = MockCriticService(simulate_timeout=True)
        
        result = await service.critique({}, [])
        
        assert result["status"] == "skipped"


# ==================== 审批服务测试 ====================

class TestMockApprovalService:
    """审批服务测试"""
    
    @pytest.mark.asyncio
    async def test_request_approval(self):
        """测试请求审批"""
        service = MockApprovalService(auto_approve=False)
        action = {"action_type": "rollback", "risk_level": "HIGH"}
        
        result = await service.request_approval(action, {})
        
        assert result["status"] == "pending"
        assert "approval_id" in result
    
    @pytest.mark.asyncio
    async def test_auto_approve(self):
        """测试自动审批"""
        service = MockApprovalService(auto_approve=True)
        action = {"action_type": "restart"}
        
        result = await service.request_approval(action, {})
        
        assert result["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_approve(self):
        """测试审批通过"""
        service = MockApprovalService()
        
        result = await service.approve("apr_001", "admin@example.com")
        
        assert result["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_reject(self):
        """测试审批拒绝"""
        service = MockApprovalService()
        
        result = await service.reject("apr_001", "admin@example.com", "风险太高")
        
        assert result["status"] == "rejected"
    
    @pytest.mark.asyncio
    async def test_modify_and_approve(self):
        """测试修改参数后审批"""
        service = MockApprovalService()
        
        result = await service.modify_and_approve(
            "apr_001",
            "admin@example.com",
            {"restart_strategy": "blue_green"},
            "建议使用蓝绿部署"
        )
        
        assert result["status"] == "approved_with_modification"


# ==================== 执行器服务测试 ====================

class TestMockExecutorService:
    """执行器服务测试"""
    
    @pytest.mark.asyncio
    async def test_execute_normal(self):
        """测试正常执行"""
        service = MockExecutorService()
        action = {"action_type": "restart", "service": "payment-service"}
        
        result = await service.execute(action)
        
        assert result["status"] == "success"
        assert "action_id" in result
    
    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """测试执行失败"""
        service = MockExecutorService(simulate_failure=True)
        
        result = await service.execute({"action_type": "restart"})
        
        assert result["status"] == "failed"
        assert "compensation_plan" in result
    
    @pytest.mark.asyncio
    async def test_execute_timeout(self):
        """测试执行超时"""
        service = MockExecutorService(simulate_timeout=True)
        
        result = await service.execute({"action_type": "restart"})
        
        assert result["status"] == "timeout"
    
    @pytest.mark.asyncio
    async def test_idempotency(self):
        """测试幂等性"""
        service = MockExecutorService()
        action = {
            "action_type": "restart",
            "idempotency_key": "test_key_001"
        }
        
        # 第一次执行
        result1 = await service.execute(action)
        # 第二次执行（相同 key）
        result2 = await service.execute(action)
        
        assert result1["status"] == "success"
        assert result2["status"] == "idempotent"
    
    @pytest.mark.asyncio
    async def test_audit_logs(self):
        """测试审计日志"""
        service = MockExecutorService()
        
        await service.execute({"action_type": "restart", "service": "test"})
        logs = service.get_audit_logs()
        
        assert len(logs) > 0


# ==================== RCA 服务测试 ====================

class TestMockRCAService:
    """RCA 服务测试"""
    
    @pytest.mark.asyncio
    async def test_generate_rca_normal(self):
        """测试正常生成 RCA"""
        service = MockRCAService()
        
        result = await service.generate_rca(
            ticket_data={"ticket_id": "INC-001", "title": "Test"},
            triage_result={"severity": "P1"},
            evidence=[MockEvidenceData.LOGS_EVIDENCE],
            analysis_result={"root_cause_candidates": [MockRootCauseData.SINGLE_ROOT_CAUSE]},
            execution_result={"status": "success"}
        )
        
        assert result["status"] == "success"
        assert "rca" in result
    
    @pytest.mark.asyncio
    async def test_generate_rca_incomplete(self):
        """测试不完整 RCA"""
        service = MockRCAService()
        
        result = await service.generate_rca(
            ticket_data={"ticket_id": "INC-001"},
            triage_result={},
            evidence=[],
            analysis_result={},
            execution_result=None  # 缺少执行结果
        )
        
        assert result["status"] == "incomplete"


# ==================== 知识服务测试 ====================

class TestMockKnowledgeService:
    """知识服务测试"""
    
    @pytest.mark.asyncio
    async def test_write_knowledge_confirmed(self):
        """测试写入已确认知识"""
        service = MockKnowledgeService()
        
        result = await service.write_knowledge(
            rca_data={"rca_id": "RCA-001", "service": "test"},
            confirmed=True
        )
        
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_write_knowledge_unconfirmed(self):
        """测试不写入未确认知识"""
        service = MockKnowledgeService()
        
        result = await service.write_knowledge(
            rca_data={"rca_id": "RCA-002"},
            confirmed=False
        )
        
        assert result["status"] == "skipped"
    
    @pytest.mark.asyncio
    async def test_retrieve_knowledge(self):
        """测试检索知识"""
        service = MockKnowledgeService()
        
        results = await service.retrieve_knowledge(
            query={"service": "payment-service"}
        )
        
        assert isinstance(results, list)


# ==================== 完整工作流测试 ====================

class TestMockWorkflowService:
    """完整工作流测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流"""
        service = MockWorkflowService()
        ticket_data = MockIncidentData.TEXT_INCIDENT_NORMAL
        
        result = await service.run_full_workflow(ticket_data)
        
        assert "intake" in result
        assert "triage" in result
        assert "evidence" in result
        assert "diagnose" in result
        assert "critic" in result
        assert "rca" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_approval(self):
        """测试需要审批的工作流"""
        service = MockWorkflowService()
        service.approval = MockApprovalService(auto_approve=False)
        
        # 高风险动作需要审批
        ticket_data = {
            "ticket_id": "INC-TEST",
            "description": "支付服务故障，需要回滚版本"
        }
        
        result = await service.run_full_workflow(ticket_data)
        
        # 应该有审批步骤
        assert "approval" in result
