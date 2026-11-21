from llm import llm

from langchain.agents import create_agent

from langchain.messages import HumanMessage, ToolMessage

import asyncio
import os

from dotenv import load_dotenv
from langchain.mcp import MCPAdapter

from fastmcp import Client
from langchain.mcp import MCPAdapter

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

load_dotenv()

MCP_URL = os.getenv("MCP_URL")
SYSTEM_PROMPT = """You are a helpful academic advisor for PUCIT BS(CS) students.

Semester graded credit hours in PUCIT BS(CS):
- Semester 1: 15.5
- Semester 2: 15.5
- Semester 3: 16.5
- Semester 4: 16.5
- Semester 5: 18.5
- Semester 6: 18.5
- Semester 7: 18.5
- Semester 8: 14.5
Total degree credit hours: 134.0.

Rules:
1. Never calculate numbers in your head. Always call a tool for every calculation.
2. Never invent or guess missing marks, credit hours, or CGPA. Ask the student for missing information only when it is needed to perform the calculation.
3. If the course names clearly identify a semester from the PUCIT course data (for example, Analysis of Algorithms, AI, and HCI belong to Semester 5), use that semester. Ask for the semester only when it cannot be determined.
4. For marks outside 0 to 100, call marks_to_grade_points and return its error.
5. Math Deficiency courses (MD-001, MD-002) are non-credit pass/fail and excluded from GPA. Quran Translation is 0.5 credit hours and included.
6. If a student mentions course names without credit hours, call get_semester_courses to find their credit hours. When a student gives marks for specific courses, calculate the GPA using only those provided courses—do NOT ask for marks of other courses in that semester.
7. Progressive Target Horizon Rule (§2.6):
   When a student asks what GPA they need to reach a target CGPA:
   - DO NOT calculate across all remaining credit hours to graduation directly (never jump to Semesters 5–8 giving 3.77).
   - Start from the student's current semester and evaluate progressive horizons one by one:
     * Horizon 1 (Current semester only): Use the credit hours for the current semester. Call required_gpa_for_target(target_cgpa, current_cgpa, completed_ch, horizon_ch). If the required GPA is > 4.0, mark it (impossible).
     * Horizon 2 (Current + next semester): Add the next semester's credit hours. Call required_gpa_for_target with the combined credit hours. If > 4.0, mark it (impossible).
     * Horizon 3 (Current + next 2 semesters): Add that semester's credit hours. Call required_gpa_for_target. If <= 4.0, mark it (achievable).
     * Continue widening one semester at a time if needed until required GPA <= 4.0.
   - Stop at the first horizon where required GPA is <= 4.0.
   - Present the output displaying each evaluated horizon and its verdict, for example:
     Semester 5 only: 4.78 (impossible)
     Semesters 5 6: 4.09 (impossible)
     Semesters 5 7: 3.86 (achievable)

     Final answer:
     "You need a GPA of 3.86 over Semesters 5 7 to reach a CGPA of 3.4."
   - Every required GPA value MUST come from calling required_gpa_for_target; never hardcode or invent numbers.
8. Offer to save a report only after calculating a semester GPA, projected CGPA, or target GPA advice. Never save without being asked.
9. Be friendly, encouraging, and clear.
10. Scope and calculation restriction:
    - You are exclusively a PUCIT GPA and CGPA assistant.
    - Only answer questions related to academic GPA, CGPA,
      PUCIT courses, credit hours, and academic progress.
    - For every numerical calculation, you MUST use an
      appropriate available tool.
    - Never perform arithmetic yourself, even simple
      addition, subtraction, multiplication, or division.
    - If the user asks for a calculation that your available
      tools cannot perform, explain that you do not have
      an appropriate tool for that calculation.
    - Do not answer unrelated general mathematics questions.
"""

async def list_threads(memory):
    print("\nSaved student chats:")

    saved_names = set()

    async for checkpoint in memory.alist(None):
        thread_id = checkpoint.config["configurable"].get("thread_id")

        if thread_id:
            saved_names.add(thread_id)

    if not saved_names:
        print("No previous chats found.")
    else:
        for name in sorted(saved_names):
            print("-", name)


async def show_history(app, config):

    state = await app.aget_state(config)

    messages = state.values.get("messages", [])

    if not messages:
        print("\nNo conversation history found.")
        return

    print("\nConversation history:")

    for message in messages:

        if message.type == "human":
            label = "You"

        elif message.type == "ai":
            label = "Agent"

        elif message.type == "tool":
            label = f"Tool ({message.name})"

        else:
            label = message.type

        if message.content:
            print(f"\n{label}: {message.content}")

        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print(f"\nAgent requested tool: {call['name']}")




