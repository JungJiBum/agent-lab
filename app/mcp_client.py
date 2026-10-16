from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def list_mcp_tools():
    server = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp_server"],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_tools()
            
            return [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in result.tools
            ]


async def call_mcp_tool(name: str, arguments: dict | None = None):
    print(
        f"[MCP TOOL CALL] name={name}, arguments={arguments}",
        flush=True,
    )
    
    server = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp_server"],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                name=name,
                arguments=arguments or {},
            )

            if result.isError:
                raise RuntimeError(
                    f"MCP tool failed: {result.content}"
                )

            return result.structuredContent or [
                item.model_dump() for item in result.content
            ]
