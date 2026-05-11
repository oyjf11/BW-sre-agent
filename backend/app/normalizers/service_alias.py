"""Service alias normalization: strip whitespace, lowercase, resolve known aliases."""

_SERVICE_ALIASES = {
    # Add project-specific aliases here, e.g.:
    # "order": "order-svc",
    # "user": "user-svc",
}


def normalize_service(service: str) -> str:
    normalized = service.strip().lower()
    return _SERVICE_ALIASES.get(normalized, normalized)
