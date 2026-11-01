"""Optional Python implementation; the video explains roles, not this syntax.

Example policy: one process/thread; no replay on subscribe; unique observers;
synchronous insertion order; snapshot for an event; listener errors propagate;
reentrant status changes are rejected before mutation. No retries or rollback.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class StatusChanged:
    order_id: str
    status: str


class Order:
    def __init__(self, order_id: str, status: str = "待付款"):
        self.order_id = order_id
        self.status = status
        self._observers: list[Callable[[StatusChanged], None]] = []
        self._notifying = False

    def subscribe(self, observer: Callable[[StatusChanged], None]):
        if observer in self._observers:
            raise ValueError("observer is already subscribed")
        self._observers.append(observer)
        active = True

        def cancel():
            nonlocal active
            if active:
                self._observers.remove(observer)
                active = False

        return cancel

    def change_status(self, new_status: str):
        if self._notifying:
            raise RuntimeError("reentrant status changes are outside this example")
        if self.status == new_status:
            return
        self.status = new_status
        event = StatusChanged(self.order_id, new_status)
        current_observers = tuple(self._observers)
        self._notifying = True
        try:
            for observer in current_observers:
                observer(event)
        finally:
            self._notifying = False


class Summary:
    def __init__(self, initial_status: str = "待付款"):
        self.status = initial_status
        self.events: list[StatusChanged] = []

    def receive(self, event: StatusChanged):
        self.status = event.status
        self.events.append(event)


class ChangeLog:
    def __init__(self):
        self.events: list[StatusChanged] = []

    def receive(self, event: StatusChanged):
        self.events.append(event)

    @property
    def change_count(self):
        return len(self.events)
