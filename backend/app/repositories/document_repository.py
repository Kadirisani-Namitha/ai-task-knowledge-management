from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, doc_id: int) -> Document | None:
        return self._db.get(Document, doc_id)

    def list_documents(self, skip: int = 0, limit: int = 50) -> list[Document]:
        stmt = select(Document).offset(skip).limit(limit)
        return list(self._db.scalars(stmt).all())

    def create(self, document: Document) -> Document:
        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        self._db.delete(document)
        self._db.commit()
