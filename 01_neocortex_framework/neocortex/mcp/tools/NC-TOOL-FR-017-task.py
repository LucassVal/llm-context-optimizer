#!/usr/bin/env python3
"""
NeoCortex Task Tool

MCP tool for neocortex_task - task execution for multi-agent orchestration.
"""

import json
import time
import traceback
from typing import Dict, Any, List
from pathlib import Path

# Import AgentExecutor for hybrid LLM task execution
from ...agent.executor import AgentExecutor, AgentTask


def register_tool(mcp):
    """
    Register the neocortex_task tool with the MCP server.
    """

    @mcp.tool(name="neocortex_task")
    def tool_task(
        action: str, task_id: str = None, task_data: str = None, backend: str = None
    ) -> Dict[str, Any]:
        """
        Execute tasks for multi-agent orchestration.

        Actions:
        - execute: Execute a task with optional backend override
        - list_queued: List queued tasks (simulated)
        - get_result: Get result of a previously executed task
        - cancel: Cancel a pending task
        """
        if action == "execute":
            return _execute_task(task_id, task_data, backend)
        elif action == "list_queued":
            return _list_queued()
        elif action == "get_result":
            return _get_result(task_id)
        elif action == "cancel":
            return _cancel_task(task_id)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}


def _execute_task(task_id: str, task_data: str, backend: str = None) -> Dict[str, Any]:
    """Execute a task using AgentExecutor."""
    if not task_data:
        return {"success": False, "error": "task_data is required"}

    try:
        # Parse task data
        task_dict = json.loads(task_data)
        task_type = task_dict.get("type", "unknown")
        prompt = task_dict.get("prompt", "")
        context = task_dict.get("context", {})

        # Create AgentExecutor
        executor = AgentExecutor()

        # Create AgentTask
        task = AgentTask(
            task_id=task_id or f"task_{int(time.time())}",
            role=task_type,
            prompt=prompt,
            system_prompt=context.get("system_prompt"),
            model=context.get("model"),
            temperature=context.get("temperature", 0.7),
            max_tokens=context.get("max_tokens"),
            metadata=context,
        )

        # Execute task with optional backend override
        start_time = time.time()
        response = executor.execute(task, backend_override=backend)
        execution_time = time.time() - start_time

        # Extract result from LLMResponse
        result_data = {
            "task_id": task.task_id,
            "type": task_type,
            "success": True,
            "result": response.content,
            "backend": response.model or "unknown",
            "execution_time": execution_time,
            "timestamp": time.time(),
            "metadata": {
                "model": response.model,
                "provider": response.provider.value
                if hasattr(response.provider, "value")
                else str(response.provider),
                "usage": response.usage if hasattr(response, "usage") else {},
            },
        }

        return {
            "success": True,
            "message": f"Task '{task_type}' executed successfully",
            "task": result_data,
        }

    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON in task_data"}
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def _list_queued() -> Dict[str, Any]:
    """List queued tasks (simulated)."""
    # In a real implementation, this would query a task queue
    return {
        "success": True,
        "queued_tasks": [],
        "total": 0,
        "note": "Task queue not implemented - simulation only",
    }


def _get_result(task_id: str) -> Dict[str, Any]:
    """Get result of a previously executed task (simulated)."""
    if not task_id:
        return {"success": False, "error": "task_id is required"}

    # In a real implementation, this would retrieve from persistent storage
    return {
        "success": True,
        "task_id": task_id,
        "status": "completed",
        "result": {"simulated": True, "note": "Result storage not implemented"},
        "retrieved_at": time.time(),
    }


def _cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a pending task (simulated)."""
    if not task_id:
        return {"success": False, "error": "task_id is required"}

    return {
        "success": True,
        "message": f"Task '{task_id}' cancelled (simulated)",
        "task_id": task_id,
        "note": "Task cancellation not fully implemented",
    }
