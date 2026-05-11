"""Environment Policy for prod environment restrictions."""
from app.models.action import ActionSpec


class EnvPolicy:

    RESTRICTED_ACTIONS_IN_PROD = {
        "delete",
        "terminate",
        "force-stop",
        "drop-table",
        "truncate",
    }

    def is_prod_restricted(self, action: ActionSpec) -> bool:
        if action.env.lower() != "prod":
            return False
        return action.action_type.lower() in self.RESTRICTED_ACTIONS_IN_PROD

    def allow_action(self, action: ActionSpec) -> bool:
        if action.env.lower() != "prod":
            return True
        return action.action_type.lower() not in self.RESTRICTED_ACTIONS_IN_PROD
