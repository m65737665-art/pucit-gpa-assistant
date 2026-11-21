
import asyncio
import os
from dotenv import load_dotenv
from langchain.mcp import MCPAdapter

load_dotenv()

MCP_URL = os.getenv("MCP_URL")


async def main():

    async with MCPAdapter(MCP_URL) as adapter:

        tools = await adapter.list_tools()

        print("\nConnected to MCP server!")
        print("\nAvailable tools:")

        for tool in tools:
            print(f"\nTool name: {tool.name}")
            print(f"Description: {tool.description}")

        print(f"\nTotal tools discovered: {len(tools)}")


if __name__ == "__main__":
    asyncio.run(main())
