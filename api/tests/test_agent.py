import pytest
from fastapi.testclient import TestClient
from main import app
from schemas.profile import UserProfileUpdate
from schemas.sorting import SortingInputUpdate
from services.features.user_profile.service import process_user_profile_chat
from services.features.sorting_input.service import process_sorting_input_chat

client = TestClient(app)


@pytest.mark.asyncio
async def test_process_user_profile_chat_missing_fields():
    profile = UserProfileUpdate()
    result = await process_user_profile_chat("My name is Taylor", [], profile)

    assert result.action == "request_more_info"
    assert "email" in result.missing_fields
    assert "bio" in result.missing_fields
    assert result.is_complete is False


@pytest.mark.asyncio
async def test_process_user_profile_chat_complete():
    profile = UserProfileUpdate()
    message = "My name is Taylor. Email is taylor@example.com. Bio: DevOps engineer."
    result = await process_user_profile_chat(message, [], profile)

    assert result.action == "submit_request"
    assert result.missing_fields == []
    assert result.is_complete is True


def test_profile_chat_endpoint():
    payload = {
        "message": "My name is Taylor. Email is taylor@example.com. Bio: DevOps engineer.",
        "history": [],
        "profile": {"full_name": "", "email": "", "bio": "", "is_complete": False},
    }
    response = client.post("/chat/profile", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "submit_request"
    assert data["is_complete"] is True


@pytest.mark.asyncio
async def test_process_sorting_input_chat_missing_fields():
    sorting = SortingInputUpdate()
    result = await process_sorting_input_chat("Sorter ID is S-100", [], sorting)

    assert result.action == "request_more_info"
    assert "tag_serial_no" in result.missing_fields
    assert result.is_complete is False


@pytest.mark.asyncio
async def test_process_sorting_input_chat_complete():
    sorting = SortingInputUpdate()
    message = "Sorter ID is S-100. Tag serial number is TAG-204."
    result = await process_sorting_input_chat(message, [], sorting)

    assert result.action == "submit_request"
    assert result.missing_fields == []
    assert result.is_complete is True


def test_sorting_chat_endpoint():
    payload = {
        "message": "Sorter ID is S-100. Tag serial number is TAG-204.",
        "history": [],
        "sorting": {"sorter_id": "", "tag_serial_no": "", "is_complete": False},
    }
    response = client.post("/chat/sorting", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "submit_request"
    assert data["is_complete"] is True
