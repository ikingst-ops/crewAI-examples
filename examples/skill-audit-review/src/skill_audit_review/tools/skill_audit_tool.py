"""Read-only CrewAI tool for 1VR's public skill-audit API.

Calls `GET https://1vr.com/api/v1/skills/{id}/audit` and returns the factual
findings from static analysis of an agent skill or MCP server: tier, declared
permissions, network / credential / suspicious signals, install notes, and
provenance. No API key is needed for reads; the tool performs no writes.

Docs: https://1vr.com/skills.md
"""

from __future__ import annotations

import requests
from crewai.tools import BaseTool

API_BASE = "https://1vr.com/api/v1"
REPORT_BASE = "https://1vr.com/skills"


def _signal_lines(title: str, signals: list[dict]) -> list[str]:
    if not signals:
        return [f"{title}: none recorded"]
    lines = [f"{title} ({len(signals)}):"]
    for s in signals:
        lines.append(f"  - {s.get('signal', '?')}: {s.get('detail', '')}")
    return lines


def format_audit_report(report: dict) -> str:
    findings = report.get("findings") or {}
    provenance = findings.get("provenance") or {}
    skill_id = report.get("skill_id")
    lines = [
        f"Skill audit report for skill #{skill_id}",
        f"Tier: {report.get('tier')}",
        f"Checked at: {report.get('checked_at')}",
        f"Source: {provenance.get('source')} "
        f"(author: {provenance.get('author')}, version: {provenance.get('version')})",
        f"Declared permissions: {findings.get('permissions') or 'none declared'}",
    ]
    lines += _signal_lines("Network signals", findings.get("network") or [])
    lines += _signal_lines("Credential references", findings.get("credentials") or [])
    lines += _signal_lines("Suspicious signals", findings.get("suspicious") or [])
    lines += _signal_lines("Install / dependency notes", findings.get("dependencies") or [])
    lines.append(f"Full report: {REPORT_BASE}/{skill_id}")
    lines.append(f"Raw API: {API_BASE}/skills/{skill_id}/audit")
    if report.get("disclaimer"):
        lines.append(f"Note: {report['disclaimer']}")
    return "\n".join(lines)


class SkillAuditTool(BaseTool):
    name: str = "1VR skill audit lookup"
    description: str = (
        "Look up the public static-analysis audit report for a 1VR skill by "
        "its numeric ID. Returns factual findings only (tier, declared "
        "permissions, network and credential signals, suspicious patterns, "
        "provenance). Input: the skill ID as an integer."
    )

    def _run(self, skill_id: int) -> str:
        resp = requests.get(f"{API_BASE}/skills/{skill_id}/audit", timeout=30)
        resp.raise_for_status()
        return format_audit_report(resp.json())
