import sys

from dotenv import load_dotenv

load_dotenv()

import anthropic

from nba_recap.tools import TOOLS
from nba_recap.prompts import RECAP_PROMPT


def process_stream_event(event):
    if event.type == "content_block_delta" and event.delta.type == "text_delta":
        print(event.delta.text, end="", flush=True)
    elif event.type == "content_block_start" and event.content_block.type == "tool_use":
        print(f"\n\n--- Tool Call: {event.content_block.name} ---")


def print_tool_inputs(message):
    for block in message.content:
        if block.type == "tool_use":
            print(f"Input: {block.input}")
            print()


def main():
    if len(sys.argv) < 2:
        print("Usage: recap <team_name>")
        print("Example: recap lakers")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    client = anthropic.Anthropic()

    runner = client.beta.messages.tool_runner(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=TOOLS,
        messages=[
            {"role": "user", "content": RECAP_PROMPT.format(user_input=user_input)}
        ],
        stream=True,
    )

    print("\n--- Assistant ---\n")
    for message_stream in runner:
        for event in message_stream:
            process_stream_event(event)

        print_tool_inputs(message_stream.get_final_message())

    print("\n--- Done ---\n")


if __name__ == "__main__":
    main()
