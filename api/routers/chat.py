from fastapi import APIRouter
from api.services.agent import process_agent_chat
from api.schemas.profile import AgentChatRequest, AgentChatResponse

router = APIRouter()

@router.post("/chat", response_model=AgentChatResponse)
async def chat_endpoint(payload: AgentChatRequest):
    result = await process_agent_chat(
        user_message=payload.message,
        history=payload.history,
        profile=payload.profile,
        session_id=payload.session_id,
    )
    return result
