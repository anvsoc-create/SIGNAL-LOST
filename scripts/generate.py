import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from github import Github


LORE_PATH = Path("lore.json")
README_PATH = Path("README.md")


def load_lore() -> Dict[str, Any]:
    if not LORE_PATH.exists():
        return {
            "day": 1,
            "story_summary": "",
            "last_challenge": "",
            "last_challenge_type": "",
            "last_challenge_solved": False,
            "total_solvers": 0,
            "solver_hall_of_fame": [],
        }
    return json.loads(LORE_PATH.read_text(encoding="utf-8"))


def save_lore(lore: Dict[str, Any]) -> None:
    LORE_PATH.write_text(json.dumps(lore, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_github_client() -> Github:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN environment variable is required.")
    return Github(token)


def get_repo(g: Github):
    repo_name = os.environ.get("GITHUB_REPO")
    if not repo_name:
        raise RuntimeError("GITHUB_REPO environment variable is required (e.g. username/repo-name).")
    return g.get_repo(repo_name)


def get_recent_activity() -> Tuple[List[str], List[str]]:
    """
    Returns (solver_usernames, lore_suggester_usernames) from the last 24 hours.
    - Solvers: authors of merged PRs that touch the solutions/ directory.
    - Lore suggesters: authors of closed issues labeled 'lore' or with 'lore' in the title.
    """
    g = get_github_client()
    repo = get_repo(g)

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=1)

    solvers = set()
    lore_suggesters = set()

    # Find merged PRs in last 24h
    for pr in repo.get_pulls(state="closed", sort="updated", direction="desc"):
        if not pr.merged:
            continue
        if pr.merged_at is None or pr.merged_at < since:
            # PRs are returned sorted by updated desc; we can break once older than since
            if pr.merged_at and pr.merged_at < since:
                break
            continue
        try:
            files = list(pr.get_files())
        except Exception:
            files = []
        touches_solutions = any(f.filename.startswith("solutions/") for f in files)
        if touches_solutions and pr.user:
            solvers.add(pr.user.login)

    # Find closed issues in last 24h that suggest lore
    for issue in repo.get_issues(state="closed", sort="updated", direction="desc"):
        if issue.pull_request is not None:
            continue
        if issue.closed_at is None or issue.closed_at < since:
            if issue.closed_at and issue.closed_at < since:
                break
            continue
        labels = {lbl.name.lower() for lbl in issue.labels}
        title = (issue.title or "").lower()
        if "lore" in labels or "lore" in title:
            if issue.user:
                lore_suggesters.add(issue.user.login)

    return sorted(solvers), sorted(lore_suggesters)


def build_system_prompt() -> str:
    return (
        "You are the cryptic narrator of an evolving sci-fi alternate reality game (ARG) "
        "that lives entirely inside a GitHub repository's README.\n\n"
        "Every day, you advance the story, present a new puzzle, and credit the community "
        "members who solved yesterday's challenge or suggested lore.\n\n"
        "Strict output format (VERY IMPORTANT):\n"
        "1) First, output ONLY a complete README in Markdown.\n"
        "2) Then, on a new line, output a fenced JSON block of the form:\n"
        "```json\n"
        "{\n"
        '  \"day\": <integer>,\n'
        '  \"story_summary\": \"<short recap of the story so far>\",\n'
        '  \"last_challenge\": \"<one-paragraph description of today\\'s puzzle>\",\n'
        '  \"last_challenge_type\": \"coding|cipher|riddle|logic\",\n'
        '  \"last_challenge_solved\": <true|false>,\n'
        '  \"new_solvers\": [\"github-username-1\", \"github-username-2\"],\n'
        '  \"hall_of_fame_additions\": [\"github-username-1\", \"github-username-2\"]\n'
        "}\n"
        "```\n\n"
        "Do not include any other commentary outside the README and the JSON block."
    )


def build_user_prompt(
    lore: Dict[str, Any],
    solvers: List[str],
    lore_suggesters: List[str],
) -> str:
    day = lore.get("day", 1)
    story_summary = lore.get("story_summary", "") or ""
    last_challenge = lore.get("last_challenge", "") or ""
    last_type = lore.get("last_challenge_type", "") or ""
    last_solved = bool(lore.get("last_challenge_solved", False))
    total_solvers = lore.get("total_solvers", 0)
    hall_of_fame = lore.get("solver_hall_of_fame", []) or []

    parts = [
        f"Today is Day {day} of the ARG.",
        "",
        "Existing story summary:",
        story_summary or "(no story yet — this is the first transmission).",
        "",
        "Yesterday's challenge:",
        last_challenge or "(none, this is the first challenge).",
        f"Yesterday's challenge type: {last_type or 'n/a'}",
        f"Was yesterday's challenge solved? {'yes' if last_solved else 'no'}",
        "",
        f"Total unique solvers so far: {total_solvers}",
        f"Current Hall of Fame usernames: {', '.join(hall_of_fame) if hall_of_fame else '(empty)'}",
        "",
        "New activity from the last 24 hours:",
        f"- Potential solvers (merged PRs touching solutions/): {', '.join(solvers) if solvers else '(none)'}",
        f"- Lore suggesters (closed lore issues): {', '.join(lore_suggesters) if lore_suggesters else '(none)'}",
        "",
        "Narrative and tone rules:",
        "- The setting is a slowly awakening, possibly hostile, network of orbital signal relays.",
        "- The README is written as a cryptic transmission being received by visitors to the repo.",
        "- If yesterday's puzzle was UNSOLVED, slightly darken the tone and raise the stakes.",
        "- If it was solved, reward the community with subtle progress and recognition.",
        "",
        "Puzzle rules:",
        "- Generate EXACTLY one new puzzle for today.",
        "- Rotate the puzzle type daily between: coding challenge, cipher, riddle, and logic puzzle.",
        "- The puzzle must be solvable by reading the README alone.",
        "- Make the puzzle clearly labeled (e.g. '### Day X Puzzle — <type>').",
        "",
        "Community rules (must be clearly spelled out in the README):",
        "- Players submit solutions by opening a Pull Request that adds a file under solutions/ based on solutions/TEMPLATE.md.",
        "- Players can suggest new lore twists by opening Issues.",
        "- Tomorrow's README must credit today's solvers and notable lore suggestions by GitHub username.",
        "",
        "In the README you generate now, you MUST:",
        f"- Show a visible counter like 'Day {day} of ∞'.",
        "- Include a 'How to Play' section with clear instructions.",
        "- Include or update a 'Hall of Fame' section listing credited solvers by username.",
        "- Credit today's new solvers and lore suggesters by username somewhere prominent.",
        "",
        "Remember: At the very end of your response, provide the JSON lore_state block exactly as specified in the system message.",
    ]

    return "\n".join(parts)


def call_groq(system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 2500,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def call_gemini(system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    # Gemini doesn't have explicit system role; we embed system instructions into the first part.
    contents = [
        {
            "role": "user",
            "parts": [
                {"text": system_prompt + "\n\n---\n\n" + user_prompt},
            ],
        }
    ]
    payload = {"contents": contents}
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts)
    return text


def call_model(system_prompt: str, user_prompt: str) -> str:
    last_error: Optional[Exception] = None

    try:
        return call_groq(system_prompt, user_prompt)
    except Exception as e:
        last_error = e

    try:
        return call_gemini(system_prompt, user_prompt)
    except Exception as e:
        last_error = e

    raise RuntimeError(f"Both Groq and Gemini calls failed: {last_error}")


def parse_model_output(raw: str) -> Tuple[str, Dict[str, Any]]:
    """
    Splits the model output into (readme_markdown, lore_state_dict).
    Expects a ```json ... ``` fenced block containing the lore JSON.
    """
    start = raw.find("```json")
    if start == -1:
        raise ValueError("Model output missing ```json block.")
    end = raw.find("```", start + 7)
    if end == -1:
        raise ValueError("Model output has unterminated ```json block.")

    readme = raw[:start].strip()
    json_str = raw[start + len("```json"): end].strip()

    lore_state = json.loads(json_str)
    return readme, lore_state


def merge_lore(old: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    # Base fields
    new_day = int(update.get("day", old.get("day", 1)))
    story_summary = update.get("story_summary", old.get("story_summary", ""))
    last_challenge = update.get("last_challenge", old.get("last_challenge", ""))
    last_type = update.get("last_challenge_type", old.get("last_challenge_type", ""))
    last_solved = bool(update.get("last_challenge_solved", old.get("last_challenge_solved", False)))

    old_hof = set(old.get("solver_hall_of_fame", []) or [])
    total_solvers = int(old.get("total_solvers", 0))

    new_solvers = list(update.get("new_solvers", []))
    hof_additions = list(update.get("hall_of_fame_additions", []))

    # Update counts and hall of fame
    for username in new_solvers:
        if username not in old_hof:
            total_solvers += 1
    updated_hof = sorted(old_hof.union(hof_additions))

    return {
        "day": new_day,
        "story_summary": story_summary,
        "last_challenge": last_challenge,
        "last_challenge_type": last_type,
        "last_challenge_solved": last_solved,
        "total_solvers": total_solvers,
        "solver_hall_of_fame": updated_hof,
    }


def main() -> None:
    lore = load_lore()
    solvers, lore_suggesters = get_recent_activity()

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(lore, solvers, lore_suggesters)

    raw = call_model(system_prompt, user_prompt)
    readme, lore_state = parse_model_output(raw)

    # Write README
    README_PATH.write_text(readme.strip() + "\n", encoding="utf-8")

    # Merge and save lore
    merged = merge_lore(lore, lore_state)
    # Increment day for next run if model didn't already
    if merged.get("day", 1) <= lore.get("day", 1):
        merged["day"] = int(lore.get("day", 1)) + 1
    save_lore(merged)


if __name__ == "__main__":
    main()

