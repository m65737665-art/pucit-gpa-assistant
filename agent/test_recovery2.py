
import asyncio

from langchain.messages import AIMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain.agents import create_agent

from llm import llm
from agent import recover_interrupted_tool_calls


async def main():

    # Use a separate SQLite database for this test.
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

        # Create TWO AI tool calls without their results.
        interrupted_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculate_semester_gpa",
                    "args": {"courses": []},
                    "id": "test_call_001",
                    "type": "tool_call"
                },
                {
                    "name": "calculate_new_cgpa",
                    "args": {},
                    "id": "test_call_002",
                    "type": "tool_call"
                }
            ]
        )

        await app.aupdate_state(
            config,
            {"messages": [interrupted_message]},
            as_node="model"
        )

        print("Created two interrupted tool calls.")

        # Run recovery for the first time.
        print("\n--- First recovery ---")
        await recover_interrupted_tool_calls(app, config)

        # Run recovery again to test duplicate prevention.
        print("\n--- Second recovery ---")
        await recover_interrupted_tool_calls(app, config)

        # Read the repaired conversation.
        state = await app.aget_state(config)
        messages = state.values.get("messages", [])

        print("\nFinal conversation:")

        for message in messages:
            print(
                type(message).__name__,
                getattr(message, "tool_call_id", None),
                getattr(message, "status", None)
            )

        # Verify that each tool call has exactly one result.
        print("\n--- Verification ---")

        all_passed = True

        for call_id in ["test_call_001", "test_call_002"]:

            count = sum(
                1 for message in messages
                if isinstance(message, ToolMessage)
                and message.tool_call_id == call_id
            )

            print(f"{call_id}: {count} result message(s)")

            if count != 1:
                all_passed = False

        print("\nRecovery and duplicate prevention:", all_passed)


if __name__ == "__main__":
    asyncio.run(main())
