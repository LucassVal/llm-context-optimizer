#!/usr/bin/env python3
"""
Performance profiler for NeoCortex infrastructure.

Provides detailed performance profiling, bottleneck detection, and optimization
recommendations for NeoCortex components.
"""

import cProfile
import pstats
import time
import tracemalloc
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union, TextIO
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
from contextlib import contextmanager
import functools

logger = logging.getLogger(__name__)


class ProfileMode(str, Enum):
    """Profiling modes."""

    CPU = "cpu"
    MEMORY = "memory"
    COMBINED = "combined"
    CUSTOM = "custom"


@dataclass
class ProfileResult:
    """Profiling result."""

    name: str
    duration_ms: float = 0.0
    memory_peak_bytes: int = 0
    memory_increment_bytes: int = 0
    call_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class Bottleneck:
    """Performance bottleneck identification."""

    location: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    impact: str
    recommendation: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class Profiler:
    """
    Advanced performance profiler for NeoCortex.

    Features:
    - CPU profiling with cProfile
    - Memory profiling with tracemalloc
    - Bottleneck detection
    - Optimization recommendations
    - Historical performance tracking
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize profiler.

        Args:
            output_dir: Directory for profile reports.
        """
        if output_dir is None:
            from ..config import get_config

            config = get_config()
            output_dir = config.project_root / ".neocortex" / "profiles"

        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir

        self.results: Dict[str, ProfileResult] = {}
        self.bottlenecks: List[Bottleneck] = []

        # Profiling state
        self._cpu_profiler = None
        self._memory_snapshot = None

        logger.info(f"Profiler initialized at {output_dir}")

    @contextmanager
    def profile(
        self,
        name: str,
        mode: ProfileMode = ProfileMode.CPU,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager for profiling code blocks.

        Args:
            name: Profile name.
            mode: Profiling mode.
            metadata: Additional metadata.

        Yields:
            Profile context.
        """
        start_time = time.time()

        # Setup profiling based on mode
        if mode in [ProfileMode.CPU, ProfileMode.COMBINED]:
            self._cpu_profiler = cProfile.Profile()
            self._cpu_profiler.enable()

        if mode in [ProfileMode.MEMORY, ProfileMode.COMBINED]:
            tracemalloc.start()
            self._memory_snapshot = tracemalloc.take_snapshot()

        try:
            yield
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Collect results based on mode
            memory_peak = 0
            memory_increment = 0
            call_count = 0

            if mode in [ProfileMode.CPU, ProfileMode.COMBINED] and self._cpu_profiler:
                self._cpu_profiler.disable()
                stats = pstats.Stats(self._cpu_profiler)
                call_count = stats.total_calls

            if (
                mode in [ProfileMode.MEMORY, ProfileMode.COMBINED]
                and self._memory_snapshot
            ):
                current_snapshot = tracemalloc.take_snapshot()
                memory_peak = tracemalloc.get_traced_memory()[1]

                # Calculate memory increment
                top_stats = current_snapshot.compare_to(self._memory_snapshot, "lineno")
                memory_increment = sum(stat.size_diff for stat in top_stats)
                tracemalloc.stop()

            # Store result
            result = ProfileResult(
                name=name,
                duration_ms=duration_ms,
                memory_peak_bytes=memory_peak,
                memory_increment_bytes=memory_increment,
                call_count=call_count,
                metadata=metadata or {},
            )

            self.results[name] = result
            logger.debug(
                f"Profiled '{name}': {duration_ms:.2f}ms, {memory_peak:,}B peak"
            )

            # Reset state
            self._cpu_profiler = None
            self._memory_snapshot = None

    def profile_function(
        self,
        mode: ProfileMode = ProfileMode.CPU,
        name: Optional[str] = None,
    ):
        """
        Decorator for profiling functions.

        Args:
            mode: Profiling mode.
            name: Custom profile name (uses function name if None).

        Returns:
            Decorator function.
        """

        def decorator(func):
            profile_name = name or func.__name__

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.profile(
                    profile_name,
                    mode,
                    metadata={
                        "function": func.__name__,
                        "module": func.__module__,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs),
                    },
                ):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def profile_store_operations(self, store_name: str):
        """
        Profile common store operations.

        Args:
            store_name: Name of store to profile.

        Returns:
            Dictionary of operation profiles.
        """
        results = {}

        # Import store based on name
        try:
            if store_name == "ledger":
                from .ledger_store import LedgerStore

                store = LedgerStore()

                with self.profile(f"{store_name}_read", ProfileMode.COMBINED):
                    store.read_ledger()

                with self.profile(f"{store_name}_write", ProfileMode.COMBINED):
                    store.write_ledger({"test": "data"})

            elif store_name == "manifest":
                from .manifest_store import ManifestStore

                store = ManifestStore()

                with self.profile(f"{store_name}_save", ProfileMode.COMBINED):
                    store.save_manifest("test", {"id": "test"})

                with self.profile(f"{store_name}_query", ProfileMode.COMBINED):
                    store.query_manifests()

            elif store_name == "lobe_index":
                from .lobe_index import LobeIndex

                store = LobeIndex()

                with self.profile(f"{store_name}_search", ProfileMode.COMBINED):
                    store.search("test")

            elif store_name == "search":
                from .search_engine import SearchEngine

                store = SearchEngine()

                with self.profile(f"{store_name}_index", ProfileMode.COMBINED):
                    store.index_document("test", "Test", "Test content", "test")

                with self.profile(f"{store_name}_search", ProfileMode.COMBINED):
                    store.search("test")

            elif store_name == "cache":
                from .hot_cache import HotCache

                store = HotCache()

                with self.profile(f"{store_name}_set", ProfileMode.COMBINED):
                    store.set("test", "value")

                with self.profile(f"{store_name}_get", ProfileMode.COMBINED):
                    store.get("test")

            else:
                logger.warning(f"Unknown store for profiling: {store_name}")
                return {}

        except Exception as e:
            logger.error(f"Failed to profile {store_name}: {e}")
            return {}

        # Collect results for this store
        store_results = {}
        for key, result in self.results.items():
            if key.startswith(f"{store_name}_"):
                store_results[key] = result

        return store_results

    def detect_bottlenecks(self) -> List[Bottleneck]:
        """
        Detect performance bottlenecks from profiling results.

        Returns:
            List of detected bottlenecks.
        """
        self.bottlenecks.clear()

        # Analyze recent results (last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        recent_results = [r for r in self.results.values() if r.timestamp >= cutoff]

        if not recent_results:
            return []

        # Group by operation type
        operations = {}
        for result in recent_results:
            op_type = result.name.split("_")[0] if "_" in result.name else result.name
            if op_type not in operations:
                operations[op_type] = []
            operations[op_type].append(result)

        # Analyze each operation type
        for op_type, results in operations.items():
            self._analyze_operation_bottlenecks(op_type, results)

        # Analyze memory usage
        self._analyze_memory_bottlenecks(recent_results)

        # Analyze I/O patterns
        self._analyze_io_bottlenecks(recent_results)

        return self.bottlenecks

    def _analyze_operation_bottlenecks(
        self, op_type: str, results: List[ProfileResult]
    ):
        """Analyze bottlenecks for specific operation type."""
        if len(results) < 3:
            return

        # Calculate statistics
        durations = [r.duration_ms for r in results]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)

        # Detect slow operations
        if max_duration > avg_duration * 5:
            self.bottlenecks.append(
                Bottleneck(
                    location=f"{op_type}_operations",
                    severity="high" if max_duration > 1000 else "medium",
                    description=f"Slow {op_type} operations detected",
                    impact=f"Maximum duration {max_duration:.2f}ms vs average {avg_duration:.2f}ms",
                    recommendation="Consider caching, batching, or optimizing data structures",
                    evidence={
                        "operation_type": op_type,
                        "sample_size": len(results),
                        "avg_duration_ms": avg_duration,
                        "max_duration_ms": max_duration,
                        "min_duration_ms": min_duration,
                    },
                )
            )

        # Detect memory-intensive operations
        memory_usage = [r.memory_peak_bytes for r in results if r.memory_peak_bytes > 0]
        if memory_usage:
            avg_memory = sum(memory_usage) / len(memory_usage)
            if avg_memory > 100 * 1024 * 1024:  # 100MB
                self.bottlenecks.append(
                    Bottleneck(
                        location=f"{op_type}_memory",
                        severity="high" if avg_memory > 500 * 1024 * 1024 else "medium",
                        description=f"High memory usage for {op_type} operations",
                        impact=f"Average memory usage {avg_memory / 1024 / 1024:.2f}MB",
                        recommendation="Implement memory pooling, streaming, or pagination",
                        evidence={
                            "operation_type": op_type,
                            "avg_memory_bytes": avg_memory,
                            "avg_memory_mb": avg_memory / 1024 / 1024,
                        },
                    )
                )

    def _analyze_memory_bottlenecks(self, results: List[ProfileResult]):
        """Analyze memory-related bottlenecks."""
        memory_results = [r for r in results if r.memory_peak_bytes > 0]
        if not memory_results:
            return

        # Find operations with memory leaks (increasing memory over time)
        memory_by_time = sorted(
            [(r.timestamp, r.memory_peak_bytes) for r in memory_results],
            key=lambda x: x[0],
        )

        if len(memory_by_time) >= 5:
            timestamps, memory_values = zip(*memory_by_time)

            # Simple trend detection
            first_half = memory_values[: len(memory_values) // 2]
            second_half = memory_values[len(memory_values) // 2 :]

            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)

            if avg_second > avg_first * 1.5:  # 50% increase
                self.bottlenecks.append(
                    Bottleneck(
                        location="memory_trend",
                        severity="medium",
                        description="Potential memory leak detected",
                        impact=f"Memory usage increased from {avg_first / 1024 / 1024:.2f}MB to {avg_second / 1024 / 1024:.2f}MB",
                        recommendation="Check for unclosed resources, circular references, or caching without limits",
                        evidence={
                            "first_half_avg_mb": avg_first / 1024 / 1024,
                            "second_half_avg_mb": avg_second / 1024 / 1024,
                            "increase_percent": (avg_second / avg_first - 1) * 100,
                        },
                    )
                )

    def _analyze_io_bottlenecks(self, results: List[ProfileResult]):
        """Analyze I/O related bottlenecks."""
        # Look for operations with high call counts
        high_call_ops = [
            r for r in results if r.call_count > 1000 and r.duration_ms > 100
        ]

        for result in high_call_ops:
            self.bottlenecks.append(
                Bottleneck(
                    location=f"{result.name}_calls",
                    severity="low",
                    description=f"High call count for {result.name}",
                    impact=f"{result.call_count:,} calls taking {result.duration_ms:.2f}ms total",
                    recommendation="Consider batching calls or implementing request coalescing",
                    evidence={
                        "operation": result.name,
                        "call_count": result.call_count,
                        "total_duration_ms": result.duration_ms,
                        "avg_duration_per_call_ms": result.duration_ms
                        / result.call_count,
                    },
                )
            )

    def generate_report(self, format: str = "text") -> Union[str, Dict[str, Any]]:
        """
        Generate profiling report.

        Args:
            format: Report format ("text", "json", "html").

        Returns:
            Report in requested format.
        """
        # Detect bottlenecks if not already done
        if not self.bottlenecks:
            self.detect_bottlenecks()

        # Prepare report data
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_profiles": len(self.results),
            "recent_profiles": len(
                [
                    r
                    for r in self.results.values()
                    if r.timestamp >= datetime.now() - timedelta(hours=24)
                ]
            ),
            "bottlenecks": [b.to_dict() for b in self.bottlenecks],
            "performance_summary": self._generate_performance_summary(),
        }

        # Generate in requested format
        if format == "json":
            return json.dumps(report_data, indent=2)

        elif format == "html":
            return self._generate_html_report(report_data)

        else:  # text format (default)
            return self._generate_text_report(report_data)

    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary from results."""
        if not self.results:
            return {}

        # Group by operation
        operations = {}
        for result in self.results.values():
            op_name = result.name
            if op_name not in operations:
                operations[op_name] = []
            operations[op_name].append(result)

        summary = {}
        for op_name, results in operations.items():
            durations = [r.duration_ms for r in results]
            memory_peaks = [
                r.memory_peak_bytes for r in results if r.memory_peak_bytes > 0
            ]

            summary[op_name] = {
                "call_count": len(results),
                "avg_duration_ms": sum(durations) / len(durations),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "avg_memory_mb": (
                    sum(memory_peaks) / len(memory_peaks) / 1024 / 1024
                    if memory_peaks
                    else 0
                ),
            }

        return summary

    def _generate_text_report(self, report_data: Dict[str, Any]) -> str:
        """Generate text format report."""
        lines = []

        lines.append("=" * 60)
        lines.append("NeoCortex Performance Profiling Report")
        lines.append("=" * 60)
        lines.append(f"Generated: {report_data['timestamp']}")
        lines.append(f"Total profiles: {report_data['total_profiles']}")
        lines.append(f"Recent profiles (24h): {report_data['recent_profiles']}")
        lines.append("")

        # Performance summary
        lines.append("Performance Summary:")
        lines.append("-" * 40)

        for op_name, stats in report_data["performance_summary"].items():
            lines.append(f"  {op_name}:")
            lines.append(f"    Calls: {stats['call_count']}")
            lines.append(
                f"    Duration: {stats['avg_duration_ms']:.2f}ms "
                f"(min: {stats['min_duration_ms']:.2f}ms, "
                f"max: {stats['max_duration_ms']:.2f}ms)"
            )
            if stats["avg_memory_mb"] > 0:
                lines.append(f"    Memory: {stats['avg_memory_mb']:.2f}MB avg peak")

        # Bottlenecks
        lines.append("")
        lines.append(f"Detected Bottlenecks ({len(report_data['bottlenecks'])}):")
        lines.append("-" * 40)

        if not report_data["bottlenecks"]:
            lines.append("  ✅ No bottlenecks detected")
        else:
            for i, bottleneck in enumerate(report_data["bottlenecks"], 1):
                lines.append(
                    f"  {i}. [{bottleneck['severity'].upper()}] {bottleneck['location']}"
                )
                lines.append(f"     Description: {bottleneck['description']}")
                lines.append(f"     Impact: {bottleneck['impact']}")
                lines.append(f"     Recommendation: {bottleneck['recommendation']}")
                lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML format report."""
        # Simple HTML report for now
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NeoCortex Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .bottleneck {{ border-left: 4px solid #e74c3c; padding: 10px; margin: 10px 0; background: #f9f9f9; }}
                .bottleneck.high {{ border-color: #e74c3c; }}
                .bottleneck.medium {{ border-color: #f39c12; }}
                .bottleneck.low {{ border-color: #3498db; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NeoCortex Performance Profiling Report</h1>
                <p>Generated: {report_data["timestamp"]}</p>
                <p>Total profiles: {report_data["total_profiles"]} | Recent (24h): {report_data["recent_profiles"]}</p>
            </div>
            
            <div class="section">
                <h2>Performance Summary</h2>
                <table>
                    <tr>
                        <th>Operation</th>
                        <th>Calls</th>
                        <th>Avg Duration (ms)</th>
                        <th>Min Duration (ms)</th>
                        <th>Max Duration (ms)</th>
                        <th>Avg Memory (MB)</th>
                    </tr>
        """

        for op_name, stats in report_data["performance_summary"].items():
            html += f"""
                    <tr>
                        <td>{op_name}</td>
                        <td>{stats["call_count"]}</td>
                        <td>{stats["avg_duration_ms"]:.2f}</td>
                        <td>{stats["min_duration_ms"]:.2f}</td>
                        <td>{stats["max_duration_ms"]:.2f}</td>
                        <td>{stats["avg_memory_mb"]:.2f if stats['avg_memory_mb'] > 0 else 'N/A'}</td>
                    </tr>
            """

        html += """
                </table>
            </div>
            
            <div class="section">
                <h2>Detected Bottlenecks</h2>
        """

        if not report_data["bottlenecks"]:
            html += "<p>✅ No bottlenecks detected</p>"
        else:
            for bottleneck in report_data["bottlenecks"]:
                html += f"""
                <div class="bottleneck {bottleneck["severity"]}">
                    <h3>[{bottleneck["severity"].upper()}] {bottleneck["location"]}</h3>
                    <p><strong>Description:</strong> {bottleneck["description"]}</p>
                    <p><strong>Impact:</strong> {bottleneck["impact"]}</p>
                    <p><strong>Recommendation:</strong> {bottleneck["recommendation"]}</p>
                </div>
                """

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def save_report(self, filename: Optional[str] = None) -> Path:
        """
        Save profiling report to file.

        Args:
            filename: Output filename (auto-generated if None).

        Returns:
            Path to saved report.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"profile_report_{timestamp}.json"

        report_path = self.output_dir / filename

        report = self.generate_report(format="json")
        if isinstance(report, str):
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
        else:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

        logger.info(f"Profile report saved to {report_path}")
        return report_path

    def clear_results(self):
        """Clear all profiling results."""
        self.results.clear()
        self.bottlenecks.clear()
        logger.info("Profiling results cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get profiler statistics."""
        return {
            "total_results": len(self.results),
            "total_bottlenecks": len(self.bottlenecks),
            "output_dir": str(self.output_dir),
            "recent_results_24h": len(
                [
                    r
                    for r in self.results.values()
                    if r.timestamp >= datetime.now() - timedelta(hours=24)
                ]
            ),
        }


def create_profiler(output_dir: Optional[Path] = None) -> Profiler:
    """
    Create a Profiler instance.

    Args:
        output_dir: Directory for profile reports.

    Returns:
        Profiler instance.
    """
    return Profiler(output_dir=output_dir)
