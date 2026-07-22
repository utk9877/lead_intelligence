from datetime import UTC, datetime, timedelta

from li_scheduler.plans import DEFAULT_CADENCE, RefreshTarget, due_jobs

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)


def test_never_refreshed_target_is_due() -> None:
    targets = [RefreshTarget("c1", "registry_mca", "https://api.example-registry.test/c1", None)]
    jobs = due_jobs(targets, now=NOW)
    assert [j.company_id for j in jobs] == ["c1"]


def test_recently_refreshed_registry_target_is_not_due() -> None:
    targets = [
        RefreshTarget(
            "c1", "registry_mca", "https://x.test", NOW - timedelta(days=5)
        )  # cadence is 30d
    ]
    assert due_jobs(targets, now=NOW) == []


def test_stale_target_past_cadence_is_due() -> None:
    targets = [
        RefreshTarget("c1", "news_funding", "https://x.test", NOW - timedelta(days=2))
    ]  # news cadence is 1d
    assert len(due_jobs(targets, now=NOW)) == 1


def test_unknown_source_is_never_scheduled_blindly() -> None:
    targets = [RefreshTarget("c1", "mystery_source", "https://x.test", None)]
    assert due_jobs(targets, now=NOW) == []


def test_exact_cadence_boundary_is_due() -> None:
    targets = [
        RefreshTarget("c1", "news_funding", "https://x.test", NOW - DEFAULT_CADENCE["news_funding"])
    ]
    assert len(due_jobs(targets, now=NOW)) == 1
