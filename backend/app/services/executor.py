"""Controlled Executor: idempotent execution with precondition checks and audit trail."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.db_models import IncidentAction
from app.repositories.actions_repo import ActionsRepo
from app.services.event_bus import EventType, event_bus
from app.tools.gateway import ToolGateway, ToolRequest

logger = logging.getLogger(__name__)


class ExecutionResult:
    def __init__(
        self,
        action_id: str,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        skipped: bool = False,
    ):
        self.action_id = action_id
        self.success = success
        self.result = result
        self.error = error
        self.skipped = skipped

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "skipped": self.skipped,
        }


class ControlledExecutor:
    def __init__(self, db: Session):
        self.db = db
        self.actions_repo = ActionsRepo(db)
        self.gateway = ToolGateway()

    async def execute_action(
        self,
        run_id: str,
        action_type: str,
        service: str,
        env: str,
        params: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        preconditions: Optional[List[str]] = None,
        approval_id: Optional[str] = None,
        attempt_no: int = 1,
    ) -> ExecutionResult:
        # 1. Idempotency check
        if idempotency_key:
            existing = self.actions_repo.get_by_idempotency(idempotency_key)
            if existing and existing.execution_status in ("COMPLETED", "EXECUTING"):
                logger.info(
                    f"Idempotent skip: {idempotency_key} already {existing.execution_status}"
                )
                event_bus.publish(
                    db=self.db,
                    run_id=run_id,
                    event_type=EventType.ACTION_STARTED,
                    message=f"Skipped (idempotent): {action_type} on {service}/{env}",
                    data={
                        "action_id": existing.action_id,
                        "skipped": True,
                        "reason": "idempotency",
                    },
                )
                return ExecutionResult(
                    action_id=existing.action_id,
                    success=existing.execution_status == "COMPLETED",
                    result=existing.result_json,
                    skipped=True,
                )

        # 2. Precondition checks
        if preconditions:
            failed = await self._check_preconditions(run_id, service, env, preconditions)
            if failed:
                action_rec = self.actions_repo.insert(
                    run_id=run_id,
                    action_type=action_type,
                    params=params,
                    idempotency_key=idempotency_key,
                    approval_id=approval_id,
                    executor_name="controlled_executor",
                    request_json={"service": service, "env": env, "params": params},
                )
                self.actions_repo.mark_completed(
                    action_rec.action_id,
                    status="PRECONDITION_FAILED",
                    result={"failed_preconditions": failed},
                )
                event_bus.publish(
                    db=self.db,
                    run_id=run_id,
                    event_type=EventType.ACTION_FAILED,
                    message=f"Precondition failed for {action_type}: {', '.join(failed)}",
                    data={"action_id": action_rec.action_id, "failed_preconditions": failed},
                )
                return ExecutionResult(
                    action_id=action_rec.action_id,
                    success=False,
                    error=f"Precondition failed: {', '.join(failed)}",
                )

        # 3. Create action record + mark started
        action_rec = self.actions_repo.insert(
            run_id=run_id,
            action_type=action_type,
            params=params,
            idempotency_key=idempotency_key,
            approval_id=approval_id,
            executor_name="controlled_executor",
            request_json={"service": service, "env": env, "params": params},
        )
        self.actions_repo.mark_started(action_rec.action_id, attempt_no=attempt_no)

        event_bus.publish(
            db=self.db,
            run_id=run_id,
            event_type=EventType.ACTION_STARTED,
            message=f"Executing {action_type} on {service}/{env} (attempt {attempt_no})",
            data={
                "action_id": action_rec.action_id,
                "action_type": action_type,
                "attempt_no": attempt_no,
            },
        )

        # 4. Execute via gateway
        try:
            req = ToolRequest(
                tool_name="execute_action",
                params={
                    "action_type": action_type,
                    "service": service,
                    "env": env,
                    "params": params,
                },
                run_id=run_id,
            )
            tool_result = await self.gateway.call_tool(req)

            if tool_result.success:
                self.actions_repo.mark_completed(
                    action_rec.action_id,
                    status="COMPLETED",
                    result=tool_result.result,
                )
                event_bus.publish(
                    db=self.db,
                    run_id=run_id,
                    event_type=EventType.ACTION_COMPLETED,
                    message=f"Completed {action_type} on {service}/{env}",
                    data={"action_id": action_rec.action_id, "result": tool_result.result},
                )
                return ExecutionResult(
                    action_id=action_rec.action_id,
                    success=True,
                    result=tool_result.result,
                )
            else:
                self.actions_repo.mark_completed(
                    action_rec.action_id,
                    status="FAILED",
                    result={"error": tool_result.error},
                )
                event_bus.publish(
                    db=self.db,
                    run_id=run_id,
                    event_type=EventType.ACTION_FAILED,
                    message=f"Failed {action_type} on {service}/{env}: {tool_result.error}",
                    data={"action_id": action_rec.action_id, "error": tool_result.error},
                )
                return ExecutionResult(
                    action_id=action_rec.action_id,
                    success=False,
                    error=tool_result.error,
                )
        except Exception as e:
            logger.exception(f"Executor error for action {action_rec.action_id}")
            self.actions_repo.mark_completed(
                action_rec.action_id,
                status="ERROR",
                result={"error": str(e)},
            )
            return ExecutionResult(
                action_id=action_rec.action_id,
                success=False,
                error=str(e),
            )

    async def execute_plan(
        self,
        run_id: str,
        actions: List[Dict[str, Any]],
        approval_id: Optional[str] = None,
    ) -> List[ExecutionResult]:
        """Execute all actions in a remediation plan sequentially."""
        results = []
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"execute_plan: received {len(actions)} actions")

        for i, action in enumerate(actions):
            logger.info(f"  action[{i}]: type={type(action).__name__}, value={action}")

            if action is None:
                logger.warning(f"Skipping None action at index {i}")
                continue

            action_type = action.get("action_type", "unknown")
            service = action.get("service", "unknown")
            env = action.get("env", "unknown")
            params = action.get("params", {})
            idempotency_key = action.get("idempotency_key")
            preconditions = action.get("preconditions")

            result = await self.execute_action(
                run_id=run_id,
                action_type=action_type,
                service=service,
                env=env,
                params=params,
                idempotency_key=idempotency_key,
                preconditions=preconditions,
                approval_id=approval_id,
            )
            results.append(result)

            # Stop on first failure (non-skipped)
            if not result.success and not result.skipped:
                break

        return results

    async def _check_preconditions(
        self, run_id: str, service: str, env: str, preconditions: List[str]
    ) -> List[str]:
        """Check preconditions. Returns list of failed conditions (empty = all passed)."""
        failed = []
        for condition in preconditions:
            # Simple precondition checks via tool gateway
            if condition == "service_exists":
                try:
                    req = ToolRequest(
                        tool_name="query_service_metadata",
                        params={"service": service, "env": env},
                        run_id=run_id,
                    )
                    result = await self.gateway.call_tool(req)
                    if not result.success:
                        failed.append(f"service_exists: check failed for {service}")
                    elif result.result and not result.result.get("exists"):
                        failed.append(f"service_exists: {service} not found")
                except Exception:
                    failed.append(f"service_exists: check failed for {service}")
            elif condition == "deployment_healthy":
                try:
                    req = ToolRequest(
                        tool_name="query_k8s_deployment_status",
                        params={"service": service, "env": env},
                        run_id=run_id,
                    )
                    result = await self.gateway.call_tool(req)
                    deploy_status = (result.result or {}).get("status", "") if result.result else ""
                    if not result.success or deploy_status not in ("running", "healthy", "available"):
                        failed.append(f"deployment_healthy: deployment not healthy for {service}")
                except Exception:
                    failed.append(f"deployment_healthy: check failed for {service}")
            # Unknown preconditions are skipped (logged)
            else:
                logger.warning(f"Unknown precondition '{condition}', skipping")
        return failed
