#!/usr/bin/env python3
"""
MetricsStore - Analytics storage using DuckDB.

Provides columnar analytics storage for NeoCortex metrics with fast queries
and aggregations. Falls back to SQLite if DuckDB is not available.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class MetricsBackend(str, Enum):
    """Available metrics backends."""

    DUCKDB = "duckdb"
    SQLITE = "sqlite"
    MEMORY = "memory"


@dataclass
class MetricRecord:
    """Single metric record."""

    metric_id: str
    metric_type: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class MetricsStore:
    """
    Analytics metrics store with DuckDB backend.

    Features:
    - Columnar storage for fast analytics
    - Time-series aggregation
    - Tag-based filtering
    - Automatic retention management
    - Fallback to SQLite if DuckDB unavailable
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        backend: MetricsBackend = MetricsBackend.DUCKDB,
        retention_days: int = 90,
    ):
        """
        Initialize metrics store.

        Args:
            db_path: Path to database file.
            backend: Preferred backend.
            retention_days: Days to retain metrics.
        """
        if db_path is None:
            from ..config import get_config

            config = get_config()
            db_path = config.project_root / ".neocortex" / "metrics" / "metrics.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path

        # Select available backend
        self.backend = self._select_backend(backend)
        self.retention_days = retention_days

        # Initialize database
        self._init_database()

        logger.info(f"MetricsStore initialized with backend: {self.backend.value}")

    def _select_backend(self, preferred: MetricsBackend) -> MetricsBackend:
        """
        Select the best available backend.

        Args:
            preferred: Preferred backend.

        Returns:
            Available backend.
        """
        # Check DuckDB availability
        if preferred == MetricsBackend.DUCKDB:
            try:
                import duckdb

                # Test DuckDB
                conn = duckdb.connect(":memory:")
                conn.execute("SELECT 1")
                conn.close()
                logger.info("DuckDB backend available")
                return MetricsBackend.DUCKDB
            except ImportError:
                logger.warning("DuckDB not available, falling back to SQLite")
            except Exception as e:
                logger.warning(f"DuckDB initialization failed: {e}")

        # Default to SQLite
        return MetricsBackend.SQLITE

    def _init_database(self):
        """Initialize database schema."""
        if self.backend == MetricsBackend.DUCKDB:
            self._init_duckdb()
        else:
            self._init_sqlite()

        # Create tables if they don't exist
        self._create_tables()

    def _init_duckdb(self):
        """Initialize DuckDB connection."""
        try:
            import duckdb

            self.conn = duckdb.connect(str(self.db_path))
            logger.info("DuckDB connection established")
        except Exception as e:
            logger.error(f"Failed to initialize DuckDB: {e}")
            # Fall back to SQLite
            self.backend = MetricsBackend.SQLITE
            self._init_sqlite()

    def _init_sqlite(self):
        """Initialize SQLite connection."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        logger.info("SQLite connection established")

    def _create_tables(self):
        """Create metrics tables."""
        # Metrics table - compatible syntax for both DuckDB and SQLite
        if self.backend == MetricsBackend.DUCKDB:
            # DuckDB uses INTEGER PRIMARY KEY (auto-increment)
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY,
                metric_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        else:
            # SQLite also uses INTEGER PRIMARY KEY (auto-increment)
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY,
                metric_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                tags_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

        # Create indexes
        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_metrics_metric_id 
        ON metrics(metric_id)
        """)

        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
        ON metrics(timestamp DESC)
        """)

        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_metrics_type 
        ON metrics(metric_type)
        """)

        # Aggregated metrics table (pre-computed aggregates)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS metric_aggregates (
            metric_id TEXT NOT NULL,
            aggregation_type TEXT NOT NULL,  -- 'hourly', 'daily', 'weekly'
            period_start TIMESTAMP NOT NULL,
            period_end TIMESTAMP NOT NULL,
            count INTEGER NOT NULL,
            sum_value REAL NOT NULL,
            avg_value REAL NOT NULL,
            min_value REAL NOT NULL,
            max_value REAL NOT NULL,
            stddev_value REAL,
            tags_json TEXT NOT NULL,
            PRIMARY KEY (metric_id, aggregation_type, period_start)
        )
        """)

        # Domain-specific tables for NeoCortex analytics
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_token_usage (
            date DATE NOT NULL,
            model TEXT NOT NULL,
            agent TEXT,
            cache_hit INTEGER DEFAULT 0,
            cache_miss INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            PRIMARY KEY (date, model, agent)
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS cost_summary (
            date DATE NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            cost_real DECIMAL(10,4) DEFAULT 0.0,
            cost_saved DECIMAL(10,4) DEFAULT 0.0,
            cost_without_cache DECIMAL(10,4) DEFAULT 0.0,
            PRIMARY KEY (date, provider, model)
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_activity (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            agent_id TEXT NOT NULL,
            action TEXT NOT NULL,  -- 'spawn', 'task_completed', 'task_failed', 'stopped'
            details_json TEXT,
            metadata_json TEXT
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS pulse_health (
            timestamp TIMESTAMP NOT NULL,
            event_type TEXT NOT NULL,  -- 'checkpoint', 'pruning', 'consolidation', 'akl_assessment'
            status TEXT NOT NULL,      -- 'success', 'failure', 'warning'
            duration_ms INTEGER,
            details_json TEXT,
            PRIMARY KEY (timestamp, event_type)
        )
        """)

        # Create indexes for domain tables
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_token_usage_date ON daily_token_usage(date DESC)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_token_usage_model ON daily_token_usage(model)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_cost_summary_date ON cost_summary(date DESC)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_agent_activity_agent ON agent_activity(agent_id)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_agent_activity_timestamp ON agent_activity(timestamp DESC)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_pulse_health_timestamp ON pulse_health(timestamp DESC)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_pulse_health_event ON pulse_health(event_type)"
        )

        self.conn.commit()

    def validate_tables(self) -> bool:
        """
        Validate that all required tables exist and have correct schema.

        Returns:
            True if all tables are valid, False otherwise.
        """
        try:
            required_tables = [
                "metrics",
                "metric_aggregates",
                "daily_token_usage",
                "cost_summary",
                "agent_activity",
                "pulse_health",
            ]

            cursor = self.conn.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (?, ?, ?, ?, ?, ?)
            """,
                tuple(required_tables),
            )

            existing_tables = {row[0] for row in cursor.fetchall()}

            if len(existing_tables) != len(required_tables):
                missing = set(required_tables) - existing_tables
                logger.warning(f"Missing metrics tables: {missing}")
                return False

            logger.debug("All metrics tables validated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to validate metrics tables: {e}")
            return False

    def insert_metric(
        self,
        metric_id: str,
        metric_type: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Insert a metric record.

        Args:
            metric_id: Metric identifier.
            metric_type: Metric type (e.g., 'latency', 'throughput', 'error_rate').
            value: Metric value.
            tags: Key-value tags for filtering.
            metadata: Additional metadata.
            timestamp: Metric timestamp (defaults to now).

        Returns:
            True if successful.
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()

            tags_json = json.dumps(tags or {})
            metadata_json = json.dumps(metadata or {})

            self.conn.execute(
                """
            INSERT INTO metrics 
            (metric_id, metric_type, value, timestamp, tags_json, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    metric_id,
                    metric_type,
                    value,
                    timestamp.isoformat(),
                    tags_json,
                    metadata_json,
                ),
            )

            self.conn.commit()
            logger.debug(f"Inserted metric: {metric_id}={value}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert metric: {e}")
            return False

    # Domain-specific recording methods
    def record_token_usage(
        self,
        date: datetime,
        model: str,
        agent: Optional[str] = None,
        cache_hit: int = 0,
        cache_miss: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
    ) -> bool:
        """
        Record token usage for a specific model/agent on a given date.

        Uses UPSERT to update existing records for the same date/model/agent.
        """
        try:
            # Convert date to DATE type (strip time component)
            if isinstance(date, datetime):
                date_str = date.date().isoformat()
            else:
                date_str = date.isoformat() if hasattr(date, "isoformat") else str(date)

            self.conn.execute(
                """
            INSERT INTO daily_token_usage 
            (date, model, agent, cache_hit, cache_miss, output_tokens, total_tokens)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (date, model, agent) DO UPDATE SET
                cache_hit = daily_token_usage.cache_hit + excluded.cache_hit,
                cache_miss = daily_token_usage.cache_miss + excluded.cache_miss,
                output_tokens = daily_token_usage.output_tokens + excluded.output_tokens,
                total_tokens = daily_token_usage.total_tokens + excluded.total_tokens
            """,
                (
                    date_str,
                    model,
                    agent,
                    cache_hit,
                    cache_miss,
                    output_tokens,
                    total_tokens,
                ),
            )

            self.conn.commit()
            logger.debug(f"Recorded token usage: {date_str}, {model}, {agent}")
            return True
        except Exception as e:
            logger.error(f"Failed to record token usage: {e}")
            return False

    def record_cost_summary(
        self,
        date: datetime,
        provider: str,
        model: str,
        cost_real: float = 0.0,
        cost_saved: float = 0.0,
        cost_without_cache: float = 0.0,
    ) -> bool:
        """Record cost summary for a provider/model on a given date."""
        try:
            date_str = date.date().isoformat() if isinstance(date, datetime) else date
            self.conn.execute(
                """
            INSERT INTO cost_summary 
            (date, provider, model, cost_real, cost_saved, cost_without_cache)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (date, provider, model) DO UPDATE SET
                cost_real = excluded.cost_real,
                cost_saved = excluded.cost_saved,
                cost_without_cache = excluded.cost_without_cache
            """,
                (date_str, provider, model, cost_real, cost_saved, cost_without_cache),
            )

            self.conn.commit()
            logger.debug(f"Recorded cost summary: {date_str}, {provider}, {model}")
            return True
        except Exception as e:
            logger.error(f"Failed to record cost summary: {e}")
            return False

    def record_agent_activity(
        self,
        agent_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Record an agent activity event."""
        try:
            if timestamp is None:
                timestamp = datetime.now()

            details_json = json.dumps(details or {})
            metadata_json = json.dumps(metadata or {})

            self.conn.execute(
                """
            INSERT INTO agent_activity 
            (timestamp, agent_id, action, details_json, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            """,
                (timestamp.isoformat(), agent_id, action, details_json, metadata_json),
            )

            self.conn.commit()
            logger.debug(f"Recorded agent activity: {agent_id}, {action}")
            return True
        except Exception as e:
            logger.error(f"Failed to record agent activity: {e}")
            return False

    def record_pulse_health(
        self,
        event_type: str,
        status: str,
        duration_ms: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Record a PulseScheduler health event."""
        try:
            if timestamp is None:
                timestamp = datetime.now()

            details_json = json.dumps(details or {})

            self.conn.execute(
                """
            INSERT INTO pulse_health 
            (timestamp, event_type, status, duration_ms, details_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (timestamp, event_type) DO UPDATE SET
                status = excluded.status,
                duration_ms = excluded.duration_ms,
                details_json = excluded.details_json
            """,
                (timestamp.isoformat(), event_type, status, duration_ms, details_json),
            )

            self.conn.commit()
            logger.debug(f"Recorded pulse health: {event_type}, {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to record pulse health: {e}")
            return False

    # Query methods for reports
    def get_daily_token_usage(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get daily token usage aggregated by date."""
        try:
            query = """
            SELECT 
                date,
                model,
                agent,
                SUM(cache_hit) as cache_hit,
                SUM(cache_miss) as cache_miss,
                SUM(output_tokens) as output_tokens,
                SUM(total_tokens) as total_tokens
            FROM daily_token_usage
            WHERE 1=1
            """
            params = []

            if start_date:
                query += " AND date >= ?"
                params.append(
                    start_date.date().isoformat()
                    if isinstance(start_date, datetime)
                    else start_date
                )

            if end_date:
                query += " AND date <= ?"
                params.append(
                    end_date.date().isoformat()
                    if isinstance(end_date, datetime)
                    else end_date
                )

            if model:
                query += " AND model = ?"
                params.append(model)

            if agent:
                query += " AND agent = ?"
                params.append(agent)

            query += " GROUP BY date, model, agent ORDER BY date DESC"

            cursor = self.conn.execute(query, params)
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))

            return results
        except Exception as e:
            logger.error(f"Failed to get daily token usage: {e}")
            return []

    def get_cost_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get cost summary aggregated by date."""
        try:
            query = """
            SELECT 
                date,
                provider,
                model,
                SUM(cost_real) as cost_real,
                SUM(cost_saved) as cost_saved,
                SUM(cost_without_cache) as cost_without_cache
            FROM cost_summary
            WHERE 1=1
            """
            params = []

            if start_date:
                query += " AND date >= ?"
                params.append(
                    start_date.date().isoformat()
                    if isinstance(start_date, datetime)
                    else start_date
                )

            if end_date:
                query += " AND date <= ?"
                params.append(
                    end_date.date().isoformat()
                    if isinstance(end_date, datetime)
                    else end_date
                )

            if provider:
                query += " AND provider = ?"
                params.append(provider)

            if model:
                query += " AND model = ?"
                params.append(model)

            query += " GROUP BY date, provider, model ORDER BY date DESC"

            cursor = self.conn.execute(query, params)
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))

            return results
        except Exception as e:
            logger.error(f"Failed to get cost summary: {e}")
            return []

    def get_agent_activity(
        self,
        agent_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        action: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get agent activity events."""
        try:
            query = "SELECT * FROM agent_activity WHERE 1=1"
            params = []

            if agent_id:
                query += " AND agent_id = ?"
                params.append(agent_id)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            if action:
                query += " AND action = ?"
                params.append(action)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = self.conn.execute(query, params)
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON fields
                if data.get("details_json"):
                    data["details"] = json.loads(data["details_json"])
                if data.get("metadata_json"):
                    data["metadata"] = json.loads(data["metadata_json"])
                results.append(data)

            return results
        except Exception as e:
            logger.error(f"Failed to get agent activity: {e}")
            return []

    def get_pulse_health(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get PulseScheduler health events."""
        try:
            query = "SELECT * FROM pulse_health WHERE 1=1"
            params = []

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = self.conn.execute(query, params)
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                if data.get("details_json"):
                    data["details"] = json.loads(data["details_json"])
                results.append(data)

            return results
        except Exception as e:
            logger.error(f"Failed to get pulse health: {e}")
            return []

    def query_metrics(
        self,
        metric_id: Optional[str] = None,
        metric_type: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[MetricRecord]:
        """
        Query metrics with filters.

        Args:
            metric_id: Filter by metric ID.
            metric_type: Filter by metric type.
            tags: Filter by tags (AND logic).
            start_time: Start of time range.
            end_time: End of time range.
            limit: Maximum results.
            offset: Result offset.

        Returns:
            List of matching metric records.
        """
        try:
            query = "SELECT * FROM metrics WHERE 1=1"
            params = []

            if metric_id:
                query += " AND metric_id = ?"
                params.append(metric_id)

            if metric_type:
                query += " AND metric_type = ?"
                params.append(metric_type)

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())

            # Tag filtering (requires JSON parsing)
            if tags:
                for key, value in tags.items():
                    # SQLite JSON support
                    if self.backend == MetricsBackend.SQLITE:
                        query += f" AND json_extract(tags_json, '$.{key}') = ?"
                    else:  # DuckDB
                        query += f" AND tags_json->>'{key}' = ?"
                    params.append(value)

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = self.conn.execute(query, params)
            results = []

            for row in cursor.fetchall():
                record = MetricRecord(
                    metric_id=row["metric_id"],
                    metric_type=row["metric_type"],
                    value=row["value"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    tags=json.loads(row["tags_json"]),
                    metadata=json.loads(row["metadata_json"]),
                )
                results.append(record)

            return results

        except Exception as e:
            logger.error(f"Failed to query metrics: {e}")
            return []

    def aggregate_metrics(
        self,
        metric_id: str,
        aggregation_type: str = "hourly",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Aggregate metrics over time periods.

        Args:
            metric_id: Metric identifier.
            aggregation_type: 'hourly', 'daily', 'weekly', 'monthly'.
            start_time: Start of time range.
            end_time: End of time range.

        Returns:
            Aggregation results.
        """
        try:
            if start_time is None:
                start_time = datetime.now() - timedelta(days=7)
            if end_time is None:
                end_time = datetime.now()

            # Determine time grouping
            if aggregation_type == "hourly":
                time_format = "%Y-%m-%d %H:00:00"
                group_sql = "strftime('%Y-%m-%d %H:00:00', timestamp)"
            elif aggregation_type == "daily":
                time_format = "%Y-%m-%d 00:00:00"
                group_sql = "strftime('%Y-%m-%d 00:00:00', timestamp)"
            elif aggregation_type == "weekly":
                time_format = "%Y-%W"
                group_sql = "strftime('%Y-%W', timestamp)"
            elif aggregation_type == "monthly":
                time_format = "%Y-%m-01"
                group_sql = "strftime('%Y-%m-01', timestamp)"
            else:
                raise ValueError(f"Unknown aggregation type: {aggregation_type}")

            query = f"""
            SELECT 
                {group_sql} as period,
                COUNT(*) as count,
                SUM(value) as sum_value,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                AVG(value*value) - AVG(value)*AVG(value) as variance
            FROM metrics
            WHERE metric_id = ?
            AND timestamp >= ?
            AND timestamp <= ?
            GROUP BY period
            ORDER BY period
            """

            cursor = self.conn.execute(
                query,
                (
                    metric_id,
                    start_time.isoformat(),
                    end_time.isoformat(),
                ),
            )

            results = []
            for row in cursor.fetchall():
                period = row["period"]
                variance = row["variance"] or 0
                stddev = variance**0.5 if variance > 0 else 0

                results.append(
                    {
                        "period": period,
                        "count": row["count"],
                        "sum": row["sum_value"],
                        "average": row["avg_value"],
                        "minimum": row["min_value"],
                        "maximum": row["max_value"],
                        "stddev": stddev,
                    }
                )

            return {
                "metric_id": metric_id,
                "aggregation_type": aggregation_type,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "results": results,
            }

        except Exception as e:
            logger.error(f"Failed to aggregate metrics: {e}")
            return {}

    def compute_aggregates(self, force_recompute: bool = False) -> int:
        """
        Compute pre-aggregated metrics for faster queries.

        Args:
            force_recompute: Force recomputation of all aggregates.

        Returns:
            Number of aggregates computed.
        """
        try:
            count = 0

            # For each aggregation type
            for agg_type in ["hourly", "daily"]:
                # Determine time range
                if agg_type == "hourly":
                    period_start = "strftime('%Y-%m-%d %H:00:00', timestamp)"
                    period_end = (
                        "datetime(strftime('%Y-%m-%d %H:00:00', timestamp), '+1 hour')"
                    )
                else:  # daily
                    period_start = "date(timestamp)"
                    period_end = "date(timestamp, '+1 day')"

                # Get unique metric IDs
                cursor = self.conn.execute("""
                SELECT DISTINCT metric_id FROM metrics
                WHERE timestamp >= date('now', '-30 days')
                """)

                metric_ids = [row[0] for row in cursor.fetchall()]

                for metric_id in metric_ids:
                    # Check if aggregate already exists
                    if not force_recompute:
                        cursor = self.conn.execute(
                            """
                        SELECT COUNT(*) FROM metric_aggregates
                        WHERE metric_id = ? AND aggregation_type = ?
                        """,
                            (metric_id, agg_type),
                        )

                        if cursor.fetchone()[0] > 0:
                            continue

                    # Compute aggregate
                    query = f"""
                    INSERT INTO metric_aggregates
                    SELECT 
                        metric_id,
                        '{agg_type}' as aggregation_type,
                        {period_start} as period_start,
                        {period_end} as period_end,
                        COUNT(*) as count,
                        SUM(value) as sum_value,
                        AVG(value) as avg_value,
                        MIN(value) as min_value,
                        MAX(value) as max_value,
                        AVG(value*value) - AVG(value)*AVG(value) as stddev_value,
                        tags_json
                    FROM metrics
                    WHERE metric_id = ?
                    GROUP BY metric_id, {period_start}, tags_json
                    ON CONFLICT (metric_id, aggregation_type, period_start) 
                    DO UPDATE SET
                        count = excluded.count,
                        sum_value = excluded.sum_value,
                        avg_value = excluded.avg_value,
                        min_value = excluded.min_value,
                        max_value = excluded.max_value,
                        stddev_value = excluded.stddev_value,
                        tags_json = excluded.tags_json
                    """

                    self.conn.execute(query, (metric_id,))
                    count += 1

            self.conn.commit()
            logger.info(f"Computed {count} metric aggregates")
            return count

        except Exception as e:
            logger.error(f"Failed to compute aggregates: {e}")
            return 0

    def cleanup_old_metrics(self) -> int:
        """
        Remove metrics older than retention period.

        Returns:
            Number of metrics removed.
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)

            cursor = self.conn.execute(
                """
            DELETE FROM metrics 
            WHERE timestamp < ?
            """,
                (cutoff_date.isoformat(),),
            )

            deleted_count = cursor.rowcount
            self.conn.commit()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old metrics")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to clean up old metrics: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get metrics store statistics."""
        try:
            cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_metrics,
                COUNT(DISTINCT metric_id) as unique_metrics,
                MIN(timestamp) as oldest_metric,
                MAX(timestamp) as newest_metric
            FROM metrics
            """)

            row = cursor.fetchone()

            cursor = self.conn.execute("""
            SELECT metric_type, COUNT(*) as count
            FROM metrics
            GROUP BY metric_type
            ORDER BY count DESC
            """)

            metrics_by_type = {}
            for type_row in cursor.fetchall():
                metrics_by_type[type_row["metric_type"]] = type_row["count"]

            return {
                "backend": self.backend.value,
                "total_metrics": row["total_metrics"] if row else 0,
                "unique_metrics": row["unique_metrics"] if row else 0,
                "oldest_metric": row["oldest_metric"] if row else None,
                "newest_metric": row["newest_metric"] if row else None,
                "metrics_by_type": metrics_by_type,
                "retention_days": self.retention_days,
                "db_path": str(self.db_path),
            }

        except Exception as e:
            logger.error(f"Failed to get metrics stats: {e}")
            return {}

    def close(self):
        """Close database connection."""
        try:
            if hasattr(self, "conn"):
                self.conn.close()
                logger.info("MetricsStore connection closed")
        except Exception as e:
            logger.warning(f"Error closing MetricsStore: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()


def create_metrics_store(
    db_path: Optional[Path] = None,
    backend: MetricsBackend = MetricsBackend.DUCKDB,
    retention_days: int = 90,
) -> MetricsStore:
    """
    Create a MetricsStore instance.

    Args:
        db_path: Path to database file.
        backend: Preferred backend.
        retention_days: Days to retain metrics.

    Returns:
        MetricsStore instance.
    """
    return MetricsStore(
        db_path=db_path,
        backend=backend,
        retention_days=retention_days,
    )
