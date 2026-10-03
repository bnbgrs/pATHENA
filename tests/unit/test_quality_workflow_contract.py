from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_QUALITY_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "quality.yml"


def _quality_workflow_text() -> str:
    return _QUALITY_WORKFLOW.read_text(encoding="utf-8")


def test_canonical_quality_cancels_superseded_candidates_but_not_main() -> None:
    workflow = _quality_workflow_text()

    assert "      - develop/pathena-next\n" in workflow
    assert (
        "  group: ${{ github.workflow }}-${{ github.event_name }}-"
        "${{ github.event.pull_request.number || github.ref }}\n"
    ) in workflow
    assert (
        "  cancel-in-progress: ${{ github.event_name == 'pull_request' || "
        "github.ref == 'refs/heads/develop/pathena-next' }}\n"
        in workflow
    )
    assert '  CANDIDATE_SHA: ${{ github.event.pull_request.head.sha || github.sha }}\n' in workflow

def test_canonical_local_install_smoke_keeps_pypdf_packaging_guard() -> None:
    workflow = _quality_workflow_text()

    assert "    name: Local install smoke\n" in workflow
    assert "      - name: Verify pypdf packaging metadata\n" in workflow
    assert "        run: uv run --locked --extra dev athena-packaging-smoke --json\n" in workflow


def test_canonical_windows_path_safety_keeps_exact_sha_and_storage_regressions() -> None:
    workflow = _quality_workflow_text()

    assert "  windows-path-safety:\n" in workflow
    assert "    runs-on: windows-latest\n" in workflow
    assert "          ref: ${{ env.CANDIDATE_SHA }}\n" in workflow
    assert "      - name: Run deterministic Windows locality regressions\n" in workflow
    assert "      - name: Run Windows storage path regressions\n" in workflow
    assert "tests/unit/test_storage_safe_mode.py" in workflow


def test_canonical_quality_keeps_full_pytest_and_enforces_all_core_checks() -> None:
    workflow = _quality_workflow_text()
    normalized = " ".join(workflow.replace("\\\n", " ").split())

    assert "  quality-static:\n" in workflow
    assert "    name: Python 3.12 static quality\n" in workflow
    assert "    timeout-minutes: 15\n" in workflow
    assert (
        "uv run --locked --extra dev --extra desktop python scripts/validate_spec.py"
        in normalized
    )
    assert (
        "uv run --locked --extra dev --extra desktop python -m ruff check "
        "src tests scripts" in normalized
    )
    assert (
        "uv run --locked --extra dev --extra desktop python -m mypy src/athena"
        in normalized
    )

    assert "  pytest-native-qt:\n" in workflow
    assert "    name: Pytest native Qt isolation\n" in workflow
    assert (
        "uv run --locked --extra dev --extra desktop python -m pytest "
        "tests/unit/test_desktop_api_controller.py" in normalized
    )
    assert (
        "uv run --locked --extra dev --extra desktop python -m pytest "
        "tests/unit/test_desktop_chat_selection_state.py" in normalized
    )
    assert (
        "uv run --locked --extra dev --extra desktop python -m pytest "
        "tests/unit/test_desktop_direct_chat.py" in normalized
    )

    assert "  pytest-shard:\n" in workflow
    assert "    name: Pytest shard ${{ matrix.shard }}/6\n" in workflow
    assert "        shard: [1, 2, 3, 4, 5, 6]\n" in workflow
    assert "    timeout-minutes: 25\n" in workflow
    assert 'Path("tests").rglob("test_*.py")' in workflow
    assert 'Path("tests/unit/test_desktop_api_controller.py")' in workflow
    assert 'Path("tests/unit/test_desktop_chat_selection_state.py")' in workflow
    assert 'Path("tests/unit/test_desktop_direct_chat.py")' in workflow
    assert 'python -m pytest "${TEST_FILES[@]}"' in workflow

    assert "  quality:\n" in workflow
    assert "    name: Python 3.12 quality\n" in workflow
    assert "      - quality-static\n" in workflow
    assert "      - pytest-native-qt\n" in workflow
    assert "      - pytest-shard\n" in workflow
    assert 'STATIC_RESULT: ${{ needs.quality-static.result }}' in workflow
    assert 'NATIVE_QT_RESULT: ${{ needs.pytest-native-qt.result }}' in workflow
    assert 'PYTEST_SHARDS_RESULT: ${{ needs.pytest-shard.result }}' in workflow
    assert 'failures = [name for name, outcome in outcomes.items() if outcome != "success"]' in workflow
    assert "ATHENA QUALITY GATE: PASS — full canonical suite completed in parallel" in workflow

def test_canonical_quality_keeps_storage_bootstrap_and_runtime_boundary_regressions() -> None:
    workflow = _quality_workflow_text()

    assert "  storage-regressions:\n" in workflow
    assert "tests/unit/test_storage_bootstrap.py" in workflow
    assert workflow.count("      - name: Run API runtime path-boundary regressions\n") == 2
    assert workflow.count("tests/unit/test_api_runtime_boundaries.py") == 2
