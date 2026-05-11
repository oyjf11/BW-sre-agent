"""
Mock Services - 测试模拟服务实现

提供各类模拟服务，模拟 OpsPilot Agent 的核心功能:
- MockIntakeService: 模拟工单入口服务
- MockTriageService: 模拟智能分诊服务
- MockInvestigatorService: 模拟证据收集服务
- MockDiagnoseService: 模拟根因分析服务
- MockCriticService: 模拟批判与校验服务
- MockApprovalService: 模拟审批服务
- MockExecutorService: 模拟执行器服务
- MockRCAService: 模拟 RCA 报告服务
- MockKnowledgeService: 模拟知识沉淀服务
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .data import (
    MockIncidentData,
    MockTriageData,
    MockEvidenceData,
    MockRootCauseData,
    MockActionData,
    MockApprovalData,
    MockRCAData,
    KNOWLEDGE_DATA,
)


class ServiceError(Exception):
    """服务异常基类"""
    pass


class ServiceTimeoutError(ServiceError):
    """服务超时异常"""
    pass


class ServiceValidationError(ServiceError):
    """服务验证异常"""
    pass


class ServiceInsufficientDataError(ServiceError):
    """数据不足异常"""
    pass


# ==================== 工单入口服务 ====================

class MockIntakeService:
    """模拟工单入口服务"""
    
    def __init__(self, simulate_error: bool = False):
        self.simulate_error = simulate_error
    
    async def submit_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提交工单
        
        测试场景:
        - 正常流程: 文本工单提交、结构化工单提交、工单 ID 模式
        - 异常流程: 空输入、无效格式、超长输入
        - 边界条件: 多实体抽取、模糊实体识别
        """
        if self.simulate_error:
            raise ServiceError("模拟服务错误")
        
        # 空输入检查
        if not ticket_data.get("description"):
            raise ServiceValidationError("工单内容不能为空")
        
        # 超长输入检查
        if len(ticket_data.get("description", "")) > 10000:
            raise ServiceValidationError("输入内容超过最大长度限制 (10000 字符)")
        
        # 实体抽取
        ticket_data["extracted_entities"] = self._extract_entities(ticket_data)
        
        # 生成标准化工单
        return {
            "status": "success",
            "ticket": ticket_data
        }
    
    def _extract_entities(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟实体抽取"""
        description = ticket_data.get("description", "")
        
        entities = {}
        
        # 服务名抽取
        if "支付" in description or "payment" in description.lower():
            entities["services"] = ["payment-service"]
        if "订单" in description or "order" in description.lower():
            entities["services"] = entities.get("services", []) + ["order-service"]
        
        # 错误码抽取
        if "5xx" in description:
            entities["error_codes"] = ["5xx"]
        if "4xx" in description:
            entities["error_codes"] = ["4xx"]
        
        # 时间范围抽取
        if "分钟" in description:
            entities["time_range"] = "30m"
        
        return entities
    
    async def get_ticket_by_id(self, ticket_id: str) -> Dict[str, Any]:
        """根据 ID 获取工单"""
        if not ticket_id:
            raise ServiceValidationError("工单 ID 不能为空")
        
        # 模拟从数据库获取
        if ticket_id.startswith("INC-"):
            return {
                "status": "success",
                "ticket": {
                    "ticket_id": ticket_id,
                    "title": "模拟工单",
                    "description": "从数据库获取的工单"
                }
            }
        
        raise ServiceValidationError(f"工单 {ticket_id} 不存在")


# ==================== 分诊服务 ====================

class MockTriageService:
    """模拟智能分诊服务"""
    
    def __init__(self, simulate_timeout: bool = False):
        self.simulate_timeout = simulate_timeout
    
    async def triage(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能分诊
        
        测试场景:
        - 正常流程: 错误率分诊、性能分诊、发布回归分诊
        - 异常流程: 信息不足、信息冲突、分诊超时
        - 严重级别: P1/P2/P3/P4 判定
        """
        if self.simulate_timeout:
            raise ServiceTimeoutError("分诊服务超时")
        
        description = ticket_data.get("description", "")
        
        # 信息不足检查
        if len(description) < 10:
            return {
                "status": "insufficient_info",
                "triage": MockTriageData.TRIAGE_INSUFFICIENT_INFO
            }
        
        # 信息冲突检查
        if "正常" in description and ("错误" in description or "失败" in description):
            return {
                "status": "conflicting_info",
                "triage": MockTriageData.TRIAGE_CONFLICTING_INFO
            }
        
        # 错误率分诊
        if "5xx" in description or "错误率" in description:
            triage_result = MockTriageData.TRIAGE_ERROR_RATE.copy()
            triage_result["ticket_id"] = ticket_data.get("ticket_id")
            return {"status": "success", "triage": triage_result}
        
        # 性能分诊
        if "延迟" in description or "性能" in description or "cpu" in description.lower():
            triage_result = MockTriageData.TRIAGE_PERFORMANCE.copy()
            triage_result["ticket_id"] = ticket_data.get("ticket_id")
            return {"status": "success", "triage": triage_result}
        
        # 发布回归分诊
        if "发布" in description and "之后" in description:
            triage_result = MockTriageData.TRIAGE_RELEASE_REGRESSION.copy()
            triage_result["ticket_id"] = ticket_data.get("ticket_id")
            return {"status": "success", "triage": triage_result}
        
        # 默认分诊
        return {"status": "success", "triage": MockTriageData.TRIAGE_P3}
    
    async def determine_severity(self, ticket_data: Dict[str, Any], triage_result: Dict[str, Any]) -> str:
        """判断严重级别"""
        severity = triage_result.get("severity", "P3")
        
        # P1 判定
        if "核心" in ticket_data.get("description", "") and "不可用" in ticket_data.get("description", ""):
            return "P1"
        
        return severity


# ==================== 证据收集服务 ====================

class MockInvestigatorService:
    """模拟证据收集服务"""
    
    def __init__(self, simulate_timeout: bool = False, simulate_failure: bool = False):
        self.simulate_timeout = simulate_timeout
        self.simulate_failure = simulate_failure
        self.concurrent_limit = 5
        self.active_calls = 0
    
    async def collect_evidence(
        self, 
        triage_result: Dict[str, Any],
        investigation_plan: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        并行证据收集
        
        测试场景:
        - 正常流程: 并行收集、证据摘要、来源记录
        - 异常流程: 工具超时、部分失败、证据不足
        - 并发性能: 大数据量、并发限制、响应时间
        """
        if self.simulate_timeout:
            # 模拟部分超时
            return {
                "status": "partial",
                "evidence": [MockEvidenceData.LOGS_EVIDENCE],
                "failed_tools": ["metrics_query"],
                "errors": {"metrics_query": "Query timeout after 30 seconds"}
            }
        
        if self.simulate_failure:
            return {
                "status": "failed",
                "evidence": [],
                "error": "All tools failed"
            }
        
        # 模拟并行收集
        evidence_tasks = [
            self._collect_logs(triage_result),
            self._collect_metrics(triage_result),
            self._collect_deployments(triage_result),
            self._collect_runbooks(triage_result),
        ]
        
        results = await asyncio.gather(*evidence_tasks, return_exceptions=True)
        
        evidence = [r for r in results if not isinstance(r, Exception)]
        
        return {
            "status": "success",
            "evidence": evidence,
            "total_duration_seconds": sum(
                e.get("duration_seconds", 1) for e in evidence if isinstance(e, dict)
            )
        }
    
    async def _collect_logs(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """收集日志"""
        await asyncio.sleep(0.1)  # 模拟延迟
        return MockEvidenceData.LOGS_EVIDENCE.copy()
    
    async def _collect_metrics(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """收集指标"""
        await asyncio.sleep(0.1)
        return MockEvidenceData.METRICS_EVIDENCE.copy()
    
    async def _collect_deployments(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """收集部署记录"""
        await asyncio.sleep(0.1)
        return MockEvidenceData.DEPLOYMENT_EVIDENCE.copy()
    
    async def _collect_runbooks(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """收集 runbook"""
        await asyncio.sleep(0.1)
        return MockEvidenceData.RUNBOOK_EVIDENCE.copy()
    
    async def generate_summary(self, evidence: List[Dict[str, Any]]) -> str:
        """生成证据摘要"""
        summary_parts = []
        for e in evidence:
            summary_parts.append(f"- {e.get('summary', 'No summary')}")
        return "\n".join(summary_parts)


# ==================== 根因分析服务 ====================

class MockDiagnoseService:
    """模拟根因分析服务"""
    
    def __init__(self, simulate_conflict: bool = False, simulate_insufficient: bool = False):
        self.simulate_conflict = simulate_conflict
        self.simulate_insufficient = simulate_insufficient
    
    async def analyze(
        self, 
        evidence: List[Dict[str, Any]], 
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        根因分析
        
        测试场景:
        - 正常流程: 单根因、多根因候选、修复建议
        - 异常流程: 证据冲突、证据不足、新类型问题
        - 风险评估: 低风险、高风险、边界判断
        """
        if self.simulate_insufficient:
            return {
                "status": "insufficient",
                "root_cause_candidates": [MockRootCauseData.INSUFFICIENT_EVIDENCE],
                "confidence": 0.1
            }
        
        if self.simulate_conflict:
            return {
                "status": "conflict",
                "root_cause_candidates": [MockRootCauseData.CONFLICTING_EVIDENCE],
                "confidence": 0.4
            }
        
        # 正常分析
        root_cause = MockRootCauseData.SINGLE_ROOT_CAUSE.copy()
        remediation = MockRootCauseData.REMEDIATION_SUGGESTION.copy()
        
        return {
            "status": "success",
            "root_cause_candidates": [root_cause],
            "remediation": remediation,
            "confidence": 0.85
        }
    
    async def assess_risk_level(self, action: Dict[str, Any]) -> str:
        """评估风险等级"""
        action_type = action.get("action_type", "")
        
        # 低风险动作
        if action_type in ["refresh_cache", "clear_cache"]:
            return "LOW"
        
        # 高风险动作
        if action_type in ["rollback", "delete", "drop"]:
            return "HIGH"
        
        # 中等风险
        if action_type in ["restart", "scale"]:
            return "MEDIUM"
        
        return "MEDIUM"
    
    async def generate_remediation_suggestion(
        self, 
        root_cause: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成修复建议"""
        return MockRootCauseData.REMEDIATION_SUGGESTION.copy()


# ==================== 批判与校验服务 ====================

class MockCriticService:
    """模拟批判与校验服务"""
    
    def __init__(self, simulate_timeout: bool = False):
        self.simulate_timeout = simulate_timeout
        self.max_feedback_loops = 3
    
    async def critique(
        self,
        analysis_result: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批判与校验
        
        测试场景:
        - 正常流程: 推理跳步检测、证据支撑检查、冲突检测
        - 异常流程: Critic 超时、循环反馈
        - 效果评估: 问题检出率、误报率、建议质量
        """
        if self.simulate_timeout:
            # 模拟超时，跳过 Critic
            return {
                "status": "skipped",
                "reason": "timeout"
            }
        
        issues = []
        
        # 检查证据支撑
        if len(evidence) < 2:
            issues.append({
                "type": "insufficient_evidence",
                "severity": "high",
                "message": "证据不足，建议补充更多证据",
                "suggestion": "收集日志、指标等多维度证据"
            })
        
        # 检查置信度
        confidence = analysis_result.get("confidence", 0)
        if confidence > 0.9 and len(evidence) < 3:
            issues.append({
                "type": "high_confidence_low_evidence",
                "severity": "medium",
                "message": "置信度高但证据较少，可能存在推理跳步",
                "suggestion": "补充更多证据验证结论"
            })
        
        if issues:
            return {
                "status": "needs_improvement",
                "issues": issues,
                "can_proceed": False
            }
        
        return {
            "status": "approved",
            "issues": [],
            "can_proceed": True
        }
    
    async def check_reasoning_jump(
        self, 
        conclusion: str, 
        evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """检查推理跳步"""
        # 简化实现
        if not evidence:
            return {
                "has_jump": True,
                "message": "缺乏证据直接得出结论",
                "missing_steps": ["收集证据", "分析证据"]
            }
        
        return {"has_jump": False}


# ==================== 审批服务 ====================

class MockApprovalService:
    """模拟人工审批服务"""
    
    def __init__(
        self, 
        auto_approve: bool = False,
        simulate_timeout: bool = False
    ):
        self.auto_approve = auto_approve
        self.simulate_timeout = simulate_timeout
        self.approvals: Dict[str, Dict[str, Any]] = {}
    
    async def request_approval(
        self, 
        action: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        请求审批
        
        测试场景:
        - 正常流程: 高风险审批、审批通过、审批拒绝、参数修改
        - 异常流程: 审批超时、身份验证
        - 审批策略: 风险分级、环境隔离、审批人配置
        """
        action_id = f"action_{datetime.now().timestamp()}"
        
        if self.auto_approve:
            return {
                "status": "approved",
                "approval_id": f"apr_{action_id}",
                "approver": "auto-system",
                "timestamp": datetime.now()
            }
        
        if self.simulate_timeout:
            return {
                "status": "pending",
                "approval_id": f"apr_{action_id}",
                "timeout_duration_minutes": 30,
                "message": "等待审批中..."
            }
        
        # 存储待审批
        self.approvals[action_id] = {
            "action": action,
            "context": context,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        return {
            "status": "pending",
            "approval_id": f"apr_{action_id}",
            "action_id": action_id
        }
    
    async def approve(
        self, 
        approval_id: str, 
        approver: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """审批通过"""
        return {
            "status": "approved",
            "approval_id": approval_id,
            "approver": approver,
            "comment": comment or "同意执行",
            "timestamp": datetime.now()
        }
    
    async def reject(
        self,
        approval_id: str,
        approver: str,
        reason: str
    ) -> Dict[str, Any]:
        """审批拒绝"""
        return {
            "status": "rejected",
            "approval_id": approval_id,
            "approver": approver,
            "reason": reason,
            "timestamp": datetime.now()
        }
    
    async def modify_and_approve(
        self,
        approval_id: str,
        approver: str,
        modified_params: Dict[str, Any],
        comment: str
    ) -> Dict[str, Any]:
        """修改参数后审批"""
        return {
            "status": "approved_with_modification",
            "approval_id": approval_id,
            "approver": approver,
            "modified_params": modified_params,
            "comment": comment,
            "timestamp": datetime.now()
        }
    
    async def check_timeout(self, approval_id: str) -> bool:
        """检查审批是否超时"""
        if approval_id in self.approvals:
            created_at = self.approvals[approval_id].get("created_at")
            if created_at:
                elapsed = datetime.now() - created_at
                return elapsed > timedelta(minutes=30)
        return False


# ==================== 执行器服务 ====================

class MockExecutorService:
    """模拟执行器服务"""
    
    def __init__(
        self,
        simulate_failure: bool = False,
        simulate_timeout: bool = False
    ):
        self.simulate_failure = simulate_failure
        self.simulate_timeout = simulate_timeout
        self.execution_history: List[Dict[str, Any]] = []
        self.idempotency_store: Dict[str, Dict[str, Any]] = {}
    
    async def execute(
        self, 
        action: Dict[str, Any],
        approved: bool = True
    ) -> Dict[str, Any]:
        """
        执行动作
        
        测试场景:
        - 正常流程: 动作执行、幂等性保障、执行验证
        - 异常流程: 执行失败、执行超时、部分成功
        - 审计日志: 记录完整性、防篡改、可查询
        """
        # 幂等性检查
        idempotency_key = action.get("idempotency_key")
        if idempotency_key and idempotency_key in self.idempotency_store:
            cached = self.idempotency_store[idempotency_key]
            return {
                "status": "idempotent",
                "action_id": cached["action_id"],
                "result": cached["result"],
                "message": "相同动作已在执行中，返回现有结果"
            }
        
        action_id = f"act_{datetime.now().timestamp()}"
        
        if self.simulate_failure:
            result = {
                "status": "failed",
                "action_id": action_id,
                "error": "服务启动失败",
                "duration_seconds": 60,
                "compensation_plan": "执行回滚到上一版本"
            }
        elif self.simulate_timeout:
            result = {
                "status": "timeout",
                "action_id": action_id,
                "duration_seconds": 120,
                "error": "执行超过 60 秒超时"
            }
        else:
            result = {
                "status": "success",
                "action_id": action_id,
                "action_type": action.get("action_type"),
                "service": action.get("service"),
                "duration_seconds": 30,
                "output": "执行成功"
            }
        
        # 记录审计日志
        audit_log = {
            "action_id": action_id,
            "action": action,
            "result": result,
            "timestamp": datetime.now(),
            "idempotency_key": idempotency_key
        }
        self.execution_history.append(audit_log)
        
        # 存储幂等结果
        if idempotency_key:
            self.idempotency_store[idempotency_key] = {
                "action_id": action_id,
                "result": result
            }
        
        return result
    
    async def verify_execution(self, action_id: str) -> Dict[str, Any]:
        """验证执行结果"""
        for log in self.execution_history:
            if log["action_id"] == action_id:
                return {
                    "verified": True,
                    "result": log["result"]
                }
        
        return {"verified": False}
    
    def get_audit_logs(
        self,
        action_id: Optional[str] = None,
        action_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查询审计日志"""
        logs = self.execution_history
        
        if action_id:
            logs = [l for l in logs if l["action_id"] == action_id]
        
        if action_type:
            logs = [l for l in logs if l["action"].get("action_type") == action_type]
        
        return logs


# ==================== RCA 报告服务 ====================

class MockRCAService:
    """模拟 RCA 报告服务"""
    
    def __init__(self):
        self.rcas: Dict[str, Dict[str, Any]] = {}
    
    async def generate_rca(
        self,
        ticket_data: Dict[str, Any],
        triage_result: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        analysis_result: Dict[str, Any],
        execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成 RCA 报告
        
        测试场景:
        - 正常流程: 完整报告、时间线、证据引用
        - 异常流程: 部分数据缺失、格式定制
        - 质量评估: 完整性、可读性、可操作性
        """
        rca_id = f"RCA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 检查是否完整
        if not execution_result:
            return {
                "status": "incomplete",
                "rca_id": rca_id,
                "message": "缺少执行结果数据，报告不完整",
                "missing_data": ["execution_result"]
            }
        
        rca = {
            "rca_id": rca_id,
            "incident_id": ticket_data.get("ticket_id"),
            "title": ticket_data.get("title"),
            "summary": analysis_result.get("summary", "分析完成"),
            
            "timeline": [
                {
                    "phase": "detection",
                    "timestamp": datetime.now() - timedelta(minutes=30),
                    "description": "检测到异常"
                },
                {
                    "phase": "diagnosis",
                    "timestamp": datetime.now() - timedelta(minutes=25),
                    "description": "开始诊断分析"
                },
                {
                    "phase": "execution",
                    "timestamp": datetime.now() - timedelta(minutes=10),
                    "description": "执行修复动作"
                },
                {
                    "phase": "recovery",
                    "timestamp": datetime.now() - timedelta(minutes=5),
                    "description": "服务恢复"
                }
            ],
            
            "root_cause": analysis_result.get("root_cause_candidates", [{}])[0],
            
            "actions_taken": [execution_result],
            
            "impact_scope": {
                "services_affected": [ticket_data.get("service")],
                "severity": triage_result.get("severity")
            },
            
            "action_items": [
                {
                    "description": "添加监控告警",
                    "owner": "sre-team",
                    "status": "pending"
                }
            ],
            
            "created_at": datetime.now(),
            "confirmed": False
        }
        
        self.rcas[rca_id] = rca
        
        return {"status": "success", "rca": rca}
    
    async def get_rca(self, rca_id: str) -> Optional[Dict[str, Any]]:
        """获取 RCA 报告"""
        return self.rcas.get(rca_id)
    
    async def confirm_rca(self, rca_id: str, confirmed_by: str) -> Dict[str, Any]:
        """确认 RCA 报告"""
        if rca_id in self.rcas:
            self.rcas[rca_id]["confirmed"] = True
            self.rcas[rca_id]["confirmed_by"] = confirmed_by
            self.rcas[rca_id]["confirmed_at"] = datetime.now()
            
            return {"status": "confirmed", "rca_id": rca_id}
        
        return {"status": "error", "message": "RCA not found"}


# ==================== 知识沉淀服务 ====================

class MockKnowledgeService:
    """模拟知识沉淀服务"""
    
    def __init__(self):
        self.knowledge_base: List[Dict[str, Any]] = []
        # 初始化历史数据
        self.knowledge_base.extend(KNOWLEDGE_DATA["historical_rcas"])
    
    async def write_knowledge(
        self,
        rca_data: Dict[str, Any],
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        写入知识库
        
        测试场景:
        - 正常流程: 知识写入、知识检索、知识更新
        - 异常流程: 未经确认不写入、区分已验证与假设
        """
        if not confirmed:
            # 未经确认不写入
            return {
                "status": "skipped",
                "reason": "未确认的推断不会写入知识库"
            }
        
        knowledge_entry = {
            "id": f"kb_{len(self.knowledge_base)}",
            "rca_id": rca_data.get("rca_id"),
            "incident_type": rca_data.get("incident_type"),
            "service": rca_data.get("service"),
            "root_cause": rca_data.get("root_cause"),
            "solution": rca_data.get("solution"),
            "confirmed": True,
            "created_at": datetime.now()
        }
        
        self.knowledge_base.append(knowledge_entry)
        
        return {
            "status": "success",
            "knowledge_id": knowledge_entry["id"]
        }
    
    async def retrieve_knowledge(
        self,
        query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        检索知识
        
        测试场景:
        - 正常流程: 知识检索
        - 异常流程: 检索降级
        """
        service = query.get("service")
        incident_type = query.get("incident_type")
        
        results = []
        
        for kb in self.knowledge_base:
            match = True
            
            if service and kb.get("service") != service:
                match = False
            if incident_type and kb.get("incident_type") != incident_type:
                match = False
            
            if match:
                results.append(kb)
        
        # 如果没有本地结果，返回默认结果
        if not results and KNOWLEDGE_DATA.get("historical_rcas"):
            results = KNOWLEDGE_DATA["historical_rcas"][:2]
        
        return results
    
    async def update_knowledge(
        self,
        knowledge_id: str,
        updated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新知识"""
        for kb in self.knowledge_base:
            if str(kb.get("id")) == str(knowledge_id):
                kb.update(updated_data)
                kb["updated_at"] = datetime.now()
                return {"status": "success", "knowledge": kb}
        
        return {"status": "error", "message": "Knowledge not found"}


# ==================== 编排服务 - 完整工作流 ====================

class MockWorkflowService:
    """模拟完整工作流服务"""
    
    def __init__(self):
        self.intake = MockIntakeService()
        self.triage = MockTriageService()
        self.investigator = MockInvestigatorService()
        self.diagnose = MockDiagnoseService()
        self.critic = MockCriticService()
        self.approval = MockApprovalService(auto_approve=True)
        self.executor = MockExecutorService()
        self.rca = MockRCAService()
        self.knowledge = MockKnowledgeService()
    
    async def run_full_workflow(
        self,
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行完整工作流"""
        results = {}
        
        # 1. 工单入口
        intake_result = await self.intake.submit_ticket(ticket_data)
        results["intake"] = intake_result
        
        # 2. 智能分诊
        triage_result = await self.triage.triage(ticket_data)
        results["triage"] = triage_result
        
        # 3. 证据收集
        evidence_result = await self.investigator.collect_evidence(
            triage_result.get("triage", {}),
            []
        )
        results["evidence"] = evidence_result
        
        # 4. 根因分析
        diagnose_result = await self.diagnose.analyze(
            evidence_result.get("evidence", []),
            ticket_data
        )
        results["diagnose"] = diagnose_result
        
        # 5. 批判校验
        critic_result = await self.critic.critique(
            diagnose_result,
            evidence_result.get("evidence", [])
        )
        results["critic"] = critic_result
        
        # 6. 审批（如需要）
        action = diagnose_result.get("remediation", {})
        if action.get("requires_approval"):
            approval_result = await self.approval.request_approval(action, {})
            results["approval"] = approval_result
        
        # 7. 执行
        if action:
            execution_result = await self.executor.execute(action)
            results["execution"] = execution_result
        else:
            execution_result = None
        
        # 8. RCA 报告
        rca_result = await self.rca.generate_rca(
            ticket_data,
            triage_result.get("triage", {}),
            evidence_result.get("evidence", []),
            diagnose_result,
            execution_result
        )
        results["rca"] = rca_result
        
        return results
