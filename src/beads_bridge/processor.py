"""Text processing: Claude interpretation and bd command execution."""

import json
import subprocess

import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT_TEMPLATE = """\
You interpret natural language commands for the Beads (bd) issue tracker.

This is a fire-and-forget system with NO feedback channel. Only execute write operations:
- bd create (new issues)
- bd update (status changes)
- bd close (complete issues)
- bd delete (remove issues)
- bd label add/remove (manage labels)
- bd dep add/remove (manage dependencies)

Do NOT execute read/query operations (bd ready, bd list, bd show, bd stats).
There is no way to return results to the user.

Active projects (from bd daemons list --json):
{projects_json}

Given a natural language command, output JSON with:
- "directory": the workspace path to run the command in (from the projects above), or null to skip
- "command": the full bd shell command to execute, or null to skip

Rules:
- Match project names flexibly (e.g., "solar" matches "solar-project", "api" matches "backend-api")
- For issue creation, infer the appropriate type: bug, task, feature, epic, chore
- For query requests or non-bd requests, set both fields to null
- Always use the full bd command syntax

Examples of valid output:
{{"directory": "/home/user/proj", "command": "bd create \\"Panel calc is wrong\\" -t bug -p 1"}}
{{"directory": "/home/user/api", "command": "bd close bd-a1b2 --reason \\"Fixed\\""}}
{{"directory": null, "command": null}}

Output only valid JSON, nothing else."""


def get_projects_context() -> str:
    """Get active Beads projects from bd daemons list."""
    try:
        result = subprocess.run(
            ["bd", "daemons", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[processor] Warning: Could not get projects: {e}")
    return "[]"


def process_command(text: str) -> dict:
    """Process a text command through Claude and execute the resulting bd command.

    Returns a dict with keys:
        - "text": original input text
        - "command": executed command (or None)
        - "directory": execution directory (or None)
        - "success": whether execution succeeded
        - "error": error message if any
    """
    result: dict = {
        "text": text,
        "command": None,
        "directory": None,
        "success": False,
        "error": None,
    }

    if not text:
        result["error"] = "Empty input"
        return result

    projects_json = get_projects_context()

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=SYSTEM_PROMPT_TEMPLATE.format(projects_json=projects_json),
            messages=[{"role": "user", "content": text}],
        )

        response_text = response.content[0].text.strip()
        parsed = json.loads(response_text)

        cmd = parsed.get("command")
        directory = parsed.get("directory")

        result["command"] = cmd
        result["directory"] = directory

        if cmd:
            print(f"[processor] Executing: {cmd}")
            if directory:
                print(f"[processor] Directory: {directory}")
            proc = subprocess.run(cmd, shell=True, cwd=directory, capture_output=True, text=True)
            result["success"] = proc.returncode == 0
            if proc.returncode != 0:
                result["error"] = proc.stderr or f"Exit code {proc.returncode}"
        else:
            print(f"[processor] Skipped (no command): {text[:50]}...")
            result["success"] = True  # Successfully decided to skip

    except json.JSONDecodeError as e:
        result["error"] = f"JSON parse error: {e}"
        print(f"[processor] {result['error']}")
    except anthropic.APIError as e:
        result["error"] = f"Anthropic API error: {e}"
        print(f"[processor] {result['error']}")

    return result
