import logging
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:
    from kubernetes import client as k8s_client_lib
    from kubernetes import config as k8s_config_lib
    from kubernetes.config.config_exception import ConfigException
except ModuleNotFoundError:  # pragma: no cover - exercised through adapter fallback
    k8s_client_lib = None
    k8s_config_lib = None

    class ConfigException(Exception):
        pass


@lru_cache(maxsize=8)
def _load_kube_config(config_path: str, context: str) -> str:
    if k8s_config_lib is None:
        raise RuntimeError("kubernetes package is not installed")

    try:
        k8s_config_lib.load_incluster_config()
        return "incluster"
    except ConfigException:
        kwargs = {}
        if config_path:
            kwargs["config_file"] = config_path
        if context:
            kwargs["context"] = context
        k8s_config_lib.load_kube_config(**kwargs)
        return "kubeconfig"


@lru_cache(maxsize=8)
def _get_api_clients(config_path: str, context: str):
    source = _load_kube_config(config_path, context)
    k8s_client_lib.Configuration._default.verify_ssl = False
    return (
        k8s_client_lib.AppsV1Api(),
        k8s_client_lib.CoreV1Api(),
        source,
    )


class K8sClient:
    def __init__(
        self,
        allowed_namespaces: Optional[List[str]] = None,
        config_path: Optional[str] = None,
        context: Optional[str] = None,
    ):
        settings = get_settings()
        self.allowed_namespaces = (
            allowed_namespaces if allowed_namespaces is not None else settings.k8s_allowed_namespaces
        )
        self.config_path = config_path if config_path is not None else settings.k8s_config_path
        self.context = context if context is not None else settings.k8s_context

    def ensure_namespace_allowed(self, namespace: str) -> None:
        if not self.allowed_namespaces:
            raise PermissionError(
                "K8S_ALLOWED_NAMESPACES is empty; real K8s queries are fail-closed"
            )
        if namespace not in self.allowed_namespaces:
            raise PermissionError(f"Namespace '{namespace}' is not in K8S_ALLOWED_NAMESPACES")

    def _apis(self):
        return _get_api_clients(self.config_path, self.context)

    def resolve_target(
        self,
        service: str,
        namespace: str = "",
        deployment_name: str = "",
    ) -> Tuple[str, str]:
        resolved_namespace = namespace or "default"
        resolved_deployment = deployment_name or service
        self.ensure_namespace_allowed(resolved_namespace)
        return resolved_namespace, resolved_deployment

    def get_deployment(self, namespace: str, deployment_name: str):
        apps_api, _, _ = self._apis()
        return apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)

    def get_deployment_status(self, namespace: str, deployment_name: str) -> Dict[str, object]:
        deployment = self.get_deployment(namespace, deployment_name)
        status = deployment.status
        desired = status.replicas or 0
        ready = status.ready_replicas or 0
        unavailable = status.unavailable_replicas or 0

        conditions = status.conditions or []
        available = any(
            cond.type == "Available" and cond.status == "True"
            for cond in conditions
            if cond is not None
        )

        last_rollout = None
        if deployment.metadata and deployment.metadata.creation_timestamp:
            last_rollout = deployment.metadata.creation_timestamp.isoformat()

        if available and ready >= desired and unavailable == 0:
            health = "running"
        elif ready > 0:
            health = "degraded"
        else:
            health = "unavailable"

        return {
            "service": deployment_name,
            "namespace": namespace,
            "status": health,
            "replicas": desired,
            "ready_replicas": ready,
            "unavailable_replicas": unavailable,
            "last_rollout": last_rollout,
        }

    def list_pods_for_target(
        self,
        namespace: str,
        deployment_name: str,
        service: str,
    ):
        _, core_api, _ = self._apis()
        deployment = self.get_deployment(namespace, deployment_name)
        selector = deployment.spec.selector.match_labels or {}
        label_selector = ",".join(f"{k}={v}" for k, v in selector.items() if k and v)
        if not label_selector:
            label_selector = f"app={service}"
        return core_api.list_namespaced_pod(namespace=namespace, label_selector=label_selector).items

    def list_events(self, namespace: str):
        _, core_api, _ = self._apis()
        return core_api.list_namespaced_event(namespace=namespace).items

    def read_pod_log(self, namespace: str, pod_name: str, tail_lines: int) -> str:
        _, core_api, _ = self._apis()
        return core_api.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=tail_lines,
            timestamps=True,
        )

    def list_all_deployments(self) -> list:
        deployments = []
        apps_api, _, _ = self._apis()
        for ns in self.allowed_namespaces:
            try:
                deps = apps_api.list_namespaced_deployment(namespace=ns)
                deployments.extend(deps.items)
            except Exception:
                pass
        return deployments
