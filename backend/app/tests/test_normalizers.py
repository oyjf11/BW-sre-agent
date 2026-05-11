import pytest
from datetime import datetime, timedelta

from app.normalizers.env import normalize_env
from app.normalizers.service_alias import normalize_service
from app.normalizers.time_range import normalize_time_range


class TestEnvNormalizer:
    def test_prd_to_prod(self):
        assert normalize_env("prd") == "prod"

    def test_production_to_prod(self):
        assert normalize_env("production") == "prod"

    def test_stg_to_staging(self):
        assert normalize_env("stg") == "staging"

    def test_stage_to_staging(self):
        assert normalize_env("stage") == "staging"

    def test_prod_passthrough(self):
        assert normalize_env("prod") == "prod"

    def test_dev_passthrough(self):
        assert normalize_env("dev") == "dev"

    def test_case_insensitive(self):
        assert normalize_env("PRD") == "prod"
        assert normalize_env("Staging") == "staging"

    def test_whitespace(self):
        assert normalize_env("  prod  ") == "prod"

    def test_invalid_env(self):
        with pytest.raises(ValueError, match="Invalid environment"):
            normalize_env("unknown_env")


class TestServiceAliasNormalizer:
    def test_lowercase(self):
        assert normalize_service("Order-Svc") == "order-svc"

    def test_strip(self):
        assert normalize_service("  api-service  ") == "api-service"


class TestTimeRangeNormalizer:
    def test_none_gives_defaults(self):
        result = normalize_time_range(None)
        assert "start" in result
        assert "end" in result
        assert (result["end"] - result["start"]).total_seconds() == pytest.approx(3600, abs=5)

    def test_empty_dict_gives_defaults(self):
        result = normalize_time_range({})
        assert isinstance(result["start"], datetime)
        assert isinstance(result["end"], datetime)

    def test_iso_strings_parsed(self):
        result = normalize_time_range({
            "start": "2026-03-28T10:00:00",
            "end": "2026-03-28T11:00:00",
        })
        assert result["start"] == datetime(2026, 3, 28, 10, 0)
        assert result["end"] == datetime(2026, 3, 28, 11, 0)

    def test_partial_fills_missing(self):
        result = normalize_time_range({"start": "2026-03-28T10:00:00"})
        assert result["start"] == datetime(2026, 3, 28, 10, 0)
        assert isinstance(result["end"], datetime)
