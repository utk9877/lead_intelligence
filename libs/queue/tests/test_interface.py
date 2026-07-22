"""Structural tests only: real defer/claim gets integration-tested in chunk 2,
when the first worker service exercises Procrastinate against Postgres end-to-end."""

from collections.abc import Mapping

from li_queue.interface import QueueDriver
from li_queue.procrastinate_driver import ProcrastinateDriver, build_app


class FakeDriver:
    def __init__(self) -> None:
        self.jobs: list[tuple[str, dict[str, object], str]] = []

    def enqueue(self, task: str, payload: Mapping[str, object], *, queue: str = "default") -> str:
        self.jobs.append((task, dict(payload), queue))
        return str(len(self.jobs))


def test_fake_driver_satisfies_protocol() -> None:
    driver: QueueDriver = FakeDriver()
    assert isinstance(driver, QueueDriver)


def test_procrastinate_driver_satisfies_protocol_without_connecting() -> None:
    app = build_app("postgresql://unused:unused@localhost:1/unused")
    driver = ProcrastinateDriver(app)
    assert isinstance(driver, QueueDriver)


def test_fake_driver_records_jobs() -> None:
    driver = FakeDriver()
    job_id = driver.enqueue("ingest.company", {"cin": "U12345MH2019PTC123456"}, queue="ingest")
    assert job_id == "1"
    assert driver.jobs == [("ingest.company", {"cin": "U12345MH2019PTC123456"}, "ingest")]
