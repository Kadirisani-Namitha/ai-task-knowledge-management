import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.deps import get_db
from app.models.models import User
from app.schemas.schemas import DocumentResponse
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> DocumentResponse:
    """Upload and index a document. Admin only."""
    service = DocumentService(db)
    
    # Read file content
    try:
        content = await file.read()
        doc = service.upload(
            file_content=content,
            original_filename=file.filename,
            content_type=file.content_type,
            user_id=current_user.id,
        )
        return DocumentResponse.model_validate(doc)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during document upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        )


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> list[DocumentResponse]:
    """List all uploaded documents. Admin only."""
    service = DocumentService(db)
    docs = service.list_documents()
    return [DocumentResponse.model_validate(d) for d in docs]
