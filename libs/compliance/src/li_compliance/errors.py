from li_core.errors import LeadIntelligenceError


class ComplianceError(LeadIntelligenceError):
    """Base class for compliance-gate violations."""


class DisallowedSourceError(ComplianceError):
    """A fetch was attempted against a source not in the allowlist (RISKS.md#data-tos)."""


class PersonDataError(ComplianceError):
    """A payload carried person-shaped data across the ingest boundary (ADR-005)."""
