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
        # Identifier validity is enforced at the write boundary, not trusted upstream.
        if cin is not None:
            parse_cin(cin)
        if gstin is not None:
            parse_gstin(gstin)
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
