import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("MODEL", "claude-haiku-5-5")
REQUIRED_KEYS = {"id", "title", "type", "priority", "preconditions", "steps", "expected_result"}
OUTPUT_DIR = Path("output")

SYSTEM_PROMPT = """You are a senior QA engineer. Given a user story, write test cases.
Return ONLY a JSON array, with no markdown fences and no commentary.
Each item must have these keys:
id (string like "TC-01"), title, type ("positive", "negative" or "edge"),
priority ("high", "medium" or "low"), preconditions (string),
steps (array of strings), expected_result (string).
Write 6 to 10 test cases covering positive, negative and edge scenarios."""

DEMO_CASES = [
    {
        "id": "TC-01", "title": "Login succeeds with valid credentials",
        "type": "positive", "priority": "high",
        "preconditions": "A registered, unlocked account exists.",
        "steps": ["Open the login page", "Enter a valid email", "Enter the correct password", "Click Log in"],
        "expected_result": "The user lands on their account page.",
    },
    {
        "id": "TC-02", "title": "Login rejected for a password shorter than 8 characters",
        "type": "negative", "priority": "medium",
        "preconditions": "A registered account exists.",
        "steps": ["Open the login page", "Enter a valid email", "Enter a 7-character password", "Click Log in"],
        "expected_result": "Login fails with a generic error message.",
    },
    {
        "id": "TC-03", "title": "Account locks after 5 failed attempts",
        "type": "edge", "priority": "high",
        "preconditions": "A registered account exists with no prior failed attempts.",
        "steps": ["Attempt login with a wrong password 5 times", "Attempt login with the correct password"],
        "expected_result": "The account is locked for 15 minutes and the correct password is rejected.",
    },
]


def call_model(story: str, demo: bool) -> str:
    """Return the raw model text. In demo mode, no API call is made."""
    if demo:
        return json.dumps(DEMO_CASES)
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": story}],
    )
    return message.content[0].text


def parse_cases(raw: str) -> list:
    """Turn the model's text into a validated list of test cases."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        cases = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Expected a non-empty JSON array of test cases.")
    for i, case in enumerate(cases, 1):
        missing = REQUIRED_KEYS - set(case)
        if missing:
            raise ValueError(f"Test case {i} is missing keys: {sorted(missing)}")
        if not isinstance(case["steps"], list):
            raise ValueError(f"Test case {i}: 'steps' must be a list.")
    return cases


def review(cases: list):
    """Human review loop: the person approves, rejects or edits each case."""
    approved = []
    stats = {"approved": 0, "rejected": 0, "edited": 0}
    start = time.time()
    for case in cases:
        print(f"\n{case['id']} [{case['type']} / {case['priority']}] {case['title']}")
        print(f"  Preconditions: {case['preconditions']}")
        for i, step in enumerate(case["steps"], 1):
            print(f"  {i}. {step}")
        print(f"  Expected: {case['expected_result']}")
        while True:
            choice = input("[a]pprove  [r]eject  [e]dit title > ").strip().lower()
            if choice == "a":
                approved.append(case)
                stats["approved"] += 1
                break
            if choice == "r":
                stats["rejected"] += 1
                break
            if choice == "e":
                new_title = input("New title: ").strip()
                if new_title:
                    case["title"] = new_title
                    stats["edited"] += 1
                approved.append(case)
                stats["approved"] += 1
                break
            print("Please type a, r or e.")
    stats["review_seconds"] = round(time.time() - start, 1)
    return approved, stats


def to_markdown(cases: list) -> str:
    lines = ["# Approved test cases", ""]
    for c in cases:
        lines += [
            f"## {c['id']}: {c['title']}",
            f"- **Type:** {c['type']} | **Priority:** {c['priority']}",
            f"- **Preconditions:** {c['preconditions']}",
            "- **Steps:**",
        ]
        lines += [f"  {i}. {s}" for i, s in enumerate(c["steps"], 1)]
        lines += [f"- **Expected:** {c['expected_result']}", ""]
    return "\n".join(lines)


def save_results(approved: list, stats: dict, generated: int, demo: bool):
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "test_cases.json").write_text(json.dumps(approved, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "test_cases.md").write_text(to_markdown(approved), encoding="utf-8")

    metrics_file = OUTPUT_DIR / "metrics.json"
    history = json.loads(metrics_file.read_text()) if metrics_file.exists() else []
    history.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "demo" if demo else "live",
        "generated": generated,
        **stats,
        "acceptance_rate": round(stats["approved"] / generated, 2) if generated else 0,
    })
    metrics_file.write_text(json.dumps(history, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate test cases from a user story.")
    parser.add_argument("story_file", nargs="?", default="user_story.txt")
    parser.add_argument("--demo", action="store_true", help="use sample data, no API call")
    args = parser.parse_args()

    try:
        story = Path(args.story_file).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        print(f"Could not find {args.story_file}")
        return

    print(f"Generating test cases ({'demo mode' if args.demo else MODEL})...")
    try:
        cases = parse_cases(call_model(story, args.demo))
    except anthropic.APIError as e:
        print(f"API error: {e}")
        return
    except ValueError as e:
        print(f"Could not use the model's answer: {e}")
        return

    print(f"Generated {len(cases)} test cases. Review each one.")
    approved, stats = review(cases)
    save_results(approved, stats, len(cases), args.demo)

    print(f"\nDone. Approved {stats['approved']}, rejected {stats['rejected']}, "
          f"edited {stats['edited']} in {stats['review_seconds']}s.")
    print("Saved to the output/ folder.")


if __name__ == "__main__":
    main()