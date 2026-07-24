"""All SQL stays behind repository interfaces — services never build queries."""

import uuid

from li_core.ids import parse_cin, parse_gstin
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from li_db.orm import Company


class CompanyRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        *,
        name: str,
        cin: str | None = None,
        gstin: str | None = None,
        domain: str | None = None,
    ) -> Company:
        # Validate AND canonicalize at the write boundary: the partial unique indexes
        # on cin/gstin are case-sensitive, so storing the raw string would let "U…"
        # and " u… " persist as two companies and defeat registry-anchor dedup (ADR-001).
        if cin is not None:
            cin = parse_cin(cin).normalized
        if gstin is not None:
            gstin = parse_gstin(gstin).normalized
        company = Company(name=name, cin=cin, gstin=gstin, domain=domain)
        self._session.add(company)
        self._session.flush()
        return company

    def get(self, company_id: uuid.UUID) -> Company | None:
        return self._session.get(Company, company_id)

    def get_by_cin(self, cin: str) -> Company | None:
        return self._session.scalar(select(Company).where(Company.cin == cin))

    def get_by_gstin(self, gstin: str) -> Company | None:
        return self._session.scalar(select(Company).where(Company.gstin == gstin))

    def get_by_domain(self, domain: str) -> list[Company]:
        # Domain is not unique (subsidiaries, shared parent sites), so a domain
        # match can be ambiguous — the resolver decides, hence a list.
        return list(self._session.scalars(select(Company).where(Company.domain == domain)).all())

    def find_by_pan(self, pan: str) -> list[Company]:
        # GSTINs embed the 10-char PAN at positions 3-12 (1-indexed). Same PAN =
        # same legal entity registered in different states; the resolver queues
        # these for human merge rather than auto-linking (single-gstin model).
        return list(
            self._session.scalars(
                select(Company).where(func.substring(Company.gstin, 3, 10) == pan)
            ).all()
        )

    def enrich(
        self, company: Company, *, gstin: str | None = None, domain: str | None = None
    ) -> Company:
        """Fill in a missing identifier on an already-matched company, so a later
        candidate carrying that identifier resolves instead of duplicating."""
        if gstin is not None and company.gstin is None:
            company.gstin = parse_gstin(gstin).normalized
        if domain is not None and company.domain is None:
            company.domain = domain
        self._session.flush()
        return company
