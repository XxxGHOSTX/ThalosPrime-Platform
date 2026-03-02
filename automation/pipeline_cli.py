"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
import json
import hashlib
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utilities import compute_sha256, append_jsonl, now_iso, validate_seed  # noqa: E402
from services.ingest.file_ingest import FileIngestor  # noqa: E402
from services.ingest.normalizer import EventNormalizer  # noqa: E402
from services.discovery_sentinel.scanner import SentinelScanner  # noqa: E402
from services.discovery_sentinel.risk_analyzer import RiskAnalyzer  # noqa: E402
from services.artifact_engine.repair_logic import ArtifactRepairEngine  # noqa: E402
from services.control_plane.session_manager import ThalosSessionManager  # noqa: E402


_PLATFORM_VERSION = "2.0.0"


def _sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file's contents."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_pipeline(
    seed: int,
    input_paths: list[str],
    output_dir: str,
    statelog_path: str = "STATELOG/events.jsonl",
) -> dict:
    """
    Execute the full deterministic pipeline end-to-end.

    Stages:
        1. Ingest – read files / entries, produce normalised events.
        2. Scan   – run sentinel scanner over raw event text.
        3. Risk   – analyse findings into a weighted risk report.
        4. Session – create control-plane session and record turns.
        5. STATELOG – append audit event.
        6. Remediation – generate artifact patches for every finding.
        7. Manifest – write artifact manifest with hashes.

    Returns the manifest dict.
    """
    seed = validate_seed(seed)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # ── Stage 1: Ingest ────────────────────────────────────────────────
    ingestor = FileIngestor()
    normalizer = EventNormalizer()
    all_events = []
    for ip in input_paths:
        events = ingestor.ingest_file(ip)
        all_events.extend(events)

    # Normalize events (used for metadata/audit; raw text fed to scanner)
    for e in all_events:
        normalizer.normalize(e)
    raw_lines = [e.raw for e in all_events]
    input_hash = compute_sha256({"seed": seed, "lines": raw_lines})

    # ── Stage 2: Scan ──────────────────────────────────────────────────
    scanner = SentinelScanner()
    findings = scanner.audit_bulk(raw_lines)

    # ── Stage 3: Risk analysis ─────────────────────────────────────────
    analyzer = RiskAnalyzer()
    report = analyzer.analyze(findings)

    # ── Stage 4: Control-plane session ────────────────────────────────
    session_mgr = ThalosSessionManager()
    session_id = session_mgr.create_session(context={"seed": seed, "input_hash": input_hash, "pipeline": "cli"})
    session_mgr.add_turn(session_id, "system", f"pipeline_start seed={seed}")
    session_mgr.add_turn(
        session_id,
        "system",
        f"scan_complete findings={len(findings)} risk={report.risk_level}",
    )

    # ── Stage 5: STATELOG ─────────────────────────────────────────────
    pipeline_event = {
        "pipeline": "cli",
        "seed": seed,
        "session_id": session_id,
        "input_hash": input_hash,
        "events_ingested": len(all_events),
        "findings_count": len(findings),
        "risk_level": report.risk_level,
        "risk_score": report.total_score,
        "state_hash": compute_sha256(
            {
                "seed": seed,
                "input_hash": input_hash,
                "findings": findings,
            }
        ),
        "timestamp": now_iso(),
    }
    append_jsonl(statelog_path, pipeline_event)

    # ── Stage 6: Remediation ──────────────────────────────────────────
    engine = ArtifactRepairEngine(seed=seed)
    artifact_files: list[dict] = []

    for idx, finding in enumerate(findings):
        endpoint = finding.get("endpoint", "unknown")
        rule = engine.generate_firewall_rule(endpoint)
        rule_file = out_path / f"firewall_rule_{idx:04d}_{rule['rule_id']}.txt"
        rule_file.write_text(rule["content"])

        patch = engine.generate_patch(finding)
        patch_file = out_path / f"patch_{idx:04d}.txt"
        patch_file.write_text(patch)

        artifact_files.append(
            {
                "index": idx,
                "rule_id": rule["rule_id"],
                "rule_file": rule_file.name,
                "rule_sha256": _sha256_file(rule_file),
                "patch_file": patch_file.name,
                "patch_sha256": _sha256_file(patch_file),
                "finding": finding,
            }
        )

    # ── Stage 7: Manifest ─────────────────────────────────────────────
    manifest = {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "seed": seed,
        "input_hash": input_hash,
        "platform_version": _PLATFORM_VERSION,
        "session_id": session_id,
        "risk_level": report.risk_level,
        "risk_score": report.total_score,
        "events_ingested": len(all_events),
        "findings_count": len(findings),
        "artifacts": artifact_files,
        "pipeline_state_hash": pipeline_event["state_hash"],
    }

    manifest_path = out_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    manifest["manifest_sha256"] = _sha256_file(manifest_path)
    # Rewrite with hash included
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Thalos Prime — Full Deterministic Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m automation.pipeline_cli --seed 9876543210123456 \\\n"
            "      --input logs/network.log --output output/run-001\n"
            "\n"
            "  python -m automation.pipeline_cli --seed 9876543210123456 \\\n"
            "      --input events.jsonl --output output/run-001\n"
        ),
    )
    parser.add_argument("--seed", type=int, required=True, help="64-bit execution seed (required)")
    parser.add_argument(
        "--input",
        dest="inputs",
        action="append",
        default=[],
        metavar="PATH",
        help="Input file to ingest (JSONL or proxy log). Repeat for multiple files.",
    )
    parser.add_argument("--output", type=str, default="output", help="Output directory for artifacts")
    parser.add_argument(
        "--statelog",
        type=str,
        default="STATELOG/events.jsonl",
        help="Path to STATELOG JSONL file",
    )
    args = parser.parse_args()

    try:
        validate_seed(args.seed)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    manifest = run_pipeline(
        seed=args.seed,
        input_paths=args.inputs,
        output_dir=args.output,
        statelog_path=args.statelog,
    )

    print("Pipeline complete.")
    print(f"  Seed:          {manifest['seed']}")
    print(f"  Input hash:    {manifest['input_hash']}")
    print(f"  Risk level:    {manifest['risk_level']}")
    print(f"  Findings:      {manifest['findings_count']}")
    print(f"  Artifacts:     {len(manifest['artifacts'])}")
    print(f"  Manifest:      {args.output}/manifest.json")
    print(f"  State hash:    {manifest['pipeline_state_hash']}")


if __name__ == "__main__":
    main()
