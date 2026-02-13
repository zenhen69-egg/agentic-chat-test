import pytest
from fastapi.testclient import TestClient
from main import app
from schemas.profile import UserProfileUpdate
from services.agent import process_agent_chat

client = TestClient(app)


@pytest.mark.asyncio
async def test_process_agent_chat_missing_fields():
    profile = UserProfileUpdate()
    result = await process_agent_chat("My name is Taylor", [], profile)

    assert result.action == "request_more_info"
    assert "email" in result.missing_fields
    assert "bio" in result.missing_fields
    assert result.is_complete is False


@pytest.mark.asyncio
async def test_process_agent_chat_complete():
    profile = UserProfileUpdate()
    message = "My name is Taylor. Email is taylor@example.com. Bio: DevOps engineer."
    result = await process_agent_chat(message, [], profile)

    assert result.action == "submit_request"
    assert result.missing_fields == []
    assert result.is_complete is True


def test_chat_endpoint():
    payload = {
        "message": "My name is Taylor. Email is taylor@example.com. Bio: DevOps engineer.",
        "history": [],
        "profile": {"full_name": "", "email": "", "bio": "", "is_complete": False},
    }
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "submit_request"
    assert data["is_complete"] is True
