"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import shutil
import subprocess

import pytest


def _docker_available() -> bool:
    return shutil.which("docker") is not None


@pytest.mark.skipif(not _docker_available(), reason="Docker not available")
def test_docker_compose_config_valid():
    result = subprocess.run(
        ["docker", "compose", "-f", "infrastructure/docker/docker-compose.yml", "config", "--quiet"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"docker compose config failed: {result.stderr}"


@pytest.mark.skipif(not _docker_available(), reason="Docker not available")
def test_dockerfile_thalos_core_exists():
    from pathlib import Path

    assert Path("infrastructure/docker/Dockerfile.thalos-core").exists()


def test_docker_stack_files_exist():
    from pathlib import Path

    assert Path("infrastructure/docker/docker-compose.yml").exists()
    assert Path("infrastructure/prometheus/prometheus.yml").exists()
    assert Path("infrastructure/grafana/provisioning/datasources.yml").exists()
    assert Path("infrastructure/grafana/dashboards/thalos-prime.json").exists()
