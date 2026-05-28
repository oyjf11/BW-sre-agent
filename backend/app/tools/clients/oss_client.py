import logging
from functools import lru_cache
from typing import Any, Dict, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:
    import oss2
except ModuleNotFoundError:  # pragma: no cover - exercised through adapter fallback
    oss2 = None


ALLOWED_PREFIXES = ("rca/", "evidence/")


@lru_cache(maxsize=1)
def _create_oss_bucket(
    access_key_id: str,
    access_key_secret: str,
    endpoint: str,
    bucket_name: str,
) -> Any:
    if oss2 is None:
        raise RuntimeError("oss2 package is not installed")

    auth = oss2.Auth(access_key_id, access_key_secret)
    return oss2.Bucket(auth, endpoint, bucket_name)


class OssClientWrapper:
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
    ):
        settings = get_settings()
        self.bucket_name = bucket_name or settings.alibaba_oss_bucket
        self.endpoint = endpoint or settings.alibaba_oss_endpoint
        self.access_key_id = access_key_id or settings.alibaba_access_key_id
        self.access_key_secret = access_key_secret or settings.alibaba_access_key_secret

        if not self.bucket_name or not self.endpoint:
            raise RuntimeError(
                "ALIBABA_OSS_BUCKET and ALIBABA_OSS_ENDPOINT are required "
                "for real OSS adapter"
            )
        if not self.access_key_id or not self.access_key_secret:
            raise RuntimeError(
                "ALIBABA_ACCESS_KEY_ID and ALIBABA_ACCESS_KEY_SECRET are required "
                "for real OSS adapter"
            )

    def _get_bucket(self) -> Any:
        return _create_oss_bucket(
            self.access_key_id,
            self.access_key_secret,
            self.endpoint,
            self.bucket_name,
        )

    def _validate_key_prefix(self, key: str) -> None:
        if not any(key.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            allowed = ", ".join(ALLOWED_PREFIXES)
            raise ValueError(
                f"OSS key '{key}' is not allowed. Only prefixes [{allowed}] are permitted."
            )

    def put_object(self, key: str, content: str) -> Dict[str, Any]:
        self._validate_key_prefix(key)

        bucket = self._get_bucket()
        result = bucket.put_object(key, content)

        oss_url = f"https://{self.bucket_name}.{self.endpoint}/{key}"

        response = {
            "oss_key": key,
            "oss_url": oss_url,
            "bucket": self.bucket_name,
            "etag": getattr(result, "etag", ""),
            "status": result.status,
        }

        logger.info(f"OSS put_object success: key={key}, status={result.status}")
        return response
