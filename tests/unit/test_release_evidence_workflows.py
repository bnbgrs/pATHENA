from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WINDOWS_PACKAGE = _REPO_ROOT / ".github" / "workflows" / "windows-package.yml"
_PROMOTION = _REPO_ROOT / ".github" / "workflows" / "promotion-readiness.yml"


def test_package_manifest_does_not_claim_full_release_readiness() -> None:
    workflow = _WINDOWS_PACKAGE.read_text(encoding="utf-8")

    assert (
        'release_status = "package_smoke_passed_exact_release_readiness_not_claimed"'
        in workflow
    )
    assert "candidate_pending_full_v0.1_gates" not in workflow


def test_promotion_workflow_emits_exact_sha_release_ready_certification() -> None:
    workflow = _PROMOTION.read_text(encoding="utf-8")

    assert "from athena.version import __version__" in workflow
    assert 'promotion_guard_green = os.environ["PROMOTION_GUARD"] == "success"' in workflow
    assert '"release_status": "release_ready"' in workflow
    assert '"canonical_quality_run_id": quality_run["id"]' in workflow
    assert '"windows_package_run_id": package_run["id"]' in workflow
    assert '"promotion_workflow_run_id": int(os.environ["GITHUB_RUN_ID"])' in workflow
    assert '.release-evidence/release-certification.json' in workflow
    assert 'name: pATHENA-release-certification-${{ env.CANDIDATE_SHA }}' in workflow
    assert "if-no-files-found: error" in workflow
