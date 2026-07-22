import json

import pytest
from li_telemetry.logging import configure_logging, get_logger


def test_logs_render_as_json(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(level="INFO")
    get_logger("test").info("hello", company_id="abc123")
    line = capsys.readouterr().out.strip().splitlines()[-1]
    event = json.loads(line)
    assert event["event"] == "hello"
    assert event["company_id"] == "abc123"
    assert event["level"] == "info"
    assert "timestamp" in event


def test_level_filtering(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(level="INFO")
    get_logger("test").debug("invisible")
    assert capsys.readouterr().out.strip() == ""
