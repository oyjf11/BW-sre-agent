"""
Mock Data - 测试模拟数据

提供各类测试场景的模拟数据，包括:
- 工单数据
- 分诊结果
- 证据数据
- 根因候选
- 动作数据
- 审批数据
- RCA 报告数据
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


# ==================== 工单数据 ====================

@dataclass
class MockIncidentData:
    """模拟工单数据"""
    
    # 正常流程测试数据 - 文本工单
    TEXT_INCIDENT_NORMAL = {
        "ticket_id": "INC-2024-0015",
        "title": "支付服务 5xx 错误率飙升",
        "description": "支付服务 5xx 错误率从 1% 飙升到 20%，影响所有用户下单",
        "service": "payment-service",
        "env": "production",
        "severity": "P1",
        "source": "alertmanager",
        "time_range": {
            "start": datetime.now() - timedelta(minutes=30),
            "end": datetime.now()
        },
        "metadata": {
            "error_code": "5xx",
            "error_rate": "20%",
            "impact_scope": "所有用户"
        }
    }
    
    # 正常流程测试数据 - 结构化工单
    STRUCTURED_INCIDENT_NORMAL = {
        "ticket_id": "INC-2024-0016",
        "title": "订单服务延迟增加",
        "description": "订单服务 p95 延迟从 200ms 增加到 3000ms",
        "service": "order-service",
        "env": "production",
        "severity": "P2",
        "source": "manual",
        "time_range": {
            "start": datetime.now() - timedelta(hours=1),
            "end": datetime.now()
        },
        "metadata": {
            "p95_latency": "3000ms",
            "baseline_latency": "200ms"
        }
    }
    
    # 正常流程测试数据 - 发布回归
    RELEASE_REGRESSION_INCIDENT = {
        "ticket_id": "INC-2024-0017",
        "title": "发布后页面加载失败",
        "description": "今天 14:00 发布了订单服务 v2.1.0，之后用户反馈页面加载失败",
        "service": "order-service",
        "env": "production",
        "severity": "P1",
        "source": "manual",
        "time_range": {
            "start": datetime(2024, 1, 15, 14, 0),
            "end": datetime(2024, 1, 15, 14, 30)
        },
        "metadata": {
            "release_version": "v2.1.0",
            "release_time": "2024-01-15 14:00"
        }
    }
    
    # 异常流程测试数据 - 空输入
    INCIDENT_EMPTY = {
        "ticket_id": "",
        "title": "",
        "description": "",
        "service": "",
        "env": "",
        "severity": "",
        "source": "manual"
    }
    
    # 异常流程测试数据 - 无效格式
    INCIDENT_INVALID = {
        "ticket_id": "INC-2024-0018",
        "title": "hello world",
        "description": "hello world",
        "service": "",
        "env": "",
        "severity": "",
        "source": "manual"
    }
    
    # 异常流程测试数据 - 超长输入
    @staticmethod
    def get_long_textincident() -> Dict[str, Any]:
        return {
            "ticket_id": "INC-2024-0019",
            "title": "测试超长输入",
            "description": "a" * 10001,
            "service": "test-service",
            "env": "test",
            "severity": "P4",
            "source": "manual"
        }
    
    # 边界条件测试数据 - 多实体
    MULTI_ENTITY_INCIDENT = {
        "ticket_id": "INC-2024-0020",
        "title": "多服务异常",
        "description": "支付服务和订单服务同时出现 5xx 错误，用户服务和商品服务也受影响",
        "service": "payment-service,order-service,user-service,product-service",
        "env": "production",
        "severity": "P1",
        "source": "alertmanager",
        "metadata": {
            "affected_services": [
                "payment-service",
                "order-service",
                "user-service",
                "product-service"
            ]
        }
    }
    
    # 性能类工单
    PERFORMANCE_INCIDENT_CPU = {
        "ticket_id": "INC-2024-0021",
        "title": "数据库服务器 CPU 打满",
        "description": "数据库服务器 CPU 使用率持续 100%，影响所有依赖数据库的服务",
        "service": "mysql-primary",
        "env": "production",
        "severity": "P1",
        "source": "alertmanager",
        "metadata": {
            "cpu_usage": "100%",
            "baseline_usage": "30%"
        }
    }
    
    @staticmethod
    def get_all_incidents() -> List[Dict[str, Any]]:
        """获取所有测试工单"""
        return [
            MockIncidentData.TEXT_INCIDENT_NORMAL,
            MockIncidentData.STRUCTURED_INCIDENT_NORMAL,
            MockIncidentData.RELEASE_REGRESSION_INCIDENT,
            MockIncidentData.PERFORMANCE_INCIDENT_CPU,
            MockIncidentData.MULTI_ENTITY_INCIDENT,
        ]


# ==================== 分诊数据 ====================

@dataclass
class MockTriageData:
    """模拟分诊结果数据"""
    
    # 正常流程 - 错误率分诊
    TRIAGE_ERROR_RATE = {
        "incident_type": "error_rate",
        "severity": "P1",
        "suspected_services": ["payment-service", "payment-gateway"],
        "suggested_time_window": {
            "start": datetime.now() - timedelta(minutes=30),
            "end": datetime.now()
        },
        "requires_immediate_human": False,
        "rationale": "错误率超过 20% 且影响核心服务，需要立即处理"
    }
    
    # 正常流程 - 性能分诊
    TRIAGE_PERFORMANCE = {
        "incident_type": "performance",
        "severity": "P2",
        "suspected_services": ["order-service"],
        "suggested_time_window": {
            "start": datetime.now() - timedelta(hours=1),
            "end": datetime.now()
        },
        "requires_immediate_human": False,
        "rationale": "延迟增加严重但未完全不可用"
    }
    
    # 正常流程 - 发布回归分诊
    TRIAGE_RELEASE_REGRESSION = {
        "incident_type": "release_regression",
        "severity": "P1",
        "suspected_services": ["order-service"],
        "suggested_time_window": {
            "start": datetime(2024, 1, 15, 13, 30),
            "end": datetime(2024, 1, 15, 14, 30)
        },
        "requires_immediate_human": False,
        "rationale": "发布后立即出现故障，强烈怀疑发布变更导致"
    }
    
    # 异常流程 - 信息不足
    TRIAGE_INSUFFICIENT_INFO = {
        "incident_type": "unknown",
        "severity": "P3",
        "suspected_services": [],
        "suggested_time_window": None,
        "requires_immediate_human": True,
        "rationale": "输入信息不足，无法判断事件类型，需要补充更多信息",
        "insufficient_info": True,
        "missing_fields": ["service", "error_code", "time_range"]
    }
    
    # 异常流程 - 信息冲突
    TRIAGE_CONFLICTING_INFO = {
        "incident_type": "unknown",
        "severity": "P2",
        "suspected_services": [],
        "suggested_time_window": None,
        "requires_immediate_human": True,
        "rationale": "输入信息存在冲突，需要人工确认",
        "conflicting_info": True,
        "conflicts": ["错误率很高 vs 服务运行正常"]
    }
    
    # P1 级别判定
    TRIAGE_P1 = {
        "incident_type": "error_rate",
        "severity": "P1",
        "suspected_services": ["payment-service"],
        "requires_immediate_human": True,
        "rationale": "核心支付服务完全不可用，错误率超过 50%，影响所有用户"
    }
    
    # P2 级别判定
    TRIAGE_P2 = {
        "incident_type": "performance",
        "severity": "P2",
        "suspected_services": ["order-service"],
        "requires_immediate_human": False,
        "rationale": "非核心服务响应变慢，错误率 10-20%，部分用户受影响"
    }
    
    # P3/P4 级别判定
    TRIAGE_P3 = {
        "incident_type": "performance",
        "severity": "P3",
        "suspected_services": ["test-service"],
        "requires_immediate_human": False,
        "rationale": "内部测试环境的轻微异常"
    }
    
    @staticmethod
    def get_all_triages() -> List[Dict[str, Any]]:
        return [
            MockTriageData.TRIAGE_ERROR_RATE,
            MockTriageData.TRIAGE_PERFORMANCE,
            MockTriageData.TRIAGE_RELEASE_REGRESSION,
            MockTriageData.TRIAGE_P1,
            MockTriageData.TRIAGE_P2,
            MockTriageData.TRIAGE_P3,
        ]


# ==================== 证据数据 ====================

@dataclass
class MockEvidenceData:
    """模拟证据数据"""
    
    # 正常流程 - 日志证据
    LOGS_EVIDENCE = {
        "evidence_id": "EV-001",
        "tool_name": "log_query",
        "category": "logs",
        "source_ref": "query_id: log_query_001",
        "source_timestamp": datetime.now() - timedelta(minutes=5),
        "summary": "发现 100 条数据库连接超时错误",
        "raw_payload": {
            "total_count": 100,
            "error_patterns": [
                {"pattern": "connection timeout", "count": 80},
                {"pattern": "database error", "count": 20}
            ],
            "sample_logs": [
                {"timestamp": "2024-01-15T10:05:00Z", "message": "connection timeout to db"},
                {"timestamp": "2024-01-15T10:05:01Z", "message": "connection timeout to db"},
            ]
        },
        "confidence": 0.9,
        "freshness_score": 0.95,
        "completeness_score": 0.85
    }
    
    # 正常流程 - 指标证据
    METRICS_EVIDENCE = {
        "evidence_id": "EV-002",
        "tool_name": "metrics_query",
        "category": "metrics",
        "source_ref": "query_id: metrics_query_001",
        "source_timestamp": datetime.now() - timedelta(minutes=3),
        "summary": "5xx 错误率从 1% 飙升到 25%，CPU 使用率 95%",
        "raw_payload": {
            "metrics": [
                {"name": "error_rate_5xx", "value": 25.0, "unit": "%", "baseline": 1.0},
                {"name": "cpu_usage", "value": 95.0, "unit": "%", "baseline": 30.0},
                {"name": "memory_usage", "value": 80.0, "unit": "%", "baseline": 50.0},
                {"name": "p95_latency", "value": 3000.0, "unit": "ms", "baseline": 200.0}
            ]
        },
        "confidence": 0.95,
        "freshness_score": 0.98,
        "completeness_score": 0.9
    }
    
    # 正常流程 - 部署记录证据
    DEPLOYMENT_EVIDENCE = {
        "evidence_id": "EV-003",
        "tool_name": "deployment_query",
        "category": "deployments",
        "source_ref": "query_id: deploy_query_001",
        "source_timestamp": datetime.now() - timedelta(hours=1),
        "summary": "最近 30 分钟无部署操作，上次部署是 2 小时前",
        "raw_payload": {
            "recent_deployments": [],
            "last_deployment": {
                "version": "v2.0.5",
                "timestamp": datetime.now() - timedelta(hours=2),
                "status": "success"
            }
        },
        "confidence": 0.85,
        "freshness_score": 0.7,
        "completeness_score": 0.8
    }
    
    # 正常流程 - Runbook 证据
    RUNBOOK_EVIDENCE = {
        "evidence_id": "EV-004",
        "tool_name": "runbook_query",
        "category": "runbook",
        "source_ref": "runbook_id: db_connection_timeout",
        "source_timestamp": datetime.now() - timedelta(days=30),
        "summary": "匹配到相关 Runbook: 数据库连接超时处理",
        "raw_payload": {
            "runbook_title": "数据库连接超时处理",
            "runbook_steps": [
                "1. 检查数据库连接池配置",
                "2. 检查数据库服务器负载",
                "3. 检查网络延迟",
                "4. 重启应用服务"
            ],
            "relevance_score": 0.92
        },
        "confidence": 0.92,
        "freshness_score": 0.6,
        "completeness_score": 0.88
    }
    
    # 异常流程 - 工具超时
    EVIDENCE_TIMEOUT = {
        "evidence_id": "EV-ERROR-001",
        "tool_name": "log_query",
        "category": "logs",
        "source_ref": "query_id: log_query_timeout",
        "summary": "日志查询超时",
        "error": "Query timeout after 30 seconds",
        "confidence": 0.0,
        "freshness_score": 0.0,
        "completeness_score": 0.0,
        "status": "timeout"
    }
    
    # 异常流程 - 证据不足
    EVIDENCE_INSUFFICIENT = {
        "evidence_id": "EV-ERROR-002",
        "tool_name": "log_query",
        "category": "logs",
        "source_ref": "query_id: log_query_empty",
        "summary": "未找到相关日志",
        "raw_payload": {"logs": []},
        "confidence": 0.1,
        "freshness_score": 0.5,
        "completeness_score": 0.1,
        "status": "insufficient"
    }
    
    # 并行证据收集结果
    PARALLEL_EVIDENCE_COLLECTION = [
        LOGS_EVIDENCE,
        METRICS_EVIDENCE,
        DEPLOYMENT_EVIDENCE,
        RUNBOOK_EVIDENCE,
    ]
    
    @staticmethod
    def get_all_evidence() -> List[Dict[str, Any]]:
        return [
            MockEvidenceData.LOGS_EVIDENCE,
            MockEvidenceData.METRICS_EVIDENCE,
            MockEvidenceData.DEPLOYMENT_EVIDENCE,
            MockEvidenceData.RUNBOOK_EVIDENCE,
        ]


# ==================== 根因数据 ====================

@dataclass
class MockRootCauseData:
    """模拟根因分析数据"""
    
    # 正常流程 - 单根因
    SINGLE_ROOT_CAUSE = {
        "candidate_id": "RC-001",
        "hypothesis": "数据库连接池耗尽导致服务响应超时",
        "confidence": 0.85,
        "supporting_evidence_ids": ["EV-001", "EV-002"],
        "contradicting_evidence_ids": [],
        "next_checks": [
            "检查数据库连接池配置",
            "检查活跃连接数"
        ]
    }
    
    # 正常流程 - 多根因候选
    MULTI_ROOT_CAUSE = [
        {
            "candidate_id": "RC-001",
            "hypothesis": "数据库连接池耗尽",
            "confidence": 0.6,
            "supporting_evidence_ids": ["EV-001"],
            "contradicting_evidence_ids": [],
            "next_checks": ["检查连接池配置"]
        },
        {
            "candidate_id": "RC-002",
            "hypothesis": "数据库服务器 CPU 过载",
            "confidence": 0.5,
            "supporting_evidence_ids": ["EV-002"],
            "contradicting_evidence_ids": [],
            "next_checks": ["检查数据库服务器负载"]
        },
        {
            "candidate_id": "RC-003",
            "hypothesis": "网络延迟增加",
            "confidence": 0.3,
            "supporting_evidence_ids": [],
            "contradicting_evidence_ids": [],
            "next_checks": ["检查网络延迟"]
        }
    ]
    
    # 正常流程 - 修复建议
    REMEDIATION_SUGGESTION = {
        "action_type": "restart",
        "service": "payment-service",
        "env": "production",
        "params": {
            "restart_strategy": "rolling"
        },
        "risk_level": "MEDIUM",
        "requires_approval": True,
        "expected_impact": "服务短暂不可用约 30 秒",
        "rollback_plan": "如有问题立即回滚到上一版本",
        "idempotency_key": "restart_payment-service_20240115"
    }
    
    # 低风险动作
    LOW_RISK_ACTION = {
        "action_type": "refresh_cache",
        "service": "payment-service",
        "env": "production",
        "params": {"cache_key": "payment_config"},
        "risk_level": "LOW",
        "requires_approval": False
    }
    
    # 高风险动作
    HIGH_RISK_ACTION = {
        "action_type": "rollback",
        "service": "order-service",
        "env": "production",
        "params": {"target_version": "v2.0.4"},
        "risk_level": "HIGH",
        "requires_approval": True
    }
    
    # 异常流程 - 证据冲突
    CONFLICTING_EVIDENCE = {
        "candidate_id": "RC-ERROR-001",
        "hypothesis": "数据库连接池问题",
        "confidence": 0.4,
        "supporting_evidence_ids": ["EV-001"],
        "contradicting_evidence_ids": ["EV-CONFLICT"],
        "next_checks": [],
        "has_conflict": True,
        "conflict_details": "日志显示连接超时，但监控显示服务正常"
    }
    
    # 异常流程 - 证据不足
    INSUFFICIENT_EVIDENCE = {
        "candidate_id": "RC-ERROR-002",
        "hypothesis": "未知",
        "confidence": 0.1,
        "supporting_evidence_ids": [],
        "contradicting_evidence_ids": [],
        "next_checks": ["需要更多证据支持"],
        "insufficient": True
    }
    
    @staticmethod
    def get_all_root_causes() -> List[Dict[str, Any]]:
        return [
            MockRootCauseData.SINGLE_ROOT_CAUSE,
            *MockRootCauseData.MULTI_ROOT_CAUSE,
        ]


# ==================== 动作数据 ====================

@dataclass
class MockActionData:
    """模拟动作数据"""
    
    # 正常流程 - 动作执行成功
    ACTION_SUCCESS = {
        "action_id": "ACT-001",
        "action_type": "restart",
        "service": "payment-service",
        "env": "production",
        "params": {"restart_strategy": "rolling"},
        "risk_level": "MEDIUM",
        "status": "success",
        "duration_seconds": 30,
        "output": "服务重启成功",
        "idempotency_key": "restart_payment-service_20240115"
    }
    
    # 正常流程 - 幂等性检查
    ACTION_IDEMPOTENT = {
        "action_id": "ACT-001",
        "action_type": "restart",
        "service": "payment-service",
        "status": "idempotent",
        "output": "相同动作已在执行中，返回现有结果",
        "idempotency_key": "restart_payment-service_20240115"
    }
    
    # 异常流程 - 执行失败
    ACTION_FAILURE = {
        "action_id": "ACT-ERROR-001",
        "action_type": "restart",
        "service": "payment-service",
        "status": "failed",
        "error": "服务启动失败",
        "duration_seconds": 60,
        "compensation_plan": "执行回滚到上一版本",
        "rollback_suggestion": "建议执行 rollback action"
    }
    
    # 异常流程 - 执行超时
    ACTION_TIMEOUT = {
        "action_id": "ACT-ERROR-002",
        "action_type": "restart",
        "service": "payment-service",
        "status": "timeout",
        "duration_seconds": 120,
        "error": "执行超过 60 秒超时"
    }
    
    # 异常流程 - 部分成功
    ACTION_PARTIAL_SUCCESS = {
        "action_id": "ACT-ERROR-003",
        "action_type": "scale",
        "service": "payment-service",
        "status": "partial_success",
        "completed_steps": ["增加副本数到 5"],
        "failed_steps": ["更新负载均衡配置"],
        "recommendation": "手动检查负载均衡配置"
    }
    
    @staticmethod
    def get_all_actions() -> List[Dict[str, Any]]:
        return [
            MockActionData.ACTION_SUCCESS,
            MockActionData.ACTION_FAILURE,
            MockActionData.ACTION_TIMEOUT,
            MockActionData.ACTION_PARTIAL_SUCCESS,
        ]


# ==================== 审批数据 ====================

@dataclass
class MockApprovalData:
    """模拟审批数据"""
    
    # 正常流程 - 审批通过
    APPROVAL_APPROVED = {
        "approval_id": "APR-001",
        "action_id": "ACT-001",
        "status": "approved",
        "approver": "admin@example.com",
        "comment": "同意执行",
        "timestamp": datetime.now()
    }
    
    # 正常流程 - 审批拒绝
    APPROVAL_REJECTED = {
        "approval_id": "APR-002",
        "action_id": "ACT-002",
        "status": "rejected",
        "approver": "admin@example.com",
        "comment": "风险太高，需要进一步分析",
        "timestamp": datetime.now()
    }
    
    # 异常流程 - 审批超时
    APPROVAL_TIMEOUT = {
        "approval_id": "APR-ERROR-001",
        "action_id": "ACT-003",
        "status": "timeout",
        "timeout_duration_minutes": 30,
        "last_reminder": datetime.now() - timedelta(minutes=10)
    }
    
    # 异常流程 - 审批参数修改
    APPROVAL_MODIFIED = {
        "approval_id": "APR-003",
        "action_id": "ACT-001",
        "status": "approved_with_modification",
        "original_params": {"restart_strategy": "rolling"},
        "modified_params": {"restart_strategy": "blue_green"},
        "comment": "建议使用蓝绿部署减少影响",
        "approver": "admin@example.com"
    }
    
    @staticmethod
    def get_all_approvals() -> List[Dict[str, Any]]:
        return [
            MockApprovalData.APPROVAL_APPROVED,
            MockApprovalData.APPROVAL_REJECTED,
            MockApprovalData.APPROVAL_MODIFIED,
        ]


# ==================== RCA 报告数据 ====================

@dataclass
class MockRCAData:
    """模拟 RCA 报告数据"""
    
    # 正常流程 - 完整 RCA 报告
    RCA_COMPLETE = {
        "rca_id": "RCA-2024-0015",
        "incident_id": "INC-2024-0015",
        "title": "支付服务 5xx 错误率飙升",
        "summary": "支付服务因数据库连接池配置不当导致连接耗尽，引发大量 5xx 错误",
        
        # 时间线
        "timeline": [
            {
                "phase": "detection",
                "timestamp": datetime.now() - timedelta(minutes=35),
                "description": "监控告警触发，5xx 错误率达到 20%"
            },
            {
                "phase": "diagnosis",
                "timestamp": datetime.now() - timedelta(minutes=30),
                "description": "开始排查，发现数据库连接超时"
            },
            {
                "phase": "execution",
                "timestamp": datetime.now() - timedelta(minutes=20),
                "description": "执行重启服务动作"
            },
            {
                "phase": "recovery",
                "timestamp": datetime.now() - timedelta(minutes=15),
                "description": "服务恢复，错误率降为 0"
            }
        ],
        
        # 根因分析
        "root_cause": {
            "confirmed_cause": "数据库连接池配置最大连接数为 100，高并发时连接耗尽",
            "confidence": 0.9,
            "evidence_refs": ["EV-001", "EV-002"]
        },
        
        # 处置动作
        "actions_taken": [
            {
                "action": "重启支付服务",
                "result": "成功",
                "timestamp": datetime.now() - timedelta(minutes=20)
            }
        ],
        
        # 影响范围
        "impact_scope": {
            "services_affected": ["payment-service"],
            "users_affected": "所有用户",
            "duration_minutes": 20,
            "severity": "P1"
        },
        
        # 后续预防项
        "action_items": [
            {
                "description": "增加数据库连接池最大连接数",
                "owner": "dba-team",
                "due_date": datetime.now() + timedelta(days=7),
                "status": "pending"
            },
            {
                "description": "添加数据库连接池监控告警",
                "owner": "sre-team",
                "due_date": datetime.now() + timedelta(days=3),
                "status": "pending"
            }
        ],
        
        # Agent 表现总结
        "agent_summary": {
            "evidence_collected": 4,
            "evidence_quality": "良好",
            "misjudgments": [],
            "improvements": ["可增加对连接池配置的自动检测"]
        },
        
        # 元数据
        "created_at": datetime.now(),
        "created_by": "OpsPilot Agent",
        "confirmed": True
    }
    
    # 异常流程 - 部分数据缺失
    RCA_PARTIAL = {
        "rca_id": "RCA-2024-0016",
        "incident_id": "INC-2024-0016",
        "title": "订单服务延迟增加",
        "summary": "部分数据缺失，无法完成完整分析",
        
        "timeline": [
            {
                "phase": "detection",
                "timestamp": datetime.now() - timedelta(hours=2),
                "description": "发现延迟增加"
            }
        ],
        
        "root_cause": {
            "confirmed_cause": None,
            "confidence": 0.1,
            "evidence_refs": [],
            "missing_data": ["执行环节被跳过"]
        },
        
        "actions_taken": [],
        "impact_scope": {
            "services_affected": ["order-service"],
            "users_affected": "部分用户",
            "duration_minutes": 60,
            "severity": "P2"
        },
        
        "action_items": [],
        
        "agent_summary": {
            "evidence_collected": 1,
            "evidence_quality": "不足",
            "misjudgments": [],
            "improvements": ["需要更多证据"]
        },
        
        "created_at": datetime.now(),
        "created_by": "OpsPilot Agent",
        "confirmed": False,
        "incomplete": True
    }
    
    @staticmethod
    def get_all_rcas() -> List[Dict[str, Any]]:
        return [
            MockRCAData.RCA_COMPLETE,
            MockRCAData.RCA_PARTIAL,
        ]


# ==================== 知识库数据 ====================

KNOWLEDGE_DATA = {
    # 历史 RCA
    "historical_rcas": [
        {
            "rca_id": "RCA-2023-010",
            "incident_type": "error_rate",
            "service": "payment-service",
            "root_cause": "数据库连接池配置不当",
            "solution": "增加连接池大小",
            "confirmed": True,
            "relevance_score": 0.95
        },
        {
            "rca_id": "RCA-2023-015",
            "incident_type": "performance",
            "service": "order-service",
            "root_cause": "缓存未命中导致数据库压力",
            "solution": "预热缓存",
            "confirmed": True,
            "relevance_score": 0.75
        }
    ],
    
    # Runbook
    "runbooks": [
        {
            "runbook_id": "RB-001",
            "title": "数据库连接超时处理",
            "steps": [
                "1. 检查数据库连接池配置",
                "2. 检查数据库服务器负载",
                "3. 检查网络延迟",
                "4. 重启应用服务"
            ],
            "applicable_services": ["payment-service", "order-service"]
        },
        {
            "runbook_id": "RB-002",
            "title": "服务重启操作",
            "steps": [
                "1. 确认无正在执行的事务",
                "2. 执行滚动重启",
                "3. 验证服务健康状态"
            ],
            "applicable_services": ["*"]
        }
    ]
}
