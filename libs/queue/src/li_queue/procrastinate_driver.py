"""Procrastinate (Postgres-backed) queue driver — no broker to operate."""

from collections.abc import Mapping
from typing import Any, cast

import procrastinate


def build_app(conninfo: str) -> procrastinate.App:
    """One Procrastinate app per process; workers (chunk 2+) register tasks on it."""
    return procrastinate.App(connector=procrastinate.SyncPsycopgConnector(conninfo=conninfo))


class ProcrastinateDriver:
    """Adapts a Procrastinate app to the QueueDriver protocol.

    The app must be open (`with app.open():` or a worker context) before enqueue
    is called; owning that lifecycle is the caller's job.
    """

    def __init__(self, app: procrastinate.App) -> None:
        self._app = app

    def enqueue(
        self,
        task: str,
        payload: Mapping[str, object],
        *,
        queue: str = "default",
    ) -> str:
        # The interface accepts any mapping; Procrastinate requires JSON-serializable
        # values, which it enforces at defer time.
        json_payload = cast(dict[str, Any], dict(payload))
        job = self._app.configure_task(task, queue=queue).defer(payload=json_payload)
        return str(job)
