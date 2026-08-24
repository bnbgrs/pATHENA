from athena.desktop import pathena_ui_refinement_300 as refinement


def test_third_refinement_pass_defines_exactly_one_hundred_tasks() -> None:
    assert len(refinement._BACKUP_OBJECT_NAMES) == 6
    assert len(refinement._TARGETS) == 47
    assert len(refinement.UI_REFINEMENT_TASKS_201_300) == 100
    assert len(set(refinement.UI_REFINEMENT_TASKS_201_300)) == 100


def test_third_refinement_pass_has_unique_targets_and_complete_help() -> None:
    keys = [key for key, _, _ in refinement._TARGETS]
    backup_names = [name for _, name in refinement._BACKUP_OBJECT_NAMES]

    assert len(set(keys)) == 47
    assert len(set(backup_names)) == 6
    assert all(key and label and help_text for key, label, help_text in refinement._TARGETS)
    assert all(help_text.endswith(".") for _, _, help_text in refinement._TARGETS)


def test_backup_identity_repairs_match_existing_accessibility_contract() -> None:
    assert dict(refinement._BACKUP_OBJECT_NAMES) == {
        "CREATE BACKUP…": "backupCreateButton",
        "VERIFY": "backupVerifyButton",
        "DEEP VERIFY": "backupDeepVerifyButton",
        "RESTORE ISOLATED…": "backupRestoreButton",
        "TARGETS": "backupTargetsButton",
        "REGISTER TARGET…": "backupAddTargetButton",
    }
