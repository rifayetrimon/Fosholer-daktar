import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.integrations.embeddings.client import EmbeddingClient
from app.integrations.llm.client import chat_with_tools
from app.integrations.llm.prompts import CROP_DOCTOR_SYSTEM_PROMPT
from app.integrations.llm.tools import DISEASE_INFO_TOOL, SCAN_HISTORY_TOOL
from app.ml.classifier import classify_disease
from app.modules.chat.schemas import ChatMessage, ChatResponse
from app.modules.knowledge.service import KnowledgeService
from app.modules.scans.models import DiseaseScan
from app.modules.scans.repository import ScanRepository

logger = logging.getLogger("uvicorn.error")


class ChatService:
    def __init__(self, db: AsyncSession, user_id: uuid.UUID, embedding_client: EmbeddingClient):
        self.db = db
        self.user_id = user_id
        self.knowledge_svc = KnowledgeService(db, embedding_client)
        self.scan_repo = ScanRepository(db)

    async def _handle_tool_call(self, tool_name: str, args: dict) -> str:
        if tool_name == "get_disease_info":
            disease_name = args.get("disease_name", "")
            chunks = await self.knowledge_svc.search_relevant(disease_name, limit=3)
            if not chunks:
                return f"No specific information found for {disease_name}"
            return "\n\n".join([c.content for c in chunks])
        if tool_name == "get_scan_history":
            limit = int(args.get("limit", 5))
            scans = await self.scan_repo.list_by_user(self.user_id, None, None)
            recent = scans[:limit]
            if not recent:
                return "No scan history found for this user."
            lines = [
                f"{s.created_at.strftime('%Y-%m-%d')}: {s.predicted_disease.replace('___', ' – ')} "
                f"in {s.crop_name} ({s.confidence * 100:.0f}% confidence)"
                for s in recent
            ]
            return "Recent scan history:\n" + "\n".join(lines)
        return "Tool not found"

    async def chat(
        self,
        message: str,
        history: list[ChatMessage],
        image_bytes: bytes | None = None,
    ) -> ChatResponse:
        disease_detected = None
        confidence = None

        if image_bytes:
            result = await classify_disease(image_bytes)
            disease_detected = result.get("label")
            confidence = result.get("confidence")

            parts = (disease_detected or "").split("___")
            crop_name = parts[0] if len(parts) > 1 else "Unknown"
            disease_name = parts[1].replace("_", " ") if len(parts) > 1 else disease_detected

            if disease_detected and disease_detected != "Unknown___Unknown":
                scan = DiseaseScan(
                    user_id=self.user_id,
                    crop_name=crop_name,
                    predicted_disease=disease_detected,
                    confidence=confidence or 0.0,
                )
                try:
                    await self.scan_repo.create(scan)
                except Exception as exc:
                    logger.error("Failed to save disease scan (non-fatal): %s", exc)
                    try:
                        await self.db.rollback()
                    except Exception as rb_exc:
                        logger.error("Rollback failed: %s", rb_exc)

            if not message:
                message = f"My {crop_name} crop has {disease_name}. What should I do?"
            else:
                message = f"[Detected disease: {disease_name} in {crop_name} ({(confidence or 0)*100:.0f}% confidence)]\n{message}"

        if not message:
            return ChatResponse(reply="Please send a message or an image.", sources_used=False)

        search_query = message
        relevant_chunks = await self.knowledge_svc.search_relevant(search_query, limit=3)
        sources_used = len(relevant_chunks) > 0

        rag_context = (
            "\n\nRelevant knowledge base information:\n"
            + "\n---\n".join(c.content for c in relevant_chunks)
            if relevant_chunks
            else "\n\n[No relevant information found in the knowledge base]"
        )

        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": message})

        reply = await chat_with_tools(
            messages=messages,
            system_prompt=CROP_DOCTOR_SYSTEM_PROMPT + rag_context,
            tools=[DISEASE_INFO_TOOL, SCAN_HISTORY_TOOL],
            tool_handler=self._handle_tool_call,
        )

        return ChatResponse(
            reply=reply,
            sources_used=sources_used,
            disease_detected=disease_detected,
            confidence=confidence,
        )
