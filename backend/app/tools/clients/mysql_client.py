import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import pymysql
from pymysql.cursors import DictCursor

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _get_mysql_config():
    settings = get_settings()
    return {
        "host": settings.mysql_host,
        "port": settings.mysql_port,
        "user": settings.mysql_user,
        "password": settings.mysql_password,
        "database": settings.mysql_db,
    }


MYSQL_HOST_DEFAULT = ""
MYSQL_PORT_DEFAULT = 3306
MYSQL_USER_DEFAULT = ""
MYSQL_PASSWORD_DEFAULT = ""
MYSQL_DB_DEFAULT = ""

CONNECT_TIMEOUT = 5
READ_TIMEOUT = 10
RESPONSE_SIZE_LIMIT_KB = 64


class MySQLClient:
    """Simple MySQL client with per-query connect/close pattern.

    pymysql has no built-in pool. We use connect-per-query with
    configurable timeouts. For production, wrap with DBUtils or
    a proper pool.
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        database: str = None,
    ):
        cfg = _get_mysql_config()
        self.host = host or cfg["host"]
        self.port = port or cfg["port"]
        self.user = user or cfg["user"]
        self.password = password or cfg["password"]
        self.database = database or cfg["database"]

    @contextmanager
    def _connection(self):
        conn = None
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                connect_timeout=CONNECT_TIMEOUT,
                read_timeout=READ_TIMEOUT,
                cursorclass=DictCursor,
                charset="utf8mb4",
            )
            yield conn
        finally:
            if conn:
                conn.close()

    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return list(rows)

    def execute_single(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
                return row


def truncate_result(data: Any, max_kb: int = RESPONSE_SIZE_LIMIT_KB) -> Any:
    """Truncate result data to max_kb kilobytes."""
    import json

    raw = json.dumps(data, ensure_ascii=False, default=str)
    if len(raw.encode("utf-8")) <= max_kb * 1024:
        return data
    truncated = raw[: max_kb * 1024 - 100]
    try:
        return json.loads(truncated + '"}]}')
    except Exception:
        return {"_truncated": True, "raw_preview": truncated[:2000]}
