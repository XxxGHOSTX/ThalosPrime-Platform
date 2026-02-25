"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
from dataclasses import dataclass


@dataclass
class AgenticAuditResult:
    url: str
    has_llms_txt: bool = False
    has_structured_data: bool = False
    has_robots_txt: bool = False
    has_sitemap: bool = False
    agentic_score: int = 0
    recommendations: list[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class AgenticAuditor:
    """
    Evaluates website machine-readability for the Agentic Web (SEO for AI).
    Checks for llms.txt, structured data, robots.txt, and sitemap presence.
    """

    def audit(self, url: str, html_content: str, headers: dict | None = None) -> AgenticAuditResult:
        result = AgenticAuditResult(url=url)
        headers = headers or {}

        if "llms.txt" in html_content or "llms-full.txt" in html_content:
            result.has_llms_txt = True
            result.agentic_score += 30
        else:
            result.recommendations.append("Add /llms.txt to describe your AI-readable content policy.")

        if "application/ld+json" in html_content or 'itemtype="http://schema.org' in html_content:
            result.has_structured_data = True
            result.agentic_score += 25
        else:
            result.recommendations.append("Add JSON-LD structured data (Schema.org) to all pages.")

        if "robots.txt" in html_content:
            result.has_robots_txt = True
            result.agentic_score += 20
        else:
            result.recommendations.append("Ensure /robots.txt is present and AI-agent friendly.")

        if "sitemap" in html_content.lower():
            result.has_sitemap = True
            result.agentic_score += 25
        else:
            result.recommendations.append("Add XML sitemap for AI crawler indexing.")

        return result
