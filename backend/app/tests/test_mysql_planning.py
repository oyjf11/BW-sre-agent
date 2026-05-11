from app.graph.nodes import planner_node
from app.models.incident import IncidentTicket
from app.models.triage import TriageResult


def test_planner_adds_db_tasks_for_resource_exhaustion():
    state = {
        "ticket": IncidentTicket(
            ticket_id="INC-DB-001",
            title="DB connections high",
            description="mysql threads connected spiking",
            service="payment-service",
            env="prod",
            severity="P2",
            source="manual",
        ),
        "triage": TriageResult(
            incident_type="resource_exhaustion",
            severity="P2",
            suspected_services=["payment-service"],
            rationale="High connection count suggests DB pressure",
        ),
        "step_count": 0,
    }

    updated = planner_node(state)
    tasks = updated["investigation_plan"].tasks
    tool_names = [task.tool_name for task in tasks]

    assert "query_db_variables" in tool_names
    assert "query_db_processlist" in tool_names
    assert "query_db_slow_queries" in tool_names
    assert "query_k8s_deployment_status" in tool_names
    assert "query_k8s_pods" in tool_names
    assert "query_k8s_events" in tool_names
    assert "query_k8s_pod_logs_summary" in tool_names


def test_planner_adds_db_tasks_for_generic_incident():
    state = {
        "ticket": IncidentTicket(
            ticket_id="INC-DB-002",
            title="unknown issue",
            description="intermittent latency",
            service="order-service",
            env="staging",
            severity="P2",
            source="manual",
        ),
        "triage": TriageResult(
            incident_type="service_degradation",
            severity="P2",
            suspected_services=["order-service"],
            rationale="Need broad evidence collection",
        ),
        "step_count": 0,
    }

    updated = planner_node(state)
    tasks = updated["investigation_plan"].tasks
    db_tasks = [task for task in tasks if task.category == "db"]

    assert db_tasks
    assert {task.tool_name for task in db_tasks} == {
        "query_db_processlist",
        "query_db_variables",
    }
