from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
import copy

from app.providers.ollama import OllamaProvider


class FakeResponse:
    def __init__(self, message):
        self.message = message

    def raise_for_status(self):
        pass

    def json(self):
        return {"message": self.message}


class FakeHTTPClient:
    def __init__(self, messages):
        self.responses = iter(FakeResponse(message) for message in messages)
        self.payloads = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, json):
        self.payloads.append(copy.deepcopy(json))
        return next(self.responses)


def tool_call(name="get_container_details", args=None):
    return {
        "function": {
            "name": name,
            "arguments": args or {"container_id": "fault-lab-api"},
        }
    }


@pytest.mark.asyncio
async def test_tool_result_is_passed_to_llm_and_answer_returned():
    http = FakeHTTPClient(
        [
            {"tool_calls": [tool_call()]},
            {"content": "환경변수 누락입니다."},
        ]
    )
    with patch(
        "app.providers.ollama.list_mcp_tools", new_callable=AsyncMock, return_value=[]
    ), patch(
        "app.providers.ollama.call_mcp_tool",
        new_callable=AsyncMock,
        return_value={"exit_code": 1},
    ) as call, patch(
        "app.providers.ollama.httpx.AsyncClient", return_value=http
    ):
        answer = await OllamaProvider().chat("진단해줘")
    assert answer == "환경변수 누락입니다."
    call.assert_awaited_once()
    assert http.payloads[1]["messages"][-1]["role"] == "tool"
    assert '"exit_code": 1' in http.payloads[1]["messages"][-1]["content"]


@pytest.mark.asyncio
async def test_identical_tool_calls_are_cached_per_chat():
    http = FakeHTTPClient(
        [
            {"tool_calls": [tool_call()]},
            {"tool_calls": [tool_call()]},
            {"content": "완료"},
        ]
    )
    with patch(
        "app.providers.ollama.list_mcp_tools", new_callable=AsyncMock, return_value=[]
    ), patch(
        "app.providers.ollama.call_mcp_tool",
        new_callable=AsyncMock,
        return_value={"status": "exited"},
    ) as call, patch(
        "app.providers.ollama.httpx.AsyncClient", return_value=http
    ):
        assert await OllamaProvider().chat("진단") == "완료"
    assert call.await_count == 1


@pytest.mark.asyncio
async def test_tool_error_is_sent_to_llm():
    http = FakeHTTPClient(
        [
            {"tool_calls": [tool_call()]},
            {"content": "도구 오류 발생"},
        ]
    )
    with patch(
        "app.providers.ollama.list_mcp_tools", new_callable=AsyncMock, return_value=[]
    ), patch(
        "app.providers.ollama.call_mcp_tool",
        new_callable=AsyncMock,
        side_effect=RuntimeError("docker unavailable"),
    ), patch(
        "app.providers.ollama.httpx.AsyncClient", return_value=http
    ):
        assert await OllamaProvider().chat("진단") == "도구 오류 발생"
    assert '"error": "RuntimeError"' in http.payloads[1]["messages"][-1]["content"]


@pytest.mark.asyncio
async def test_round_limit_stops_repeated_tool_calls():
    from app.providers.ollama import MAX_TOOL_ROUNDS

    http = FakeHTTPClient([{"tool_calls": [tool_call()]}] * MAX_TOOL_ROUNDS)
    with patch(
        "app.providers.ollama.list_mcp_tools", new_callable=AsyncMock, return_value=[]
    ), patch(
        "app.providers.ollama.call_mcp_tool",
        new_callable=AsyncMock,
        return_value={"status": "exited"},
    ) as call, patch(
        "app.providers.ollama.httpx.AsyncClient", return_value=http
    ):
        answer = await OllamaProvider().chat("진단")
    assert answer == "도구 호출 횟수 제한을 초과했습니다."
    assert len(http.payloads) == MAX_TOOL_ROUNDS
    assert call.await_count == 1  # repeated calls reuse cached results
