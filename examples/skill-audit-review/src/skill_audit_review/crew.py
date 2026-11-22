"""A one-agent crew that reviews a skill dependency before adoption.

The reviewer agent uses the read-only 1VR skill-audit tool to fetch the
static-analysis report for a skill ID, then writes a handoff that quotes the
report's findings verbatim and cites the skill ID and report URL, so a human
or another agent can verify every claim against the source report.
"""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from .tools.skill_audit_tool import SkillAuditTool


def build_crew() -> Crew:
    audit_tool = SkillAuditTool()

    reviewer = Agent(
        role="Skill Dependency Reviewer",
        goal=(
            "Review agent skills before adoption using recorded static-analysis "
            "findings, and hand off a summary that cites those findings exactly."
        ),
        backstory=(
            "You review third-party agent skills for a small team. You never "
            "guess about a skill's behaviour: you look up its 1VR audit report "
            "and quote the recorded signals, including the tier and any "
            "suspicious patterns, with the report link attached."
        ),
        tools=[audit_tool],
        verbose=True,
    )

    review_task = Task(
        description=(
            "Use the 1VR skill audit lookup tool to fetch the audit report for "
            "skill ID {skill_id}. Then write a dependency-review handoff that:\n"
            "1. States the skill ID, its tier, and when the report was checked.\n"
            "2. Quotes the findings verbatim: declared permissions, network "
            "signals, credential references, suspicious signals, and install / "
            "dependency notes.\n"
            "3. Cites the full report URL and the raw API URL.\n"
            "Do not add judgements that are not in the report; the report "
            "summarises static signals only and is not a security guarantee."
        ),
        expected_output=(
            "A short handoff note for skill {skill_id}: tier and check date, "
            "the report's findings quoted verbatim by category, and the report "
            "and API URLs for verification."
        ),
        agent=reviewer,
    )

    return Crew(agents=[reviewer], tasks=[review_task], process=Process.sequential)
