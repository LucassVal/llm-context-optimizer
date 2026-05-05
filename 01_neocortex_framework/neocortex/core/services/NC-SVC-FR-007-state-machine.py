"""---
@Module NC-SVC-FR-007-state-machine mcp _genealogy:   injected_at: '2026-04-16T00:23:58.78
---
"""


"""
NC-SVC-FR-007-state-machine.py
FR-007  Agent State Machine: Finite State Machine for T1 agent lifecycle.

Defines the legal state transitions for a T1 worker agent in the NeoCortex
Nworker system. States: IDLE, READING, PLANNING, EXECUTING, VALIDATING,
HANDOFF, BLOCKED, ESCALATED.

Restriction: server.py, sub_server.py are @LOCKS.
"""

import importlib.util
import logging
import threading
import time
from collections import deque
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentStateMachine:
    """
    Finite State Machine for T1 agent lifecycle.

    States:
        IDLE: Agent waiting for a task (AVAILABLE in queue)
        READING: Reading ticket YAML and understanding requirements
        PLANNING: Planning execution steps (F1F6)
        EXECUTING: Creating/modifying files in write_zone (F2)
        VALIDATING: Running barriers B1B6 (F3)
        HANDOFF: Creating handoff YAML and marking task DONE (F5F6)
        BLOCKED: Task blocked due to write_zone conflict or lock violation
        ESCALATED: Task escalated to T0 after 5 selfrefine failures

    Terminal states: HANDOFF, ESCALATED (cannot leave).
    """

    # All possible states
    IDLE = "IDLE"
    READING = "READING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    HANDOFF = "HANDOFF"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"

    # Terminal states (no outgoing transitions)
    TERMINAL_STATES = {HANDOFF, ESCALATED}

    # Legal transitions: from_state -> list[to_state]
    ALLOWED_TRANSITIONS = {
        IDLE: [READING, BLOCKED],
        READING: [PLANNING, BLOCKED],
        PLANNING: [EXECUTING, BLOCKED, ESCALATED],
        EXECUTING: [VALIDATING, BLOCKED, ESCALATED],
        VALIDATING: [HANDOFF, EXECUTING, BLOCKED],
        HANDOFF: [],  # terminal
        BLOCKED: [IDLE, ESCALATED],
        ESCALATED: [],  # terminal
    }

    # Singleton registry per agent_id
    _instances: dict[str, "AgentStateMachine"] = {}
    _instances_lock = threading.Lock()

    def __init__(self, agent_id: str = "", initial_state: str = IDLE):
        """Initialize the state machine with an initial state."""
        if initial_state not in self.ALLOWED_TRANSITIONS:
            raise ValueError(f"Invalid initial state: {initial_state}")
        self._agent_id = agent_id
        self._state = initial_state
        self._history = deque(maxlen=100)
        self._lock = threading.Lock()
        self._record_transition(initial_state, reason="initialization")

    @property
    def _event_bus(self):
        if not hasattr(self, "_event_bus_instance"):
            spec = importlib.util.spec_from_file_location(
                "event_bus", Path(__file__).parent / "NC-SVC-FR-005-event-bus.py"
            )
            if spec is None:
                raise ImportError("Failed to load event bus module")
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
            self._event_bus_module = module
            self._event_bus_instance = module.get_event_bus()
        return self._event_bus_instance

    @property
    def _neocortex_event_class(self):
        _ = self._event_bus  # ensure module loaded
        return self._event_bus_module.NeoCortexEvent

    def transition(self, new_state: str, reason: str = "") -> bool:
        """
        Attempt to transition to a new state.

        Args:
            new_state: Target state
            reason: Humanreadable reason for the transition

        Returns:
            True if transition is legal and performed, False otherwise.
        """
        if new_state not in self.ALLOWED_TRANSITIONS:
            logger.warning(
                f"Invalid transition attempt to unknown state '{new_state}' from '{self._state}'"
            )
            return False

        if new_state not in self.ALLOWED_TRANSITIONS[self._state]:
            logger.warning(f"Invalid transition from '{self._state}' to '{new_state}'")
            return False

        with self._lock:
            old_state = self._state
            self._state = new_state
            self._record_transition(new_state, reason, old_state)

        # Publish event after successful transition
        try:
            # Ensure event bus module loaded
            _ = self._event_bus  # load module
            self._event_bus_module.publish_agent_state_changed(
                old_state=old_state, new_state=new_state, agent_id=self._agent_id
            )
        except Exception:
            # Fallback silent as per R09
            pass

        return True

    def get_state(self) -> str:
        """Return current state."""
        return self._state

    def get_allowed_transitions(self) -> list[str]:
        """Lista de estados alcanveis do estado atual."""
        return self.ALLOWED_TRANSITIONS.get(self._state, [])[:]

    def get_history(self) -> list[dict[str, str]]:
        """
        Return full transition history.

        Each entry is a dict with keys:
            state: state after transition
            timestamp: ISO 8601 timestamp
            reason: reason provided for transition
            from_state: previous state (except for initialization)
        """
        return list(self._history)

    def is_terminal(self) -> bool:
        """Return True if current state is terminal (HANDOFF or ESCALATED)."""
        return self._state in self.TERMINAL_STATES

    def reset(self) -> None:
        """Reset machine to IDLE state, preserving history."""
        with self._lock:
            old_state = self._state
            self._state = self.IDLE
            self._record_transition(self.IDLE, reason="reset")
            # Publish event after reset
            try:
                # Ensure event bus module loaded
                _ = self._event_bus  # load module
                self._event_bus_module.publish_agent_state_changed(
                    old_state=old_state, new_state=self.IDLE, agent_id=self._agent_id
                )
            except Exception:
                # Fallback silent as per R09
                pass

    def _record_transition(
        self, state: str, reason: str = "", from_state: str | None = None
    ) -> None:
        """Internal helper to record a transition in history."""
        entry = {
            "state": state,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "reason": reason,
            "from_state": from_state if from_state is not None else "",
        }
        self._history.append(entry)

    def __repr__(self) -> str:
        return (
            f"AgentStateMachine(state={self._state}, history_len={len(self._history)})"
        )


# Singleton factory per agent_id
def get_state_machine(agent_id: str = "") -> AgentStateMachine:
    """Cria ou retorna StateMachine para agent_id."""
    with AgentStateMachine._instances_lock:
        if agent_id not in AgentStateMachine._instances:
            AgentStateMachine._instances[agent_id] = AgentStateMachine(
                agent_id=agent_id
            )
        return AgentStateMachine._instances[agent_id]


# Convenience function to create a new state machine
def create_agent_state_machine(
    initial_state: str = AgentStateMachine.IDLE,
) -> AgentStateMachine:
    """Create a new AgentStateMachine instance."""
    return AgentStateMachine(initial_state=initial_state)
