"""Entry point: run the dependency-review crew for one skill ID.

Usage:
    python -m skill_audit_review.main [skill_id]   # default 66

Running the crew itself needs an LLM API key (e.g. OPENAI_API_KEY), as with
any CrewAI example. The audit lookup tool it uses is read-only and needs no
key; you can exercise it alone via tools/skill_audit_tool.py.
"""

from __future__ import annotations

import sys

from .crew import build_crew


def run() -> None:
    skill_id = int(sys.argv[1]) if len(sys.argv) > 1 else 66
    result = build_crew().kickoff(inputs={"skill_id": skill_id})
    print(result)


if __name__ == "__main__":
    run()
