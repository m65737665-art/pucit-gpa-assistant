
import asyncio
from fastmcp import Client

MCP_URL = "https://pucit-cgpa-assistant.fastmcp.app/mcp"

async def main():
    client = Client(MCP_URL, auth="oauth")

    async with client:
        print("Connected successfully!")

        await client.ping()
        print("Server ping successful!")

        tools = await client.list_tools()

        print(f"\nDiscovered {len(tools)} tools:")

        for tool in tools:
            print("-", tool.name)

if __name__ == "__main__":
    asyncio.run(main())
