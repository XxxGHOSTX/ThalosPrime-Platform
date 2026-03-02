"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.discovery_sentinel.risk_analyzer import RiskAnalyzer, RISK_WEIGHTS


def test_empty_findings_is_low():
    analyzer = RiskAnalyzer()
    report = analyzer.analyze([])
    assert report.risk_level == "LOW"
    assert report.total_score == 0


def test_single_shadow_ai_is_critical():
    analyzer = RiskAnalyzer()
    findings = [{"alert": "SHADOW_AI_DETECTED"}]
    report = analyzer.analyze(findings)
    assert report.risk_level == "CRITICAL"
    assert report.total_score == RISK_WEIGHTS["SHADOW_AI_DETECTED"]


def test_medium_risk_score():
    analyzer = RiskAnalyzer()
    # MISSING_DETERMINISTIC_HEADER = 30 → score 30 → MEDIUM (20 ≤ score < 50)
    findings = [{"alert": "MISSING_DETERMINISTIC_HEADER"}]
    report = analyzer.analyze(findings)
    assert report.risk_level == "MEDIUM"
    assert report.total_score == RISK_WEIGHTS["MISSING_DETERMINISTIC_HEADER"]


def test_high_risk_score():
    analyzer = RiskAnalyzer()
    findings = [{"alert": "UNSANCTIONED_FRAMEWORK"}]
    report = analyzer.analyze(findings)
    assert report.risk_level == "HIGH"


def test_findings_get_weight_appended():
    analyzer = RiskAnalyzer()
    findings = [{"alert": "SHADOW_AI_DETECTED", "endpoint": "api.openai.com"}]
    report = analyzer.analyze(findings)
    assert report.findings[0]["weight"] == RISK_WEIGHTS["SHADOW_AI_DETECTED"]
    assert report.findings[0]["endpoint"] == "api.openai.com"


def test_unknown_alert_uses_default_weight():
    analyzer = RiskAnalyzer()
    findings = [{"alert": "SOMETHING_NEW"}]
    report = analyzer.analyze(findings)
    assert report.findings[0]["weight"] == 10
