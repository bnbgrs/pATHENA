from athena.desktop import pathena_ui_refinement_800 as refinement


def test_eighth_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._SURFACE_RULES) == 20
    assert len(refinement._REFINEMENTS) == 5
    assert len(refinement.UI_REFINEMENT_TASKS_701_800) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_701_800)) == 100


def test_eighth_refinement_targets_system_and_backup_operations() -> None:
    keys = {key for key, _label, _role in refinement._SURFACE_RULES}

    assert "systemWorkspace" in keys
    assert "systemOperationsTabs" in keys
    assert "systemDetail" in keys
    assert "backupWorkspace" in keys
    assert "backupSnapshotList" in keys
    assert "backupRestoreButton" in keys


def test_backup_restore_is_visually_distinct_from_normal_verification() -> None:
    roles = {key: role for key, _label, role in refinement._SURFACE_RULES}

    assert roles["backupRestoreButton"] == "destructive"
    assert roles["backupVerifyButton"] == "secondary"
    assert roles["backupDeepVerifyButton"] == "secondary"
    assert roles["backupCreateButton"] == "primary"


def test_ops_styles_remain_quiet_and_non_glowing() -> None:
    stylesheet = refinement._OPS_STYLESHEET.lower()

    assert "#f26a21" in stylesheet
    assert 'pathenaopsrole="destructive"' in stylesheet
    assert "glow" not in stylesheet
    assert "shadow" not in stylesheet