async def recover_interrupted_tool_calls(app, config):

    # Get the saved conversation
    state = await app.aget_state(config)

    messages = state.values.get("messages", [])

    if not messages:
        return

    # Store tool call IDs that have received results
    completed_tool_calls = set()

    for message in messages:
        if isinstance(message, ToolMessage):
            completed_tool_calls.add(message.tool_call_id)

    # Find AI tool calls that never received a result
    recovery_messages = []

    for message in messages:

        if message.type == "ai":

            for call in getattr(message, "tool_calls", []):

                call_id = call.get("id")

                if call_id and call_id not in completed_tool_calls:

                    print(
                        f"\n[Recovery] Found interrupted tool call: "
                        f"{call['name']}"
                    )

                    recovery_messages.append(
                        ToolMessage(
                            content=(
                                "This tool call was interrupted because "
                                "the MCP server or network connection failed. "
                                "The result is unavailable. Please retry "
                                "the operation if appropriate."
                            ),
                            tool_call_id=call_id,
                            name=call["name"],
                            status="error"
                        )
                    )

                    completed_tool_calls.add(call_id)

    # Save the repair to SQLite through LangGraph
    if recovery_messages:

        await app.aupdate_state(
            config,
            {"messages": recovery_messages}
        )

        print(
            f"[Recovery] Repaired {len(recovery_messages)} "
            "interrupted tool call(s)."
        )

    else:
        print("[Recovery] No interrupted tool calls found.")


async def main():

    if not MCP_URL:
        print("Error: MCP_URL is missing.")
        return

    async with AsyncSqliteSaver.from_conn_string("checkpoints.sqlite") as memory:

        client = Client(MCP_URL, auth="oauth")
        
        async with MCPAdapter(client) as adapter:

            tools = await adapter.list_tools()

            print(f"Connected! Discovered {len(tools)} tools.")

            app = create_agent(
                model=llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                checkpointer=memory
            )

            # Show saved student chats
            await list_threads(memory)

            # Ask who is using the assistant
            current_name = input("\nWho is chatting? Enter your name: ").strip()

            if not current_name:
                print("Name cannot be empty.")
                return

            print(f"\nWelcome, {current_name}!")
            print("Commands: /switch, /history, /forget, exit\n")

            while True:

                user_input = input(f"{current_name}: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break

                # Switch student
                elif user_input.lower() == "/switch":

                    new_name = input("Enter the next student's name: ").strip()

                    if new_name:
                        current_name = new_name
                        print(f"Switched to {current_name}.")

                    continue

                # Show conversation history
                elif user_input.lower() == "/history":

                    config = {
                        "configurable": {
                            "thread_id": current_name
                        }
                    }

                    await show_history(app, config)
                    continue

                # Delete current student's conversation
                elif user_input.lower() == "/forget":

                    await memory.adelete_thread(current_name)

                    print(f"Conversation history for {current_name} deleted.")
                    continue

                # Normal conversation
                config = {
                    "configurable": {
                        "thread_id": current_name
                    }
                }

                # Recover interrupted tool calls
                await recover_interrupted_tool_calls(app, config)

                try:
                    print("\nAgent: ", end="", flush=True)

                    async for chunk in app.astream(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config,
                        stream_mode=["updates", "messages"],
                        version="v2"
                    ):

                        # PART 1: Display the answer as it is generated
                        if chunk["type"] == "messages":
                            token, metadata = chunk["data"]

                            if metadata.get("langgraph_node") == "model" and token.text:
                                print(token.text, end="", flush=True)

                        # PART 2: Display tool calls and tool results
                        elif chunk["type"] == "updates":
                            for node, update in chunk["data"].items():

                                messages = update.get("messages", [])

                                if not messages:
                                    continue

                                # Agent requested a tool
                                if node == "model":
                                    msg = messages[-1]

                                    if getattr(msg, "tool_calls", None):
                                        for call in msg.tool_calls:
                                            print(
                                                f"\n[Agent requested tool: {call['name']}]"
                                            )

                                # Tool finished running
                                elif node == "tools":
                                    for msg in messages:
                                        print(
                                            f"\n[Tool {msg.name} returned: {msg.content}]"
                                        )

                    print("\n")

                except Exception as e:
                    print("\nError:", e, "\n")


if __name__ == "__main__":
    asyncio.run(main())