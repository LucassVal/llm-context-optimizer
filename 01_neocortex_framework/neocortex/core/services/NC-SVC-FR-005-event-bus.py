"""---
@Module NC-SVC-FR-005-event-bus mcp _genealogy:   injected_at: '2026-04-16T00:23:58.70
---
"""


"""
NC-SVC-FR-005-event-bus.py
FR-005  Event Bus: Synchronous event bus for inter-tool communication in NeoCortex.

Provides a singleton event bus for publishing and subscribing to events
(TOOL_CALLED, TOOL_RESULT, AGENT_STATE_CHANGED, HANDOFF_SUBMITTED,
KAIROS_TICK, ENTITY_EXPIRED, NOTIFICATION_SENT, CHANNEL_MESSAGE).
Fully synchronous for MCP compatibility; no asyncio.

Restriction: server.py, sub_server.py are @LOCKS.
This module is a standalone service that can be imported by any module.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class NeoCortexEvent:
    """Event data structure for NeoCortex event bus."""

    event_type: str
    payload: Any
    timestamp: datetime
    source_tool: str | None = None


class EventBus:
    """Synchronous event bus for NeoCortex."""

    _instance: Optional["EventBus"] = None
    _subscribers: dict[str, list[Callable[[NeoCortexEvent], None]]]

    def __new__(cls) -> "EventBus":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance

    def subscribe(
        self, event_type: str, callback: Callable[[NeoCortexEvent], None]
    ) -> None:
        """
        Subscribe a callback to an event type.

        Args:
            event_type: Event type string (e.g., 'TOOL_CALLED')
            callback: Function that takes a NeoCortexEvent and returns None
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed callback to event type '{event_type}'")

    def unsubscribe(
        self, event_type: str, callback: Callable[[NeoCortexEvent], None]
    ) -> bool:
        """
        Unsubscribe a callback from an event type.

        Args:
            event_type: Event type string
            callback: Callback to remove

        Returns:
            True if callback was removed, False if not found
        """
        if event_type not in self._subscribers:
            return False
        try:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed callback from event type '{event_type}'")
            return True
        except ValueError:
            return False

    def get_subscribers_count(self, event_type: str) -> int:
        """
        Get the number of subscribers for an event type.

        Args:
            event_type: Event type string

        Returns:
            Number of subscribers (0 if event type not found)
        """
        if event_type not in self._subscribers:
            return 0
        return len(self._subscribers[event_type])

    def publish(self, event: NeoCortexEvent) -> None:
        """
        Publish an event to all subscribers of its type.

        Args:
            event: NeoCortexEvent instance
        """
        event_type = event.event_type
        if event_type not in self._subscribers:
            logger.debug(f"No subscribers for event type '{event_type}'")
            return

        logger.info(
            f"Publishing event '{event_type}' from {event.source_tool or 'unknown'}"
        )
        for callback in self._subscribers[event_type]:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Callback error for event '{event_type}': {e}")


def get_event_bus() -> EventBus:
    """Get the singleton EventBus instance."""
    return EventBus()


# Predefined event types
TOOL_CALLED = "TOOL_CALLED"
TOOL_RESULT = "TOOL_RESULT"
AGENT_STATE_CHANGED = "AGENT_STATE_CHANGED"
HANDOFF_SUBMITTED = "HANDOFF_SUBMITTED"
KAIROS_TICK = "kairos.tick"
ENTITY_EXPIRED = "entity_expired"
NOTIFICATION_SENT = "notification_sent"
CHANNEL_MESSAGE = "channel.notification"


# Convenience functions
def publish_tool_called(tool_name: str, payload: Any) -> None:
    """Publish a TOOL_CALLED event."""
    event = NeoCortexEvent(
        event_type=TOOL_CALLED,
        payload=payload,
        timestamp=datetime.now(),
        source_tool=tool_name,
    )
    get_event_bus().publish(event)


def publish_tool_result(
    tool_name: str, result: Any, error: str | None = None
) -> None:
    """Publish a TOOL_RESULT event."""
    event = NeoCortexEvent(
        event_type=TOOL_RESULT,
        payload={"result": result, "error": error},
        timestamp=datetime.now(),
        source_tool=tool_name,
    )
    get_event_bus().publish(event)


def publish_agent_state_changed(
    old_state: str, new_state: str, agent_id: str | None = None
) -> None:
    """Publish an AGENT_STATE_CHANGED event."""
    event = NeoCortexEvent(
        event_type=AGENT_STATE_CHANGED,
        payload={"old_state": old_state, "new_state": new_state, "agent_id": agent_id},
        timestamp=datetime.now(),
        source_tool=agent_id,
    )
    get_event_bus().publish(event)


def publish_handoff_submitted(ticket_id: str, handoff_data: dict[str, Any]) -> None:
    """Publish a HANDOFF_SUBMITTED event."""
    event = NeoCortexEvent(
        event_type=HANDOFF_SUBMITTED,
        payload=handoff_data,
        timestamp=datetime.now(),
        source_tool="handoff_system",
    )
    get_event_bus().publish(event)


def publish_entity_expired(entity_id: str, payload: Any = None) -> None:
    """Publish an ENTITY_EXPIRED event."""
    event = NeoCortexEvent(
        event_type=ENTITY_EXPIRED,
        payload=payload,
        timestamp=datetime.now(),
        source_tool="entity_manager",
    )
    get_event_bus().publish(event)
