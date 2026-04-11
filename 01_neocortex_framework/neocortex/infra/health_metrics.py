#!/usr/bin/env python3
"""
Health check and metrics collection for NeoCortex infrastructure.

Provides system health monitoring and performance metrics collection.
"""

import json
import logging
import time
import psutil
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Single health check result."""

    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """Single metric measurement."""

    name: str
    value: float
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class HealthChecker:
    """
    Health check manager for NeoCortex components.

    Performs periodic health checks on stores, services, and system resources.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize health checker.

        Args:
            config: Health check configuration.
        """
        self.config = config or {}
        self.checks: List[Callable[[], HealthCheck]] = []
        self.results: Dict[str, HealthCheck] = {}
        self.last_run: Optional[datetime] = None

        # Register default checks
        self._register_default_checks()

    def _register_default_checks(self):
        """Register default health checks."""
        self.register_check("system_resources", self.check_system_resources)
        self.register_check("python_environment", self.check_python_environment)
        self.register_check("neocortex_paths", self.check_neocortex_paths)

    def register_check(self, name: str, check_func: Callable[[], HealthCheck]):
        """
        Register a health check function.

        Args:
            name: Check name.
            check_func: Function returning HealthCheck.
        """
        self.checks.append(lambda name=name, func=check_func: func())

    def run_checks(self) -> Dict[str, HealthCheck]:
        """
        Run all registered health checks.

        Returns:
            Dictionary of check results keyed by check name.
        """
        logger.info("Running health checks...")

        results = {}
        for check_func in self.checks:
            start_time = time.time()
            try:
                result = check_func()
                result.duration_ms = (time.time() - start_time) * 1000
                results[result.name] = result

                if result.status == HealthStatus.UNHEALTHY:
                    logger.error(
                        f"Health check failed: {result.name} - {result.message}"
                    )
                elif result.status == HealthStatus.DEGRADED:
                    logger.warning(
                        f"Health check degraded: {result.name} - {result.message}"
                    )
                else:
                    logger.debug(f"Health check passed: {result.name}")

            except Exception as e:
                logger.error(f"Health check error: {e}")
                results[check_func.__name__] = HealthCheck(
                    name=check_func.__name__,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed with exception: {e}",
                    duration_ms=(time.time() - start_time) * 1000,
                )

        self.results = results
        self.last_run = datetime.now()

        return results

    def get_overall_status(self) -> HealthStatus:
        """
        Get overall health status based on all checks.

        Returns:
            Overall health status.
        """
        if not self.results:
            return HealthStatus.UNKNOWN

        statuses = [check.status for check in self.results.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def check_system_resources(self) -> HealthCheck:
        """Check system resources (CPU, memory, disk)."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(Path.cwd())

            checks = []

            # CPU check
            if cpu_percent > 90:
                checks.append(f"CPU usage high: {cpu_percent:.1f}%")
            elif cpu_percent > 70:
                checks.append(f"CPU usage elevated: {cpu_percent:.1f}%")

            # Memory check
            if memory.percent > 90:
                checks.append(f"Memory usage high: {memory.percent:.1f}%")
            elif memory.percent > 75:
                checks.append(f"Memory usage elevated: {memory.percent:.1f}%")

            # Disk check
            if disk.percent > 90:
                checks.append(f"Disk usage high: {disk.percent:.1f}%")
            elif disk.percent > 80:
                checks.append(f"Disk usage elevated: {disk.percent:.1f}%")

            if checks:
                status = (
                    HealthStatus.DEGRADED if len(checks) < 3 else HealthStatus.UNHEALTHY
                )
                message = "; ".join(checks)
            else:
                status = HealthStatus.HEALTHY
                message = "System resources within normal limits"

            return HealthCheck(
                name="system_resources",
                status=status,
                message=message,
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / 1024**3,
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / 1024**3,
                },
            )

        except Exception as e:
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check system resources: {e}",
            )

    def check_python_environment(self) -> HealthCheck:
        """Check Python environment and dependencies."""
        try:
            import sys
            import importlib.metadata as metadata

            checks = []
            required_packages = [
                "mcp",
                "msgspec",
                "diskcache",
                "sqlite-utils",
                "psutil",
            ]

            for package in required_packages:
                try:
                    metadata.version(package)
                except metadata.PackageNotFoundError:
                    checks.append(f"Package missing: {package}")

            python_version = sys.version_info
            if python_version < (3, 8):
                checks.append(
                    f"Python version too old: {python_version.major}.{python_version.minor}"
                )

            if checks:
                status = HealthStatus.DEGRADED
                message = "; ".join(checks)
            else:
                status = HealthStatus.HEALTHY
                message = "Python environment OK"

            return HealthCheck(
                name="python_environment",
                status=status,
                message=message,
                metadata={
                    "python_version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                    "platform": platform.platform(),
                },
            )

        except Exception as e:
            return HealthCheck(
                name="python_environment",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check Python environment: {e}",
            )

    def check_neocortex_paths(self) -> HealthCheck:
        """Check NeoCortex critical paths."""
        try:
            from ..config import get_config

            config = get_config()

            checks = []
            metadata = {}

            # Check critical directories
            critical_dirs = [
                ("core_central", config.core_central),
                ("archive", config.archive_path),
                ("backup", config.backup_path),
                ("docs", config.docs_path),
            ]

            for name, path in critical_dirs:
                if path.exists():
                    metadata[f"{name}_exists"] = True
                    # Check if directory is writable
                    try:
                        test_file = path / ".health_check"
                        test_file.touch(exist_ok=True)
                        test_file.unlink(missing_ok=True)
                        metadata[f"{name}_writable"] = True
                    except Exception:
                        metadata[f"{name}_writable"] = False
                        checks.append(f"Directory not writable: {name}")
                else:
                    metadata[f"{name}_exists"] = False
                    checks.append(f"Directory missing: {name}")

            # Check critical files
            critical_files = [
                ("cortex", config.cortex_path),
                ("ledger", config.ledger_path),
            ]

            for name, path in critical_files:
                metadata[f"{name}_exists"] = path.exists()
                if not path.exists():
                    checks.append(f"File missing: {name}")

            if checks:
                status = (
                    HealthStatus.DEGRADED if len(checks) < 3 else HealthStatus.UNHEALTHY
                )
                message = "; ".join(checks)
            else:
                status = HealthStatus.HEALTHY
                message = "All critical paths accessible"

            return HealthCheck(
                name="neocortex_paths",
                status=status,
                message=message,
                metadata=metadata,
            )

        except Exception as e:
            return HealthCheck(
                name="neocortex_paths",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check NeoCortex paths: {e}",
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert health checker state to dictionary."""
        return {
            "overall_status": self.get_overall_status().value,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "results": {
                name: {
                    "status": check.status.value,
                    "message": check.message,
                    "duration_ms": check.duration_ms,
                    "timestamp": check.timestamp.isoformat(),
                    "metadata": check.metadata,
                }
                for name, check in self.results.items()
            },
        }


class MetricsCollector:
    """
    Metrics collector for NeoCortex performance monitoring.

    Collects and aggregates performance metrics from various components.
    """

    def __init__(self, retention_days: int = 7):
        """
        Initialize metrics collector.

        Args:
            retention_days: Number of days to retain metrics.
        """
        self.retention_days = retention_days
        self.metrics: List[Metric] = []
        self.start_time = datetime.now()

        # Metric categories
        self.categories = {
            "performance": [],
            "resources": [],
            "business": [],
            "errors": [],
        }

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None,
        category: str = "performance",
    ):
        """
        Record a metric.

        Args:
            name: Metric name.
            value: Metric value.
            unit: Unit of measurement.
            tags: Optional tags.
            category: Metric category.
        """
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {},
        )

        self.metrics.append(metric)
        if category in self.categories:
            self.categories[category].append(metric)

        logger.debug(f"Recorded metric: {name}={value}{unit}")

    def record_latency(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Record operation latency.

        Args:
            operation: Operation name.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            tags: Additional tags.
        """
        all_tags = tags or {}
        all_tags["operation"] = operation
        all_tags["success"] = str(success)

        self.record_metric(
            name="operation_latency",
            value=duration_ms,
            unit="ms",
            tags=all_tags,
            category="performance",
        )

        if not success:
            self.record_metric(
                name="operation_error",
                value=1,
                unit="count",
                tags={"operation": operation},
                category="errors",
            )

    def record_cache_stats(
        self,
        cache_name: str,
        hits: int,
        misses: int,
        size: int,
    ):
        """
        Record cache statistics.

        Args:
            cache_name: Cache identifier.
            hits: Number of cache hits.
            misses: Number of cache misses.
            size: Current cache size.
        """
        total = hits + misses
        hit_ratio = hits / total if total > 0 else 0

        self.record_metric(
            name="cache_hit_ratio",
            value=hit_ratio,
            unit="ratio",
            tags={"cache": cache_name},
            category="performance",
        )

        self.record_metric(
            name="cache_size",
            value=size,
            unit="items",
            tags={"cache": cache_name},
            category="resources",
        )

    def record_llm_metrics(
        self,
        provider: str,
        model: str,
        tokens_used: int,
        duration_ms: float,
        success: bool,
    ):
        """
        Record LLM API metrics.

        Args:
            provider: LLM provider.
            model: Model name.
            tokens_used: Number of tokens used.
            duration_ms: Request duration.
            success: Whether request succeeded.
        """
        tags = {
            "provider": provider,
            "model": model,
            "success": str(success),
        }

        self.record_metric(
            name="llm_tokens",
            value=tokens_used,
            unit="tokens",
            tags=tags,
            category="business",
        )

        self.record_metric(
            name="llm_latency",
            value=duration_ms,
            unit="ms",
            tags=tags,
            category="performance",
        )

        if not success:
            self.record_metric(
                name="llm_errors",
                value=1,
                unit="count",
                tags=tags,
                category="errors",
            )

    def get_recent_metrics(
        self,
        since: Optional[datetime] = None,
        category: Optional[str] = None,
    ) -> List[Metric]:
        """
        Get recent metrics.

        Args:
            since: Only return metrics since this time.
            category: Filter by category.

        Returns:
            List of matching metrics.
        """
        if since is None:
            since = datetime.now() - timedelta(days=1)

        filtered = [m for m in self.metrics if m.timestamp >= since]

        if category and category in self.categories:
            filtered = [m for m in filtered if m in self.categories[category]]

        return filtered

    def aggregate_metrics(
        self,
        since: Optional[datetime] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate metrics by name.

        Args:
            since: Only aggregate metrics since this time.

        Returns:
            Dictionary of aggregated metrics.
        """
        recent = self.get_recent_metrics(since)

        aggregated = {}
        for metric in recent:
            if metric.name not in aggregated:
                aggregated[metric.name] = {
                    "values": [],
                    "units": metric.unit,
                    "tags": set(),
                }

            aggregated[metric.name]["values"].append(metric.value)
            if metric.tags:
                aggregated[metric.name]["tags"].update(
                    f"{k}={v}" for k, v in metric.tags.items()
                )

        # Calculate statistics
        results = {}
        for name, data in aggregated.items():
            values = data["values"]
            if not values:
                continue

            results[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "sum": sum(values),
                "unit": data["units"],
                "tags": list(data["tags"]),
                "last_value": values[-1],
            }

        return results

    def cleanup_old_metrics(self) -> int:
        """
        Remove metrics older than retention period.

        Returns:
            Number of metrics removed.
        """
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        old_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]

        # Clean up categories too
        for category in self.categories:
            self.categories[category] = [
                m for m in self.categories[category] if m.timestamp >= cutoff
            ]

        removed = old_count - len(self.metrics)
        if removed > 0:
            logger.info(f"Cleaned up {removed} old metrics")

        return removed

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics collector state to dictionary."""
        return {
            "total_metrics": len(self.metrics),
            "start_time": self.start_time.isoformat(),
            "categories": {
                category: len(metrics) for category, metrics in self.categories.items()
            },
            "recent_aggregates": self.aggregate_metrics(
                since=datetime.now() - timedelta(hours=1)
            ),
        }


def create_health_checker(config: Optional[Dict[str, Any]] = None) -> HealthChecker:
    """
    Create a HealthChecker instance.

    Args:
        config: Health check configuration.

    Returns:
        HealthChecker instance.
    """
    return HealthChecker(config)


def create_metrics_collector(retention_days: int = 7) -> MetricsCollector:
    """
    Create a MetricsCollector instance.

    Args:
        retention_days: Number of days to retain metrics.

    Returns:
        MetricsCollector instance.
    """
    return MetricsCollector(retention_days)
