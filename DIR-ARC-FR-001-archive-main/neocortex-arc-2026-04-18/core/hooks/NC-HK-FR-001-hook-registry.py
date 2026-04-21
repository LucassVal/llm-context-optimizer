from typing import Callable, Any, Dict, List, Optional
import inspect


class Hook:
    def before_tool_call(
        self, tool_name: str, args: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> None:
        pass

    def after_tool_call(
        self, tool_name: str, result: Any, error: Optional[Exception]
    ) -> None:
        pass

    def on_error(self, error: Exception, context: Dict[str, Any]) -> None:
        pass

    def session_start(self, session_id: str, metadata: Dict[str, Any]) -> None:
        pass

    def session_end(self, session_id: str, metadata: Dict[str, Any]) -> None:
        pass

    def on_checkpoint(self, checkpoint_id: str, data: Dict[str, Any]) -> None:
        pass


class HookRegistry:
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {
            "before_tool_call": [],
            "after_tool_call": [],
            "on_error": [],
            "session_start": [],
            "session_end": [],
            "on_checkpoint": [],
        }

    def register(self, event: str, hook: Callable) -> None:
        if event not in self._hooks:
            raise ValueError(f"Unknown event: {event}")
        self._hooks[event].append(hook)

    def unregister(self, event: str, hook: Callable) -> None:
        if event not in self._hooks:
            raise ValueError(f"Unknown event: {event}")
        if hook in self._hooks[event]:
            self._hooks[event].remove(hook)

    def trigger(self, event: str, *args, **kwargs) -> None:
        for hook in self._hooks[event]:
            try:
                if inspect.ismethod(hook) or inspect.isfunction(hook):
                    hook(*args, **kwargs)
                else:
                    getattr(hook, event)(*args, **kwargs)
            except Exception as e:
                print(f"Error executing hook for event {event}: {e}")

    def register_hook_object(self, hook_obj: Hook) -> None:
        for event in self._hooks.keys():
            method = getattr(hook_obj, event, None)
            if callable(method):
                self.register(event, method)
