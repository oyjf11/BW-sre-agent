from typing import Dict, Any, List, Optional
from enum import Enum


class EnvPolicy:
    RESTRICTED_ENVS = {"prod", "production", "prd"}
    RESTRICTED_ACTIONS = {"delete", "drop", "truncate"}
    
    ENV_ALLOWLIST: Dict[str, List[str]] = {
        "dev": ["restart", "scale_up", "scale_down", "update_config"],
        "staging": ["restart", "scale_up", "scale_down", "update_config", "rollback"],
        "prod": ["restart", "scale_up", "scale_down"],
    }

    @classmethod
    def is_restricted_env(cls, env: str) -> bool:
        return env.lower() in cls.RESTRICTED_ENVS

    @classmethod
    def is_restricted_action(cls, action_type: str) -> bool:
        return action_type.lower() in cls.RESTRICTED_ACTIONS

    @classmethod
    def can_execute_action(cls, env: str, action_type: str) -> Dict[str, Any]:
        env_lower = env.lower()
        
        if cls.is_restricted_env(env_lower) and cls.is_restricted_action(action_type):
            return {
                "allowed": False,
                "reason": f"Action '{action_type}' is not allowed in production environment",
                "requires_approval": True,
            }
        
        allowed_actions = cls.ENV_ALLOWLIST.get(env_lower, [])
        
        if action_type not in allowed_actions:
            return {
                "allowed": False,
                "reason": f"Action '{action_type}' is not in the allowlist for environment '{env}'",
                "requires_approval": True,
                "allowed_actions": allowed_actions,
            }
        
        return {
            "allowed": True,
            "reason": None,
            "requires_approval": False,
        }

    @classmethod
    def validate_env(cls, env: str) -> bool:
        valid_envs = {"dev", "development", "staging", "stg", "prod", "production", "prd"}
        return env.lower() in valid_envs
