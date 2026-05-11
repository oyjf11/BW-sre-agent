import logging
import asyncio
import json
from datetime import datetime
from typing import Any, Dict

from app.tools.clients.mysql_client import MySQLClient

logger = logging.getLogger(__name__)

YII_LEVEL_MAP = {1: "ERROR", 2: "WARNING", 4: "INFO"}
ENV_CATEGORY_ALIASES = {
    "prod": ["prod", "production"],
    "production": ["production", "prod"],
    "staging": ["staging", "stage"],
    "stage": ["stage", "staging"],
    "dev": ["dev", "development"],
    "development": ["development", "dev"],
    "test": ["test", "testing"],
    "testing": ["testing", "test"],
}


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")


def _build_category_conditions(
    service: str,
    env: str,
    conditions: list[str],
    params: list[str],
) -> None:
    if service:
        conditions.append("category LIKE %s ESCAPE '\\\\'")
        params.append(f"%{_escape_like(service.strip())}%")

    if env:
        env_terms = ENV_CATEGORY_ALIASES.get(env.strip().lower(), [env.strip()])
        env_conditions = []
        for term in dict.fromkeys(term for term in env_terms if term):
            env_conditions.append("category LIKE %s ESCAPE '\\\\'")
            params.append(f"%{_escape_like(term)}%")
        if env_conditions:
            conditions.append(f"({' OR '.join(env_conditions)})")


async def query_logs_from_db(
    service: str = "",
    env: str = "",
    time_range: Dict[str, str] = None,
    query: str = "*",
    limit: int = 200,
    **kwargs,
) -> Dict[str, Any]:
    """Query application logs from MySQL common_app_log table.

    Replaces the mock query_logs adapter with real DB-backed log retrieval.
    Table: common_app_log (id, level, category, log_time, prefix, message, created_at)
    """
    limit = max(1, min(limit, 200))
    conditions = []
    params: list[str] = []

    _build_category_conditions(service, env, conditions, params)

    if time_range and "from" in time_range:
        conditions.append("created_at >= %s")
        params.append(time_range["from"])
    if time_range and "to" in time_range:
        conditions.append("created_at <= %s")
        params.append(time_range["to"])
    if query and query != "*":
        escaped_query = _escape_like(query)
        conditions.append("message LIKE %s ESCAPE '\\\\'")
        params.append(f"%{escaped_query}%")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    data_sql = f"SELECT id, level, category, log_time, prefix, message, created_at FROM common_app_log {where_clause} ORDER BY created_at DESC LIMIT %s"

    client = MySQLClient()

    try:
        rows = await asyncio.to_thread(client.execute_query, data_sql, tuple(params) + (limit,))
        logs = []
        for row in rows:
            level_int = row.get("level", 4)
            level_str = YII_LEVEL_MAP.get(level_int, f"LEVEL_{level_int}")
            logs.append(
                {
                    "timestamp": datetime.fromtimestamp(row["log_time"]).isoformat()
                    if row.get("log_time")
                    else str(row.get("created_at", "")),
                    "level": level_str,
                    "message": row.get("message", ""),
                    "source": row.get("category", ""),
                }
            )

        MAX_BYTES = 64 * 1024
        truncated_flag = False
        while logs and len(json.dumps(logs, ensure_ascii=False, default=str).encode()) > MAX_BYTES:
            logs.pop()
            truncated_flag = True

        return {
            "logs": logs,
            "count": len(logs),
            "query": query,
            "truncated": truncated_flag,
        }
    except Exception as e:
        logger.error(f"query_logs_from_db failed: {e}")
        return {
            "logs": [],
            "count": 0,
            "query": query,
            "error": str(e),
        }


async def query_db_processlist(**kwargs) -> Dict[str, Any]:
    """Query active MySQL connections and lock waits.

    Filters out Sleep state connections. Returns truncated result.
    """
    client = MySQLClient()

    try:
        rows = await asyncio.to_thread(client.execute_query, "SHOW FULL PROCESSLIST")
        active = [r for r in rows if r.get("Command", "").lower() != "sleep"]

        MAX_BYTES = 64 * 1024
        while (
            active and len(json.dumps(active, ensure_ascii=False, default=str).encode()) > MAX_BYTES
        ):
            active.pop()

        return {
            "processlist": active,
            "total_connections": len(rows),
            "active_connections": len(active),
            "response_size_limit_kb": 64,
        }
    except Exception as e:
        logger.error(f"query_db_processlist failed: {e}")
        return {
            "processlist": [],
            "total_connections": 0,
            "active_connections": 0,
            "error": str(e),
            "response_size_limit_kb": 64,
        }


