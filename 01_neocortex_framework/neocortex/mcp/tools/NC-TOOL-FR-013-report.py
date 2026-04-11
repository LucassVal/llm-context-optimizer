#!/usr/bin/env python3
"""
NeoCortex Report Tool

MCP tool for generating metrics reports in Markdown, CSV, and JSON formats.
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def register_tool(mcp):
    """
    Register the neocortex_report tool with the MCP server.
    """
    from ...infra.metrics_store import create_metrics_store
    from ..server import get_metrics_store

    # Get metrics store (use global instance or create new)
    metrics_store = get_metrics_store()
    if metrics_store is None:
        metrics_store = create_metrics_store()
        logger.warning("Metrics store not initialized globally, created new instance")

    @mcp.tool(name="neocortex_report")
    def tool_report(
        action: str, format: str = "markdown", days: int = 7
    ) -> Dict[str, Any]:
        """
        Generate metrics reports for NeoCortex analytics.

        Actions:
        - generate_daily_summary: Daily token usage and system health summary
        - generate_cost_report: Cost savings and token economy analysis
        - generate_agent_report: Agent activity and performance report
        - get_metrics_stats: Basic metrics store statistics

        Formats: markdown, csv, json

        Args:
            action: Report action to perform
            format: Output format (markdown, csv, json)
            days: Number of days to include in report (default: 7)
        """
        if action == "generate_daily_summary":
            return _generate_daily_summary(metrics_store, format, days)
        elif action == "generate_cost_report":
            return _generate_cost_report(metrics_store, format, days)
        elif action == "generate_agent_report":
            return _generate_agent_report(metrics_store, format, days)
        elif action == "get_metrics_stats":
            return _get_metrics_stats(metrics_store, format)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}. Available: generate_daily_summary, generate_cost_report, generate_agent_report, get_metrics_stats",
            }


def _generate_daily_summary(metrics_store, format: str, days: int) -> Dict[str, Any]:
    """Generate daily summary report."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get data
        token_usage = metrics_store.get_daily_token_usage(start_date, end_date)
        pulse_health = metrics_store.get_pulse_health(
            start_time=start_date, end_time=end_date
        )
        agent_activity = metrics_store.get_agent_activity(
            start_time=start_date, end_time=end_date, limit=1000
        )

        # Calculate totals
        total_tokens = sum(row.get("total_tokens", 0) for row in token_usage)
        cache_hits = sum(row.get("cache_hit", 0) for row in token_usage)
        cache_misses = sum(row.get("cache_miss", 0) for row in token_usage)
        cache_hit_rate = (
            cache_hits / (cache_hits + cache_misses)
            if (cache_hits + cache_misses) > 0
            else 0
        )

        pulse_success = sum(
            1 for event in pulse_health if event.get("status") == "success"
        )
        pulse_failure = sum(
            1 for event in pulse_health if event.get("status") == "failure"
        )
        pulse_success_rate = pulse_success / len(pulse_health) if pulse_health else 0

        # Generate report
        if format == "markdown":
            report = _format_daily_summary_markdown(
                token_usage,
                pulse_health,
                agent_activity,
                total_tokens,
                cache_hit_rate,
                pulse_success_rate,
                start_date,
                end_date,
                days,
            )
        elif format == "csv":
            report = _format_daily_summary_csv(
                token_usage, pulse_health, agent_activity, start_date, end_date
            )
        elif format == "json":
            report = _format_daily_summary_json(
                token_usage,
                pulse_health,
                agent_activity,
                total_tokens,
                cache_hit_rate,
                pulse_success_rate,
                start_date,
                end_date,
            )
        else:
            return {"success": False, "error": f"Unsupported format: {format}"}

        # Save report to file
        report_path = _save_report("daily_summary", report, format)

        return {
            "success": True,
            "report": report,
            "report_path": str(report_path),
            "summary": {
                "total_tokens": total_tokens,
                "cache_hit_rate": cache_hit_rate,
                "pulse_success_rate": pulse_success_rate,
                "period_days": days,
            },
        }

    except Exception as e:
        logger.error(f"Error generating daily summary: {e}")
        return {"success": False, "error": str(e)}


