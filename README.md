# Day 01: CLI Chatbot with Memory

A terminal chatbot using the Anthropic API that remembers the conversation.

## What it does
- Streams replies as they are generated
- Keeps conversation history so follow-up questions work
- Handles API errors without crashing

## Tech used
Python, Anthropic SDK, python-dotenv

## How to run
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    # create a .env file with:
    # ANTHROPIC_API_KEY=your-key
    # MODEL=claude-haiku-5-5
    python chat.py

## What I learned
The API is stateless: memory means resending the full message history each turn.

## Note
Requires API credits in the Anthropic Console.