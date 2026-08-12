import logging
from sqlalchemy.orm import Session

from app.ai.embeddings import embed_query
from app.services.document_service import _get_vector_store
from app.repositories.document_repository import DocumentRepository
from app.services.activity_service import ActivityLogService
from app.schemas.schemas import SearchResponse, SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._doc_repo = DocumentRepository(db)
        self._activity = ActivityLogService(db)

    def search(self, query: str, user_id: int, top_k: int = 5) -> SearchResponse:
        # Validate query
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty")
        if len(query) > 500:
            raise ValueError("Query is too long (maximum 500 characters)")
        if top_k <= 0 or top_k > 50:
            raise ValueError("top_k must be between 1 and 50")

        logger.info("Executing semantic search for user %d: '%s'", user_id, query)

        # Log query
        self._activity.log(
            user_id=user_id,
            action="SEARCH",
            details={"query": query},
        )

        store = _get_vector_store()
        if store.total_vectors == 0:
            return SearchResponse(query=query, results=[])

        # Generate embedding
        query_vector = embed_query(query)

        # Search vector store
        raw_results = store.search(query_vector, top_k=top_k)

        # Build response with document metadata
        results = []
        for chunk, score in raw_results:
            # We fetch document metadata to confirm it exists and get its details
            doc = self._doc_repo.get_by_id(chunk.document_id)
            if doc is None:
                continue

            results.append(
                SearchResult(
                    document_id=doc.id,
                    original_filename=doc.original_filename,
                    score=float(score),
                    chunk_text=chunk.text,
                )
            )

        return SearchResponse(query=query, results=results)
