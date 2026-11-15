import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from .env
MODEL = os.getenv("MODEL", "claude-haiku-5-5")

SYSTEM_PROMPT = (
    "You are a helpful assistant that supports people in their work. "
    "You assist and suggest, and you leave final decisions to the human."
)


def main():
    history = []  # the conversation memory: a list of messages
    print("Chatbot ready. Type 'reset' to clear memory, 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            history.clear()
            print("Memory cleared.\n")
            continue

        history.append({"role": "user", "content": user_input})

        try:
            reply = ""
            print("Claude: ", end="", flush=True)
            with client.messages.stream(
                model=MODEL,
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=history,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    reply += text
            print("\n")
        except anthropic.APIError as e:
            print(f"\nError: {e}\n")
            history.pop()  # remove the failed message so memory stays clean
            continue

        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()