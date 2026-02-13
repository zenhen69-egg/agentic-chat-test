from pydantic import BaseModel, Field
from typing import Optional, List

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="User's full name")
    email: Optional[str] = Field(None, description="User's email address")
    bio: Optional[str] = Field(None, description="User's biography")
    is_complete: bool = Field(False, description="True if all fields are filled")


class AgentChatRequest(BaseModel):
    message: str = Field(..., description="User message to the agent")
    history: List[dict] = Field(default_factory=list, description="Chat history")
    profile: UserProfileUpdate = Field(
        default_factory=UserProfileUpdate,
        description="Current profile state from the UI",
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for server-side memory",
    )


class AgentChatResponse(BaseModel):
    message: str = Field(..., description="Agent response message")
    action: str = Field(..., description="Agent action name")
    missing_fields: List[str] = Field(default_factory=list)
    profile: UserProfileUpdate
    is_complete: bool = Field(False, description="True if all fields are filled")
    session_id: str = Field(..., description="Session identifier for server-side memory")
