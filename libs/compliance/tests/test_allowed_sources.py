import pytest
from li_compliance.allowed_sources import (
    DEFAULT_REGISTRY,
    AllowedSource,
    SourceKind,
    SourceRegistry,
)
from li_compliance.errors import DisallowedSourceError

FICTIONAL_SOURCE = AllowedSource(
    name="fictional-registry-vendor",
    kind=SourceKind.REGISTRY_API,
    domains=("api.example-registry.test",),
)


class TestDefaultRegistryIsEmpty:
    """No vendor is chosen yet (QUESTIONS.md#api-vendor): nothing may be fetchable."""

    def test_default_registry_has_no_sources(self) -> None:
        assert DEFAULT_REGISTRY.sources == ()

    @pytest.mark.parametrize(
        "url",
        [
            "https://api.example-registry.test/company/U12345MH2019PTC123456",
            "https://www.mca.gov.in/anything",
            "https://linkedin.com/in/anyone",
        ],
    )
    def test_default_registry_blocks_everything(self, url: str) -> None:
        with pytest.raises(DisallowedSourceError):
            DEFAULT_REGISTRY.require_allowed(url)


class TestRegistryMatching:
    def test_registered_domain_allowed(self) -> None:
        registry = SourceRegistry((FICTIONAL_SOURCE,))
        url = "https://api.example-registry.test/v1/company"
        assert registry.is_allowed(url)
        assert registry.require_allowed(url) is FICTIONAL_SOURCE

    def test_subdomain_of_registered_domain_allowed(self) -> None:
        registry = SourceRegistry((FICTIONAL_SOURCE,))
        assert registry.is_allowed("https://cdn.api.example-registry.test/x")

    def test_lookalike_suffix_domain_rejected(self) -> None:
        registry = SourceRegistry((FICTIONAL_SOURCE,))
        assert not registry.is_allowed("https://evilapi.example-registry.test.attacker.io/")
        assert not registry.is_allowed("https://notapi.example-registry.test.io/")

    def test_other_domain_rejected(self) -> None:
        registry = SourceRegistry((FICTIONAL_SOURCE,))
        with pytest.raises(DisallowedSourceError):
            registry.require_allowed("https://other.test/company")

    def test_hostless_url_rejected(self) -> None:
        registry = SourceRegistry((FICTIONAL_SOURCE,))
        assert not registry.is_allowed("not-a-url")

    def test_matching_is_case_insensitive(self) -> None:
        registry = SourceRegistry((FICTIONAL_SOURCE,))
        assert registry.is_allowed("https://API.Example-Registry.TEST/v1")
