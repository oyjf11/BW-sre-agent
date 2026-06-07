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


class TestRootCauseCandidateIncidentType:
    def test_defaults_to_unknown(self):
        from app.models.root_cause import RootCauseCandidate

        c = RootCauseCandidate(
            candidate_id="c1", hypothesis="something", confidence=0.5
        )
        assert c.incident_type == IncidentType.unknown

    def test_accepts_explicit_type(self):
        from app.models.root_cause import RootCauseCandidate

        c = RootCauseCandidate(
            candidate_id="c1",
            hypothesis="bad deploy",
            confidence=0.9,
            incident_type=IncidentType.deployment_regression,
        )
        assert c.incident_type == IncidentType.deployment_regression

    def test_backward_compat_old_dict_without_field(self):
        # Old checkpoints serialized before this field existed must still load
        from app.models.root_cause import RootCauseCandidate

        old = {"candidate_id": "c1", "hypothesis": "x", "confidence": 0.3}
        c = RootCauseCandidate(**old)
        assert c.incident_type == IncidentType.unknown

    def test_accepts_string_value(self):
        # LLM-parsed string should coerce into the enum
        from app.models.root_cause import RootCauseCandidate

        c = RootCauseCandidate(
            candidate_id="c1",
            hypothesis="db lock",
            confidence=0.7,
            incident_type="database_failure",
        )
        assert c.incident_type == IncidentType.database_failure
