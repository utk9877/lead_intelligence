from li_agents.eval import DeliveredOutcome, precision_of_warm
from li_core.models import ScoreBand


def test_precision_counts_only_warm_or_hot_as_positives() -> None:
    outcomes = [
        DeliveredOutcome(ScoreBand.HOT, pursued=True),
        DeliveredOutcome(ScoreBand.WARM, pursued=True),
        DeliveredOutcome(ScoreBand.WARM, pursued=False),
        DeliveredOutcome(ScoreBand.NOT_WARM, pursued=False),  # not delivered as warm
    ]
    report = precision_of_warm(outcomes)
    assert report.delivered_warm == 3  # not_warm is excluded
    assert report.pursued == 2
    assert report.precision == 2 / 3


def test_precision_is_zero_when_nothing_called_warm() -> None:
    report = precision_of_warm([DeliveredOutcome(ScoreBand.NOT_WARM, pursued=False)])
    assert report.delivered_warm == 0
    assert report.precision == 0.0


def test_perfect_precision() -> None:
    outcomes = [DeliveredOutcome(ScoreBand.HOT, pursued=True) for _ in range(5)]
    assert precision_of_warm(outcomes).precision == 1.0
