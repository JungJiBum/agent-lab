import json

import httpx

from app.config import settings
from app.providers.base import LLMProvider
from app.tools.host_client import (
    get_host_status_remote,
    get_container_status_remote,
)
from app.mcp_client import call_mcp_tool, list_mcp_tools

# TOOLS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_host_status",
#             "description": "Mac mini 호스트 서버의 CPU와 메모리 상태를 조회합니다.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {},
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_container_status",
#             "description": "현재 실행 중인 Docker 컨테이너들의 CPU와 메모리 상태를 조회합니다.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {},
#             },
#         },
#     },
# ]


# TOOL_HANDLERS = {
#     "get_host_status": get_host_status_remote,
#     "get_container_status": get_container_status_remote,
# }
MAX_TOOL_ROUNDS = 10

SYSTEM_PROMPT = """
너는 MCP 도구를 활용해 운영 상태를 진단하고
Obsidian 문서를 검색하는 AI Agent다.

규칙:
1. Docker 컨테이너 및 호스트 상태 질문은 관련 MCP 도구를 호출한다.
2. Obsidian 문서, 개인 기록, 일정, 학습 내용에 관한 질문은
   반드시 search_obsidian 도구를 호출한다.
3. 도구를 호출하지 않았다면 검색하거나 확인했다고 주장하지 않는다.
4. 검색 결과에 없는 정보는 임의로 만들어내지 않는다.
5. 확인된 사실과 추정 내용을 구분한다.
6. 동일한 정보를 불필요하게 반복 조회하지 않는다.
7. 답변은 간결한 한국어로 작성한다.

답변 형식:
- Docker 장애 진단 질문:
  [관측된 사실]
  [장애 원인]
  [권장 조치]
  [추가 확인 필요 사항]

- Obsidian 문서 검색 질문:
  질문에 직접 답하고, 참고한 문서의 이름을 함께 표시한다.
  검색 결과에서 답을 찾지 못했다면 확인되지 않았다고 설명한다.
"""

class OllamaProvider(LLMProvider):
    async def chat(self, message: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        tools = await list_mcp_tools()
        tool_cache: dict[str, object] = {}
        timeout = httpx.Timeout(
            connect=10.0,
            read=300.0,
            write=30.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            for _ in range(MAX_TOOL_ROUNDS):
                response = await client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": settings.ollama_model,
                        "messages": messages,
                        "tools": tools,
                        "stream": False,
                    },
                )
                response.raise_for_status()

                assistant_message = response.json()["message"]
                messages.append(assistant_message)

                tool_calls = assistant_message.get("tool_calls") or []

                if not tool_calls:
                    return assistant_message.get("content", "")

                for tool_call in tool_calls:
                    name = tool_call["function"]["name"]
                    arguments = tool_call["function"].get("arguments") or {}

                    cache_key = json.dumps(
                        {"name": name, "arguments": arguments},
                        sort_keys=True,
                        ensure_ascii=False,
                    )
                    if cache_key in tool_cache:
                        print(
                            f"[MCP CACHE HIT] {name} arguments={arguments}",
                            flush=True,
                        )
                        result= tool_cache[cache_key]
                    else:
                        print(
                            f"[MCP CALL] {name} arguments={arguments}",
                            flush=True,
                        )
                        try:
                            result = await call_mcp_tool(name, arguments)
                            # 현재 4가지 도구는 모두 읽기 전용 조회 도구
                            tool_cache[cache_key] = result
                        except Exception as exc:
                            result = {
                                "error": type(exc).__name__,
                                "message": str(exc),
                            }
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": name,
                            "content": json.dumps(result, ensure_ascii=False),
                        }
                    )

        return "도구 호출 횟수 제한을 초과했습니다."
