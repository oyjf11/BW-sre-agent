"""Environment alias normalization: prd→prod, stg→staging, etc."""

_ENV_ALIASES = {
    "prd": "prod",
    "production": "prod",
    "stg": "staging",
    "stage": "staging",
    "pre": "staging",
    "dev": "dev",
    "development": "dev",
    "test": "test",
    "testing": "test",
}

VALID_ENVS = {"prod", "staging", "dev", "test"}


def normalize_env(env: str) -> str:
    normalized = env.strip().lower()
    normalized = _ENV_ALIASES.get(normalized, normalized)
    if normalized not in VALID_ENVS:
        raise ValueError(f"Invalid environment: '{env}'. Valid: {sorted(VALID_ENVS)}")
    return normalized
