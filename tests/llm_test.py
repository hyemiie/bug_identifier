import pytest
from httpx import ASGITransport, AsyncClient
from main import app
from helper import core


@pytest.mark.asyncio
async def test_find_bug_with_mocked_ai(monkeypatch):
    def mock_ai_suggestion(code_snippet, language, tone):
        return {
            "summary": "This is a mock response.",
            "bugs": ["Syntax error at line 1", "Potential logic bug"]
        }

    monkeypatch.setattr(core, "get_ai_suggestion", mock_ai_suggestion)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/find-bug", json={
            "code_snippet": "if x = 5:",
            "language": "Python",
            "tone": "dev"
        })

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_find_bug_ai_quota_exceeded(monkeypatch):
    def mock_ai_fail(code_snippet, language, tone):
        raise Exception("429 Quota exceeded")

    monkeypatch.setattr(core, "get_ai_suggestion", mock_ai_fail)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/find-bug", json={
            "code_snippet": "total = sum(numbers) / len(numbers)",
            "language": "Python",
            "tone": "dev"
        })
    data = res.json()
    assert data.get("error") == "429 Quota exceeded"

@pytest.mark.asyncio
async def test_find_bug_code_length_exceeded():
    long_snippet = "\n".join([f"print({i})" for i in range(31)])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/find-bug", json={
            "code_snippet": long_snippet,
            "language": "Python",
            "tone": "neutral"
        })
    data = res.json()
    print(res.status_code)
    assert res.status_code == 400
    assert res.json().get("detail") == "Snippet length's greater than 30"
