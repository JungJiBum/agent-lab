from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.mcp_client import call_mcp_tool, list_mcp_tools


class AsyncContext:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, *args):
        return False


def mock_transport(session):
    return (
        patch("app.mcp_client.stdio_client", return_value=AsyncContext((object(), object()))),
        patch("app.mcp_client.ClientSession", return_value=AsyncContext(session)),
    )


@pytest.mark.asyncio
async def test_list_mcp_tools_converts_schema():
    session = SimpleNamespace(
        initialize=AsyncMock(),
        list_tools=AsyncMock(return_value=SimpleNamespace(tools=[
            SimpleNamespace(name="get_container_logs", description="Logs", inputSchema={"type": "object"})
        ])),
    )
    p1, p2 = mock_transport(session)
    with p1, p2:
        result = await list_mcp_tools()
    assert result == [{"type": "function", "function": {"name": "get_container_logs", "description": "Logs", "parameters": {"type": "object"}}}]
    session.initialize.assert_awaited_once()


@pytest.mark.asyncio
async def test_call_mcp_tool_returns_structured_content():
    session = SimpleNamespace(
        initialize=AsyncMock(),
        call_tool=AsyncMock(return_value=SimpleNamespace(isError=False, structuredContent={"status": "exited"}, content=[])),
    )
    p1, p2 = mock_transport(session)
    with p1, p2:
        result = await call_mcp_tool("get_container_details", {"container_id": "fault-lab-api"})
    assert result == {"status": "exited"}
    session.call_tool.assert_awaited_once_with(name="get_container_details", arguments={"container_id": "fault-lab-api"})


@pytest.mark.asyncio
async def test_call_mcp_tool_raises_on_tool_error():
    session = SimpleNamespace(
        initialize=AsyncMock(),
        call_tool=AsyncMock(return_value=SimpleNamespace(isError=True, structuredContent=None, content=["failed"])),
    )
    p1, p2 = mock_transport(session)
    with p1, p2, pytest.raises(RuntimeError, match="MCP tool failed"):
        await call_mcp_tool("get_container_logs", {"container_id": "missing"})
