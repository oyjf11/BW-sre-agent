"""Tests for IncidentType enum (closed label space for eval)."""
from app.models.incident_type import IncidentType


class TestIncidentType:
    def test_has_eleven_types(self):
        assert len(list(IncidentType)) == 11

    def test_str_enum_values_match_names(self):
        # str-Enum: value equals the snake_case string used everywhere
        assert IncidentType.deployment_regression.value == "deployment_regression"
        assert IncidentType.unknown.value == "unknown"
        assert IncidentType.other.value == "other"

    def test_is_str_subclass(self):
        # Must be a str subclass so `== "deployment_regression"` works directly
        assert isinstance(IncidentType.deployment_regression, str)
        assert IncidentType.resource_exhaustion == "resource_exhaustion"

    def test_triage_legacy_values_all_present(self):
        # The 5 magic-strings triage already emits must round-trip with zero loss
        for legacy in (
            "deployment_regression",
            "resource_exhaustion",
            "dependency_failure",
            "security_incident",
            "service_degradation",
        ):
            assert IncidentType(legacy).value == legacy

    def test_membership_check_by_value(self):
        values = {t.value for t in IncidentType}
        assert "database_failure" in values
        assert "network_failure" in values
        assert "traffic_anomaly" in values
        assert "configuration_error" in values
        assert "made_up_type" not in values
