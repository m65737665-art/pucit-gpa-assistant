
import asyncio

from langchain.messages import AIMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain.agents import create_agent

from llm import llm
from agent import recover_interrupted_tool_calls


async def main():

    async with AsyncSqliteSaver.from_conn_string(
        "recovery_test.sqlite"
    ) as memory:

        app = create_agent(
            model=llm,
            tools=[],
            system_prompt="You are a test agent.",
            checkpointer=memory
        )

        config = {
            "configurable": {
                "thread_id": "recovery_test"
            }
        }

        # Create a conversation with an unfinished tool call
        interrupted_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculate_semester_gpa",
                    "args": {"courses": []},
                    "id": "test_call_001",
                    "type": "tool_call"
                }
            ]
        )

        await app.aupdate_state(
            config,
            {"messages": [interrupted_message]},
            as_node="model"
        )

        print("Created an interrupted tool call.")

        # Run our recovery function
        await recover_interrupted_tool_calls(app, config)

        # Check whether the missing result was added
        state = await app.aget_state(config)

        messages = state.values.get("messages", [])

        print("\nFinal conversation:")

        for message in messages:
            print(
                type(message).__name__,
                getattr(message, "tool_call_id", None),
                getattr(message, "status", None)
            )

        repaired = any(
            isinstance(message, ToolMessage)
            and message.tool_call_id == "test_call_001"
            and message.status == "error"
            for message in messages
        )

        print("\nRecovery successful:", repaired)


if __name__ == "__main__":
    asyncio.run(main())
