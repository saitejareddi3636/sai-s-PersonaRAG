from fastapi import APIRouter

from app.core.config import get_settings
from app.rag.retrieve import retrieve_top_k
from app.schemas.chat import ChatRequest, ChatResponse, RetrievalHitSchema, SourceCitation
from app.services import llm_service
from app.services.session_store import get_session_store

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    settings = get_settings()
    store = get_session_store(settings.session_max_messages, settings.session_max_total_chars)
    session_id = store.ensure_session(body.session_id)
    history_text = store.get_history_text(session_id)

    hits, err = retrieve_top_k(body.question, settings=settings)

    result = await llm_service.generate_grounded_answer(
        body.question,
        session_id,
        retrieval_hits=hits,
        retrieval_error=err,
        settings=settings,
        conversation_history=history_text or None,
    )

    store.append_turn(session_id, "user", body.question)
    store.append_turn(session_id, "assistant", result.answer)

    return ChatResponse(
        answer=result.answer,
        confidence=result.confidence,
        grounding_note=result.grounding_note,
        sources=[
            SourceCitation(
                chunk_id=c.chunk_id,
                source_file=c.source_file,
                section_title=c.section_title,
                content_type=c.content_type,
                score=c.score,
                excerpt=c.excerpt,
            )
            for c in result.citations
        ],
        session_id=session_id,
        retrieval=[RetrievalHitSchema(**h.to_api_dict()) for h in hits],
        retrieval_error=err,
    )
