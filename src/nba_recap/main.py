import sys
from dotenv import load_dotenv

load_dotenv()

import anthropic
from nba_recap.tools import TOOLS


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
            {"role": "user", "content": f"Get me a recap of the {user_input} game"}
        ],
        stream=True,
    )

    final_message = runner.until_done()
    print(final_message.content[0].text)


if __name__ == "__main__":
    main()
