"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.artifact_engine.template_factory import TemplateFactory, TEMPLATES
from services.artifact_engine.repair_logic import ArtifactRepairEngine


# ── TemplateFactory tests ──────────────────────────────────────────────────────

def test_list_templates():
    factory = TemplateFactory()
    templates = factory.list_templates()
    assert "firewall_rule" in templates
    assert "code_patch" in templates


def test_render_firewall_rule():
    factory = TemplateFactory()
    output = factory.render("firewall_rule", {
        "rule_id": "abc123",
        "blocked_endpoint": "api.openai.com",
        "seed": 99999,
    })
    assert "abc123" in output
    assert "api.openai.com" in output
    assert "Tony Ray Macier III" in output


def test_render_code_patch():
    factory = TemplateFactory()
    output = factory.render("code_patch", {
        "patch_hash": "deadbeef",
        "vulnerability": {"type": "shadow_ai"},
        "seed": 12345,
    })
    assert "deadbeef" in output
    assert "Tony Ray Macier III" in output


def test_render_unknown_template_raises():
    factory = TemplateFactory()
    with pytest.raises(ValueError, match="Unknown template"):
        factory.render("nonexistent_template", {})


# ── ArtifactRepairEngine tests ─────────────────────────────────────────────────

def test_generate_firewall_rule_returns_dict():
    engine = ArtifactRepairEngine(seed=9876543210123456)
    result = engine.generate_firewall_rule("api.openai.com")
    assert isinstance(result, dict)
    assert "rule_id" in result
    assert "content" in result
    assert "seed" in result
    assert result["seed"] == 9876543210123456


def test_generate_firewall_rule_is_deterministic():
    engine = ArtifactRepairEngine(seed=9876543210123456)
    r1 = engine.generate_firewall_rule("api.openai.com")
    r2 = engine.generate_firewall_rule("api.openai.com")
    assert r1["rule_id"] == r2["rule_id"]
    assert r1["content"] == r2["content"]


def test_different_endpoints_produce_different_rule_ids():
    engine = ArtifactRepairEngine(seed=9876543210123456)
    r1 = engine.generate_firewall_rule("api.openai.com")
    r2 = engine.generate_firewall_rule("api.anthropic.com")
    assert r1["rule_id"] != r2["rule_id"]


def test_generate_patch_returns_string():
    engine = ArtifactRepairEngine(seed=9876543210123456)
    patch = engine.generate_patch({"type": "unauthorized_egress", "endpoint": "api.openai.com"})
    assert isinstance(patch, str)
    assert "Tony Ray Macier III" in patch


def test_generate_patch_is_deterministic():
    engine = ArtifactRepairEngine(seed=9876543210123456)
    vuln = {"type": "unauthorized_egress"}
    p1 = engine.generate_patch(vuln)
    p2 = engine.generate_patch(vuln)
    assert p1 == p2
