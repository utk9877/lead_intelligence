"""robots.txt honoring for crawlers.

The fetcher is injectable so tests never touch the network; the real fetcher is
supplied by the ingestion service (chunk 2), which itself goes through the
allowed-sources registry first.
"""

from collections.abc import Callable
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

RobotsFetcher = Callable[[str], str]


class RobotsPolicy:
    def __init__(self, fetch_robots_txt: RobotsFetcher, user_agent: str) -> None:
        self._fetch = fetch_robots_txt
        self._user_agent = user_agent
        self._parsers: dict[str, RobotFileParser] = {}

    def _parser_for(self, url: str) -> RobotFileParser:
        parts = urlsplit(url)
        origin = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
        parser = self._parsers.get(origin)
        if parser is None:
            parser = RobotFileParser()
            parser.parse(self._fetch(origin + "/robots.txt").splitlines())
            self._parsers[origin] = parser
        return parser

    def can_fetch(self, url: str) -> bool:
        return self._parser_for(url).can_fetch(self._user_agent, url)
