from fastapi import APIRouter
from api.schemas.profile import AgentChatRequest, AgentChatResponse
from api.schemas.sorting import SortingChatRequest, SortingChatResponse
from api.services.features.sorting_input.service import process_sorting_input_chat
from api.services.features.user_profile.service import process_user_profile_chat

router = APIRouter()

@router.post("/chat/profile", response_model=AgentChatResponse)
async def profile_chat_endpoint(payload: AgentChatRequest):
    result = await process_user_profile_chat(
        user_message=payload.message,
        history=payload.history,
        profile=payload.profile,
        session_id=payload.session_id,
    )
    return result


@router.post("/chat/sorting", response_model=SortingChatResponse)
async def sorting_chat_endpoint(payload: SortingChatRequest):
    result = await process_sorting_input_chat(
        user_message=payload.message,
        history=payload.history,
        sorting=payload.sorting,
        session_id=payload.session_id,
    )
    return result
