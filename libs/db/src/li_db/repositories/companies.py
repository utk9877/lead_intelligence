"""All SQL stays behind repository interfaces — services never build queries."""

import uuid

from li_core.ids import parse_cin, parse_gstin
from sqlalchemy import select
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
