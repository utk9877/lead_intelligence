"""Shared exception hierarchy for Lead Intelligence."""


class LeadIntelligenceError(Exception):
    """Base class for all Lead Intelligence errors."""


class InvalidIdentifierError(LeadIntelligenceError, ValueError):
    """A CIN or GSTIN failed structural or checksum validation."""