def _generate_cost_report(metrics_store, format: str, days: int) -> Dict[str, Any]:
    """Generate cost analysis report."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get data
        cost_summary = metrics_store.get_cost_summary(start_date, end_date)
        token_usage = metrics_store.get_daily_token_usage(start_date, end_date)

        # Calculate totals
        total_cost_real = sum(row.get("cost_real", 0) for row in cost_summary)
        total_cost_saved = sum(row.get("cost_saved", 0) for row in cost_summary)
        total_cost_without_cache = sum(
            row.get("cost_without_cache", 0) for row in cost_summary
        )

        total_tokens = sum(row.get("total_tokens", 0) for row in token_usage)
        cost_per_token = total_cost_real / total_tokens if total_tokens > 0 else 0
        savings_percentage = (
            (total_cost_saved / total_cost_without_cache * 100)
            if total_cost_without_cache > 0
            else 0
        )

        # Generate report
        if format == "markdown":
            report = _format_cost_report_markdown(
                cost_summary,
                token_usage,
                total_cost_real,
                total_cost_saved,
                total_cost_without_cache,
                savings_percentage,
                cost_per_token,
                start_date,
                end_date,
                days,
            )
        elif format == "csv":
            report = _format_cost_report_csv(
                cost_summary, token_usage, start_date, end_date
            )
        elif format == "json":
            report = _format_cost_report_json(
                cost_summary,
                token_usage,
                total_cost_real,
                total_cost_saved,
                total_cost_without_cache,
                savings_percentage,
                cost_per_token,
                start_date,
                end_date,
            )
        else:
            return {"success": False, "error": f"Unsupported format: {format}"}

        # Save report
        report_path = _save_report("cost_report", report, format)

        return {
            "success": True,
            "report": report,
            "report_path": str(report_path),
            "summary": {
                "total_cost_real": total_cost_real,
                "total_cost_saved": total_cost_saved,
                "savings_percentage": savings_percentage,
                "cost_per_token": cost_per_token,
                "period_days": days,
            },
        }

    except Exception as e:
        logger.error(f"Error generating cost report: {e}")
        return {"success": False, "error": str(e)}


def _generate_agent_report(metrics_store, format: str, days: int) -> Dict[str, Any]:
    """Generate agent activity report."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get data
        agent_activity = metrics_store.get_agent_activity(
            start_time=start_date, end_time=end_date, limit=5000
        )
        token_usage = metrics_store.get_daily_token_usage(start_date, end_date)

        # Group by agent
        agent_stats = {}
        for activity in agent_activity:
            agent_id = activity.get("agent_id", "unknown")
            if agent_id not in agent_stats:
                agent_stats[agent_id] = {
                    "spawns": 0,
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "stopped": 0,
                    "first_seen": activity.get("timestamp"),
                    "last_seen": activity.get("timestamp"),
                }

            stats = agent_stats[agent_id]
            action = activity.get("action", "")

            if action == "spawn":
                stats["spawns"] += 1
            elif action == "task_completed":
                stats["tasks_completed"] += 1
            elif action == "task_failed":
                stats["tasks_failed"] += 1
            elif action == "stopped":
                stats["stopped"] += 1

            # Update timestamps
            if activity.get("timestamp") < stats.get("first_seen", "9999"):
                stats["first_seen"] = activity.get("timestamp")
            if activity.get("timestamp") > stats.get("last_seen", "0000"):
                stats["last_seen"] = activity.get("timestamp")

        # Calculate token usage per agent
        agent_tokens = {}
        for usage in token_usage:
            agent = usage.get("agent")
            if agent:
                agent_tokens[agent] = agent_tokens.get(agent, 0) + usage.get(
                    "total_tokens", 0
                )

        # Merge token data
        for agent_id, stats in agent_stats.items():
            stats["tokens_used"] = agent_tokens.get(agent_id, 0)
            stats["success_rate"] = (
                stats["tasks_completed"]
                / (stats["tasks_completed"] + stats["tasks_failed"])
                if (stats["tasks_completed"] + stats["tasks_failed"]) > 0
                else 0
            )

        # Generate report
        if format == "markdown":
            report = _format_agent_report_markdown(
                agent_stats, start_date, end_date, days
            )
        elif format == "csv":
            report = _format_agent_report_csv(agent_stats, start_date, end_date)
        elif format == "json":
            report = _format_agent_report_json(agent_stats, start_date, end_date)
        else:
            return {"success": False, "error": f"Unsupported format: {format}"}

        # Save report
        report_path = _save_report("agent_report", report, format)

        return {
            "success": True,
            "report": report,
            "report_path": str(report_path),
            "summary": {
                "total_agents": len(agent_stats),
                "total_tasks": sum(
                    s["tasks_completed"] + s["tasks_failed"]
                    for s in agent_stats.values()
                ),
                "success_rate_overall": sum(
                    s["tasks_completed"] for s in agent_stats.values()
                )
                / max(
                    1,
                    sum(
                        s["tasks_completed"] + s["tasks_failed"]
                        for s in agent_stats.values()
                    ),
                ),
                "period_days": days,
            },
        }

    except Exception as e:
        logger.error(f"Error generating agent report: {e}")
        return {"success": False, "error": str(e)}


