from li_compliance.robots import RobotsPolicy

ROBOTS_TXT = """
User-agent: *
Disallow: /private/

User-agent: li-bot
Disallow: /careers/internal/
"""


def make_policy(user_agent: str) -> tuple[RobotsPolicy, list[str]]:
    fetched: list[str] = []

    def fetch(url: str) -> str:
        fetched.append(url)
        return ROBOTS_TXT

    return RobotsPolicy(fetch, user_agent), fetched


def test_disallowed_path_blocked() -> None:
    policy, _ = make_policy("li-bot")
    assert not policy.can_fetch("https://site.test/careers/internal/page")


def test_allowed_path_permitted() -> None:
    policy, _ = make_policy("li-bot")
    assert policy.can_fetch("https://site.test/careers/openings")


def test_wildcard_rules_apply_to_other_agents() -> None:
    policy, _ = make_policy("some-other-bot")
    assert not policy.can_fetch("https://site.test/private/x")
    assert policy.can_fetch("https://site.test/careers/internal/page")


def test_robots_fetched_once_per_origin() -> None:
    policy, fetched = make_policy("li-bot")
    policy.can_fetch("https://site.test/a")
    policy.can_fetch("https://site.test/b")
    policy.can_fetch("https://other.test/c")
    assert fetched == ["https://site.test/robots.txt", "https://other.test/robots.txt"]
