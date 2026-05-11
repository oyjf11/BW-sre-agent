import os
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)

MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "")

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
        self.host = host or MYSQL_HOST
        self.port = port or MYSQL_PORT
        self.user = user or MYSQL_USER
        self.password = password or MYSQL_PASSWORD
        self.database = database or MYSQL_DB

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