def _get_metrics_stats(metrics_store, format: str) -> Dict[str, Any]:
    """Get metrics store statistics."""
    try:
        stats = metrics_store.get_stats()

        if format == "json":
            report = json.dumps(stats, indent=2)
        elif format == "markdown":
            report = _format_stats_markdown(stats)
        else:
            return {
                "success": False,
                "error": f"Unsupported format for stats: {format}",
            }

        return {
            "success": True,
            "stats": stats,
            "report": report,
        }

    except Exception as e:
        logger.error(f"Error getting metrics stats: {e}")
        return {"success": False, "error": str(e)}


def _save_report(report_name: str, content: str, format: str) -> Path:
    """Save report to file."""
    from ...config import get_config

    config = get_config()
    reports_dir = config.project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = {"markdown": "md", "csv": "csv", "json": "json"}.get(format, "txt")
    filename = f"{report_name}_{timestamp}.{ext}"
    filepath = reports_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Report saved to {filepath}")
    return filepath


# Formatting functions
def _format_daily_summary_markdown(
    token_usage,
    pulse_health,
    agent_activity,
    total_tokens,
    cache_hit_rate,
    pulse_success_rate,
    start_date,
    end_date,
    days,
):
    """Format daily summary as Markdown."""
    report = [
        "# NeoCortex Daily Summary Report",
        "",
        f"**Period:** {start_date.date()} to {end_date.date()} ({days} days)",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 📊 Executive Summary",
        "",
        f"- **Total Tokens Used:** {total_tokens:,}",
        f"- **Cache Hit Rate:** {cache_hit_rate:.1%}",
        f"- **Pulse Success Rate:** {pulse_success_rate:.1%}",
        "",
        "## 📈 Token Usage by Model",
        "",
        "| Date | Model | Agent | Cache Hits | Cache Misses | Output Tokens | Total Tokens |",
        "|------|-------|-------|------------|--------------|---------------|--------------|",
    ]

    for row in sorted(token_usage, key=lambda x: x.get("date", ""), reverse=True):
        report.append(
            f"| {row.get('date', '')} | {row.get('model', '')} | {row.get('agent', 'N/A')} | "
            f"{row.get('cache_hit', 0):,} | {row.get('cache_miss', 0):,} | "
            f"{row.get('output_tokens', 0):,} | {row.get('total_tokens', 0):,} |"
        )

    report.extend(
        [
            "",
            "## ⚙️ Pulse Health Events",
            "",
            "| Timestamp | Event Type | Status | Duration (ms) |",
            "|-----------|------------|--------|---------------|",
        ]
    )

    for event in sorted(
        pulse_health, key=lambda x: x.get("timestamp", ""), reverse=True
    )[:20]:
        report.append(
            f"| {event.get('timestamp', '')} | {event.get('event_type', '')} | "
            f"{event.get('status', '')} | {event.get('duration_ms', 'N/A')} |"
        )

    report.extend(
        [
            "",
            "## 🤖 Recent Agent Activity",
            "",
            "| Timestamp | Agent ID | Action | Details |",
            "|-----------|----------|--------|---------|",
        ]
    )

    for activity in sorted(
        agent_activity, key=lambda x: x.get("timestamp", ""), reverse=True
    )[:15]:
        details = activity.get("details", {})
        details_str = (
            json.dumps(details)[:50] + "..."
            if len(json.dumps(details)) > 50
            else json.dumps(details)
        )
        report.append(
            f"| {activity.get('timestamp', '')} | {activity.get('agent_id', '')} | "
            f"{activity.get('action', '')} | {details_str} |"
        )

    return "\n".join(report)


