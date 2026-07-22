"""Driver-agnostic queue interface.

Services import this, never a driver directly (docs/ARCHITECTURE.md §3): the
Procrastinate driver is the P1/P2 implementation, an SQS driver is the P3 option.
Claim/complete semantics live inside the driver's worker runtime; the surface
services need is deferring work.
"""

from collections.abc import Mapping
from typing import Protocol, runtime_checkable


@runtime_checkable
class QueueDriver(Protocol):
    def enqueue(
        self,
        task: str,
        payload: Mapping[str, object],
        *,
        queue: str = "default",
    ) -> str:
        """Defer a job; returns the driver's job id."""
        ...