async def query_db_slow_queries(**kwargs) -> Dict[str, Any]:
    """Query slow queries from processlist and information_schema.

    Filters queries running longer than threshold (default 5 seconds).
    """
    threshold = kwargs.get("threshold_seconds", 5)
    client = MySQLClient()

    try:
        rows = await asyncio.to_thread(client.execute_query, "SHOW FULL PROCESSLIST")
        slow = [
            r
            for r in rows
            if r.get("Time", 0) >= threshold and r.get("Command", "").lower() != "sleep"
        ]

        MAX_BYTES = 64 * 1024
        while slow and len(json.dumps(slow, ensure_ascii=False, default=str).encode()) > MAX_BYTES:
            slow.pop()

        return {
            "slow_queries": slow,
            "threshold_seconds": threshold,
            "count": len(slow),
            "response_size_limit_kb": 64,
        }
    except Exception as e:
        logger.error(f"query_db_slow_queries failed: {e}")
        return {
            "slow_queries": [],
            "threshold_seconds": threshold,
            "count": 0,
            "error": str(e),
            "response_size_limit_kb": 64,
        }


async def query_db_table_status(**kwargs) -> Dict[str, Any]:
    """Query table status (row count, size, fragmentation).

    Returns top 20 tables sorted by data length.
    """
    client = MySQLClient()

    try:
        rows = await asyncio.to_thread(client.execute_query, "SHOW TABLE STATUS")
        sorted_rows = sorted(rows, key=lambda r: r.get("Data_length", 0) or 0, reverse=True)[:20]

        MAX_BYTES = 64 * 1024
        while (
            sorted_rows
            and len(json.dumps(sorted_rows, ensure_ascii=False, default=str).encode()) > MAX_BYTES
        ):
            sorted_rows.pop()

        return {
            "table_status": sorted_rows,
            "total_tables": len(rows),
            "returned_tables": len(sorted_rows),
            "response_size_limit_kb": 64,
        }
    except Exception as e:
        logger.error(f"query_db_table_status failed: {e}")
        return {
            "table_status": [],
            "total_tables": 0,
            "returned_tables": 0,
            "error": str(e),
            "response_size_limit_kb": 64,
        }


async def query_db_variables(**kwargs) -> Dict[str, Any]:
    """Query key MySQL status variables.

    Filters SHOW GLOBAL STATUS for connection, buffer pool, lock metrics.
    """
    key_patterns = [
        "Threads_connected",
        "Threads_running",
        "Max_used_connections",
        "Innodb_buffer_pool_reads",
        "Innodb_buffer_pool_read_requests",
        "Innodb_buffer_pool_pages_total",
        "Innodb_buffer_pool_pages_free",
        "Innodb_row_lock_waits",
        "Innodb_row_lock_time",
        "Innodb_row_lock_time_avg",
        "Connections",
        "Aborted_connects",
        "Slow_queries",
        "Questions",
        "Uptime",
    ]

    client = MySQLClient()

    try:
        all_vars = await asyncio.to_thread(client.execute_query, "SHOW GLOBAL STATUS")
        filtered = {
            row["Variable_name"]: row["Value"]
            for row in all_vars
            if row.get("Variable_name") in key_patterns
        }

        buffer_pool_hit_rate = 0
        reads = float(filtered.get("Innodb_buffer_pool_reads", 0))
        read_requests = float(filtered.get("Innodb_buffer_pool_read_requests", 1))
        if read_requests > 0:
            buffer_pool_hit_rate = round((1 - reads / read_requests) * 100, 2)

        filtered["buffer_pool_hit_rate_pct"] = buffer_pool_hit_rate

        return {
            "variables": filtered,
            "response_size_limit_kb": 64,
        }
    except Exception as e:
        logger.error(f"query_db_variables failed: {e}")
        return {
            "variables": {},
            "error": str(e),
            "response_size_limit_kb": 64,
        }