def _format_daily_summary_csv(
    token_usage, pulse_health, agent_activity, start_date, end_date
):
    """Format daily summary as CSV."""
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Token usage
    writer.writerow(["Token Usage"])
    writer.writerow(
        [
            "Date",
            "Model",
            "Agent",
            "Cache Hits",
            "Cache Misses",
            "Output Tokens",
            "Total Tokens",
        ]
    )
    for row in token_usage:
        writer.writerow(
            [
                row.get("date", ""),
                row.get("model", ""),
                row.get("agent", ""),
                row.get("cache_hit", 0),
                row.get("cache_miss", 0),
                row.get("output_tokens", 0),
                row.get("total_tokens", 0),
            ]
        )

    writer.writerow([])
    writer.writerow(["Pulse Health"])
    writer.writerow(["Timestamp", "Event Type", "Status", "Duration (ms)"])
    for event in pulse_health:
        writer.writerow(
            [
                event.get("timestamp", ""),
                event.get("event_type", ""),
                event.get("status", ""),
                event.get("duration_ms", ""),
            ]
        )

    return output.getvalue()


def _format_daily_summary_json(
    token_usage,
    pulse_health,
    agent_activity,
    total_tokens,
    cache_hit_rate,
    pulse_success_rate,
    start_date,
    end_date,
):
    """Format daily summary as JSON."""
    return json.dumps(
        {
            "report_type": "daily_summary",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_tokens": total_tokens,
                "cache_hit_rate": cache_hit_rate,
                "pulse_success_rate": pulse_success_rate,
            },
            "token_usage": token_usage,
            "pulse_health": pulse_health,
            "agent_activity": agent_activity[:100],  # Limit
        },
        indent=2,
    )


def _format_cost_report_markdown(
    cost_summary,
    token_usage,
    total_cost_real,
    total_cost_saved,
    total_cost_without_cache,
    savings_percentage,
    cost_per_token,
    start_date,
    end_date,
    days,
):
    """Format cost report as Markdown."""
    report = [
        "# NeoCortex Cost Analysis Report",
        "",
        f"**Period:** {start_date.date()} to {end_date.date()} ({days} days)",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 💰 Cost Summary",
        "",
        f"- **Actual Cost:** ${total_cost_real:,.4f}",
        f"- **Cost Saved:** ${total_cost_saved:,.4f}",
        f"- **Cost Without Cache:** ${total_cost_without_cache:,.4f}",
        f"- **Savings:** {savings_percentage:.1f}%",
        f"- **Cost per Token:** ${cost_per_token:.6f}",
        "",
        "## 📊 Cost by Provider & Model",
        "",
        "| Date | Provider | Model | Actual Cost | Cost Saved | Cost Without Cache |",
        "|------|----------|-------|-------------|------------|---------------------|",
    ]

    for row in sorted(
        cost_summary,
        key=lambda x: (x.get("date", ""), x.get("provider", "")),
        reverse=True,
    ):
        report.append(
            f"| {row.get('date', '')} | {row.get('provider', '')} | {row.get('model', '')} | "
            f"${row.get('cost_real', 0):,.4f} | ${row.get('cost_saved', 0):,.4f} | "
            f"${row.get('cost_without_cache', 0):,.4f} |"
        )

    report.extend(
        [
            "",
            "## 🪙 Token Usage Economics",
            "",
            "| Date | Model | Agent | Cache Hits | Cache Misses | Total Tokens | Effective Cost |",
            "|------|-------|-------|------------|--------------|--------------|----------------|",
        ]
    )

    for row in sorted(token_usage, key=lambda x: x.get("date", ""), reverse=True)[:30]:
        effective_cost = row.get("total_tokens", 0) * cost_per_token
        report.append(
            f"| {row.get('date', '')} | {row.get('model', '')} | {row.get('agent', 'N/A')} | "
            f"{row.get('cache_hit', 0):,} | {row.get('cache_miss', 0):,} | "
            f"{row.get('total_tokens', 0):,} | ${effective_cost:,.4f} |"
        )

    return "\n".join(report)


def _format_cost_report_csv(cost_summary, token_usage, start_date, end_date):
    """Format cost report as CSV."""
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Cost Summary"])
    writer.writerow(
        ["Date", "Provider", "Model", "Actual Cost", "Cost Saved", "Cost Without Cache"]
    )
    for row in cost_summary:
        writer.writerow(
            [
                row.get("date", ""),
                row.get("provider", ""),
                row.get("model", ""),
                row.get("cost_real", 0),
                row.get("cost_saved", 0),
                row.get("cost_without_cache", 0),
            ]
        )

    return output.getvalue()


def _format_cost_report_json(
    cost_summary,
    token_usage,
    total_cost_real,
    total_cost_saved,
    total_cost_without_cache,
    savings_percentage,
    cost_per_token,
    start_date,
    end_date,
):
    """Format cost report as JSON."""
    return json.dumps(
        {
            "report_type": "cost_report",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_cost_real": total_cost_real,
                "total_cost_saved": total_cost_saved,
                "total_cost_without_cache": total_cost_without_cache,
                "savings_percentage": savings_percentage,
                "cost_per_token": cost_per_token,
            },
            "cost_summary": cost_summary,
            "token_usage": token_usage[:100],
        },
        indent=2,
    )


