from pydantic import BaseModel, Field
from typing import Optional, List


class SortingInputUpdate(BaseModel):
    sorter_id: Optional[str] = Field(None, description="Sorter identifier")
    tag_serial_no: Optional[str] = Field(None, description="Tag serial number")
    is_complete: bool = Field(False, description="True if all fields are filled")


class SortingChatRequest(BaseModel):
    message: str = Field(..., description="User message to the agent")
    history: List[dict] = Field(default_factory=list, description="Chat history")
    sorting: SortingInputUpdate = Field(
        default_factory=SortingInputUpdate,
        description="Current sorting input state from the UI",
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for server-side memory",
    )


class SortingChatResponse(BaseModel):
    message: str = Field(..., description="Agent response message")
    action: str = Field(..., description="Agent action name")
    missing_fields: List[str] = Field(default_factory=list)
    sorting: SortingInputUpdate
    is_complete: bool = Field(False, description="True if all fields are filled")
    session_id: str = Field(..., description="Session identifier for server-side memory")
