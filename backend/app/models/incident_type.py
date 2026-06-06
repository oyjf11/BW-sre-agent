"""Closed incident-type label space shared by triage, diagnose, and offline eval.

This enum is the single source of truth for root-cause classification. The eval
scorer compares against these values by enum equality (no keyword/LLM guessing),
so the label space must stay closed and mutually exclusive.

Extending: add one line here + at least one dataset case for the new type.
The scorer/metrics compare dynamically by value and need no code change.
"""
from enum import Enum


class IncidentType(str, Enum):
    deployment_regression = "deployment_regression"  # 发布变更(代码/配置/镜像/依赖版本)直接引入
    configuration_error = "configuration_error"      # 非发布的配置错误(手工改动/环境漂移/配置中心)
    resource_exhaustion = "resource_exhaustion"      # CPU/内存/连接池/磁盘耗尽
    dependency_failure = "dependency_failure"        # 下游/第三方依赖不可用
    database_failure = "database_failure"            # DB 层故障(慢查询/锁/连接/主从)
    network_failure = "network_failure"              # 网络/DNS/LB 链路
    traffic_anomaly = "traffic_anomaly"              # 流量突增/异常请求模式
    security_incident = "security_incident"          # 安全事件(入侵/漏洞利用/异常访问)
    service_degradation = "service_degradation"      # 服务自身退化(非以上明确归因)
    unknown = "unknown"                              # 证据不足，无法判断
    other = "other"                                  # 已判因但超出标签体系
