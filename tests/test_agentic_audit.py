"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.discovery_sentinel.agentic_audit import AgenticAuditor, AgenticAuditResult


def test_detects_llms_txt():
    auditor = AgenticAuditor()
    html = '<a href="/llms.txt">LLMs</a>'
    result = auditor.audit("https://example.com", html)
    assert result.has_llms_txt is True
    assert result.agentic_score >= 30


def test_detects_structured_data():
    auditor = AgenticAuditor()
    html = '<script type="application/ld+json">{"@type": "WebPage"}</script>'
    result = auditor.audit("https://example.com", html)
    assert result.has_structured_data is True
    assert result.agentic_score >= 25


def test_detects_robots_txt():
    auditor = AgenticAuditor()
    html = '<a href="/robots.txt">Robots</a>'
    result = auditor.audit("https://example.com", html)
    assert result.has_robots_txt is True
    assert result.agentic_score >= 20


def test_detects_sitemap():
    auditor = AgenticAuditor()
    html = '<a href="/sitemap.xml">Sitemap</a>'
    result = auditor.audit("https://example.com", html)
    assert result.has_sitemap is True
    assert result.agentic_score >= 25


def test_perfect_score():
    auditor = AgenticAuditor()
    html = (
        '<a href="/llms.txt">LLMs</a>'
        '<script type="application/ld+json">{}</script>'
        '<a href="/robots.txt">robots</a>'
        '<a href="/sitemap.xml">sitemap</a>'
    )
    result = auditor.audit("https://perfect.com", html)
    assert result.agentic_score == 100
    assert result.recommendations == []


def test_empty_page_has_recommendations():
    auditor = AgenticAuditor()
    result = auditor.audit("https://empty.com", "<html></html>")
    assert result.agentic_score == 0
    assert len(result.recommendations) == 4


def test_result_url_preserved():
    auditor = AgenticAuditor()
    result = auditor.audit("https://mysite.com", "")
    assert result.url == "https://mysite.com"
