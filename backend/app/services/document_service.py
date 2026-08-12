import logging
import os
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.ai.document_processor import chunk_text, extract_text
from app.ai.embeddings import embed_texts
from app.ai.vector_store import ChunkMetadata, VectorStore
from app.core.config import get_settings
from app.models.models import Document
from app.repositories.document_repository import DocumentRepository
from app.services.activity_service import ActivityLogService

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

# Module-level vector store singleton, initialized lazily
_vector_store: VectorStore | None = None


def _get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        _vector_store = VectorStore(settings.VECTOR_STORE_PATH)
    return _vector_store


class DocumentService:
    def __init__(self, db: Session) -> None:
        self._repo = DocumentRepository(db)
        self._db = db
        self._activity = ActivityLogService(db)

    def upload(
        self,
        file_content: bytes,
        original_filename: str,
        content_type: str,
        user_id: int,
    ) -> Document:
        extension = self._validate_extension(original_filename)
        self._validate_size(file_content)

        settings = get_settings()
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid.uuid4().hex}.{extension}"
        file_path = upload_dir / stored_filename

        with open(file_path, "wb") as f:
            f.write(file_content)

        document = Document(
            filename=stored_filename,
            original_filename=original_filename,
            file_type=extension,
            file_path=str(file_path),
            file_size=len(file_content),
            uploaded_by=user_id,
        )
        document = self._repo.create(document)

        # Index the document asynchronously-safe (still synchronous here)
        try:
            self._index_document(document)
        except Exception:
            logger.exception("Failed to index document %d", document.id)

        self._activity.log(
            user_id=user_id,
            action="DOCUMENT_UPLOAD",
            entity_type="document",
            entity_id=document.id,
            details={"filename": original_filename},
        )

        return document

    def list_documents(self, skip: int = 0, limit: int = 50) -> list[Document]:
        return self._repo.list_documents(skip=skip, limit=limit)

    def get_document(self, doc_id: int) -> Document | None:
        return self._repo.get_by_id(doc_id)

    def _index_document(self, document: Document) -> None:
        logger.info("Extracting text from document %d (%s)", document.id, document.original_filename)
        text = extract_text(document.file_path, document.file_type)
        if not text.strip():
            logger.warning("No text extracted from document %d", document.id)
            return

        chunks = chunk_text(text)
        logger.info("Document %d produced %d chunks", document.id, len(chunks))

        vectors = embed_texts(chunks)
        metadata_list = [
            ChunkMetadata(
                document_id=document.id,
                chunk_index=i,
                filename=document.original_filename,
                text=chunk,
            )
            for i, chunk in enumerate(chunks)
        ]

        store = _get_vector_store()
        store.add(vectors, metadata_list)
        logger.info("Document %d indexed (%d vectors)", document.id, len(chunks))

    def _validate_extension(self, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: .{ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        return ext

    def _validate_size(self, content: bytes) -> None:
        settings = get_settings()
        if len(content) > settings.max_upload_bytes:
            raise ValueError(
                f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB"
            )