def _format_agent_report_markdown(agent_stats, start_date, end_date, days):
    """Format agent report as Markdown."""
    report = [
        "# NeoCortex Agent Activity Report",
        "",
        f"**Period:** {start_date.date()} to {end_date.date()} ({days} days)",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 🤖 Agent Performance Summary",
        "",
        "| Agent ID | Spawns | Tasks Completed | Tasks Failed | Success Rate | Tokens Used | First Seen | Last Seen |",
        "|----------|--------|-----------------|--------------|--------------|-------------|------------|-----------|",
    ]

    for agent_id, stats in sorted(
        agent_stats.items(), key=lambda x: x[1].get("tasks_completed", 0), reverse=True
    ):
        report.append(
            f"| {agent_id} | {stats['spawns']} | {stats['tasks_completed']} | "
            f"{stats['tasks_failed']} | {stats['success_rate']:.1%} | "
            f"{stats['tokens_used']:,} | {stats['first_seen']} | {stats['last_seen']} |"
        )

    # Calculate totals
    total_spawns = sum(s["spawns"] for s in agent_stats.values())
    total_completed = sum(s["tasks_completed"] for s in agent_stats.values())
    total_failed = sum(s["tasks_failed"] for s in agent_stats.values())
    total_tokens = sum(s["tokens_used"] for s in agent_stats.values())
    overall_success_rate = (
        total_completed / (total_completed + total_failed)
        if (total_completed + total_failed) > 0
        else 0
    )

    report.extend(
        [
            "",
            "## 📈 Summary Statistics",
            "",
            f"- **Total Agents:** {len(agent_stats)}",
            f"- **Total Spawns:** {total_spawns}",
            f"- **Total Tasks Completed:** {total_completed}",
            f"- **Total Tasks Failed:** {total_failed}",
            f"- **Overall Success Rate:** {overall_success_rate:.1%}",
            f"- **Total Tokens Used:** {total_tokens:,}",
            f"- **Average Tokens per Agent:** {total_tokens / len(agent_stats):,.0f}"
            if agent_stats
            else "",
        ]
    )

    return "\n".join(report)


def _format_agent_report_csv(agent_stats, start_date, end_date):
    """Format agent report as CSV."""
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Agent Activity Report"])
    writer.writerow(
        [
            "Agent ID",
            "Spawns",
            "Tasks Completed",
            "Tasks Failed",
            "Success Rate",
            "Tokens Used",
            "First Seen",
            "Last Seen",
        ]
    )
    for agent_id, stats in agent_stats.items():
        writer.writerow(
            [
                agent_id,
                stats["spawns"],
                stats["tasks_completed"],
                stats["tasks_failed"],
                f"{stats['success_rate']:.4f}",
                stats["tokens_used"],
                stats["first_seen"],
                stats["last_seen"],
            ]
        )

    return output.getvalue()


def _format_agent_report_json(agent_stats, start_date, end_date):
    """Format agent report as JSON."""
    return json.dumps(
        {
            "report_type": "agent_report",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "agent_stats": agent_stats,
        },
        indent=2,
    )


def _format_stats_markdown(stats):
    """Format metrics store stats as Markdown."""
    report = [
        "# Metrics Store Statistics",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 📊 Storage Information",
        "",
        f"- **Backend:** {stats.get('backend', 'N/A')}",
        f"- **Database Path:** {stats.get('db_path', 'N/A')}",
        f"- **Retention Days:** {stats.get('retention_days', 'N/A')}",
        "",
        "## 📈 Metrics Overview",
        "",
        f"- **Total Metrics:** {stats.get('total_metrics', 0):,}",
        f"- **Unique Metric IDs:** {stats.get('unique_metrics', 0):,}",
        f"- **Oldest Metric:** {stats.get('oldest_metric', 'N/A')}",
        f"- **Newest Metric:** {stats.get('newest_metric', 'N/A')}",
        "",
        "## 📊 Metrics by Type",
        "",
        "| Metric Type | Count |",
        "|-------------|-------|",
    ]

    for metric_type, count in stats.get("metrics_by_type", {}).items():
        report.append(f"| {metric_type} | {count:,} |")

    return "\n".join(report)
