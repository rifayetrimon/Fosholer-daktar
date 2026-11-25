import asyncio
import sys
from pathlib import Path
sys.path.insert(0, ".")
from app.db.session import session_manager
from app.integrations.embeddings.dependencies import get_embedding_client
from app.modules.knowledge.service import KnowledgeService


async def ingest(file_path: str, disease_name: str, crop_name: str, source: str | None) -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"[error] File not found: {file_path}")
        sys.exit(1)

    file_bytes = path.read_bytes()
    embedding_client = get_embedding_client()

    async with session_manager.run():
        async with session_manager.session() as db:
            svc = KnowledgeService(db, embedding_client)
            chunks = await svc.ingest_document(
                file_bytes=file_bytes,
                filename=path.name,
                disease_name=disease_name,
                crop_name=crop_name,
                source=source or path.name,
            )
            print(f"[+] Ingested {len(chunks)} chunk(s) from '{path.name}'")
            for i, c in enumerate(chunks, 1):
                preview = c.content[:80].replace("\n", " ")
                print(f"    chunk {i}: {preview}…")

    print("Ingest complete.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    _file   = sys.argv[1]
    _disease = sys.argv[2]
    _crop   = sys.argv[3]
    _source = sys.argv[4] if len(sys.argv) > 4 else None

    asyncio.run(ingest(_file, _disease, _crop, _source))
