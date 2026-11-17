# Day 02: Test Case Generator with Human Review

Turns a user story into structured test cases with Claude, then lets a human approve, reject, or edit each one. Review results are logged as metrics.

## What it does
- Reads a user story from `user_story.txt`
- Asks Claude for test cases as JSON and validates the response
- Human review loop: approve, reject, or edit each case
- Saves approved cases (JSON and Markdown) and logs metrics (acceptance rate, review time)
- `--demo` mode runs with sample data, so no API key is needed

## Tech used
Python, Anthropic SDK, python-dotenv

## How to run
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python generator.py --demo      # no API key needed
    python generator.py             # live mode, needs ANTHROPIC_API_KEY in .env

## What I learned
- Asking an AI for JSON, then validating it before trusting it
- Defensive parsing, for example stripping code fences and checking required fields
- A human-in-the-loop design where AI drafts and a person decides
- Logging metrics so human and AI collaboration can be measured