from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.integrations.embeddings.dependencies import EmbeddingDep
from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.auth.models import User
from app.modules.knowledge.schemas import KnowledgeIngestRequest, KnowledgeResponse
from app.modules.knowledge.service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/ingest", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def ingest_knowledge(
    data: KnowledgeIngestRequest,
    embeddings: EmbeddingDep,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    svc = KnowledgeService(db, embeddings)
    return await svc.ingest(data)


@router.post("/upload-document", response_model=list[KnowledgeResponse], status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    embeddings: EmbeddingDep,
    disease_name: str = Form(...),
    crop_name: str = Form(...),
    source: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    file_bytes = await file.read()
    svc = KnowledgeService(db, embeddings)
    return await svc.ingest_document(
        file_bytes=file_bytes,
        filename=file.filename or "document",
        disease_name=disease_name,
        crop_name=crop_name,
        source=source,
    )


@router.get("/", response_model=list[KnowledgeResponse])
async def list_knowledge(
    embeddings: EmbeddingDep,
    disease_name: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    svc = KnowledgeService(db, embeddings)
    return await svc.list_knowledge(disease_name)
