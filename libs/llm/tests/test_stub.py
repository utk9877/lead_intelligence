import pytest
from li_llm.stub import StubLLMClient, text_response


def test_requires_exactly_one_mode() -> None:
    with pytest.raises(ValueError):
        StubLLMClient()
    with pytest.raises(ValueError):
        StubLLMClient(responses=[text_response("x")], responder=lambda _: text_response("y"))


def test_queue_pops_in_order_and_records_calls() -> None:
    stub = StubLLMClient([text_response("a"), text_response("b")])
    r1 = stub.create(model="m", system="s", messages=[], max_tokens=1)
    r2 = stub.create(model="m", system="s", messages=[], max_tokens=1)
    assert (r1.text, r2.text) == ("a", "b")
    assert len(stub.calls) == 2


def test_queue_exhaustion_is_loud() -> None:
    stub = StubLLMClient([text_response("a")])
    stub.create(model="m", system="s", messages=[], max_tokens=1)
    with pytest.raises(AssertionError, match="ran out"):
        stub.create(model="m", system="s", messages=[], max_tokens=1)


def test_responder_mode_sees_the_request() -> None:
    seen: list[str] = []

    def responder(request: dict[str, object]) -> object:
        seen.append(str(request["model"]))
        return text_response("ok")

    stub = StubLLMClient(responder=responder)  # type: ignore[arg-type]
    stub.create(model="claude-x", system="s", messages=[], max_tokens=1)
    assert seen == ["claude-x"]
