import pytest
from httpx import ASGITransport, AsyncClient
from main import app
from helper import core


@pytest.mark.asyncio
async def test_rate_limit_triggered(monkeypatch):
    def mock_ai_success(code_snippet, language, tone):
        return "This is a mocked AI response"
    
    monkeypatch.setattr(core, "get_ai_suggestion", mock_ai_success)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "code_snippet": "print('Hello')",
            "language": "Python",
            "tone": "dev"
        }

        for i in range(9):
            res = await ac.post("/find-bug", params=payload)
            if res.status_code != 429: 
                assert res.status_code == 200
            else:
                break
            
        response = await ac.post("/find-bug", params=payload)  
        assert response.status_code == 429
        assert "rate limit exceeded" in response.text.lower()