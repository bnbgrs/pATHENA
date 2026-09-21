"""Apply the narrow Knowledge visual-fixture determinism fix.

This migration helper is intentionally source-exact: it refuses to mutate the
capture script unless the known nondeterministic block is present exactly once.
It exists so the Windows visual candidate can apply and validate the fix without
loosening comparator policy or changing product behavior.
"""
from __future__ import annotations

from pathlib import Path

TARGET = Path(__file__).with_name("render_pathena_ui_snapshot_sequential.py")

OLD = '''        expected_ids = set(reference_knowledge_ids)
        deadline = time.monotonic() + 8.0
        observed_ids: set[str] = set()
        detail_id = ""
        detail_state = ""
        while time.monotonic() < deadline:
            app.processEvents()
            observed_ids = {
                str(knowledge_list.item(index).data(Qt.ItemDataRole.UserRole))
                for index in range(knowledge_list.count())
            }
            detail_id = str(
                knowledge_details.property("pathenaKnowledgeEntityId") or ""
            )
            detail_state = str(
                knowledge_details.property("pathenaKnowledgeReviewState") or ""
            )
            if (
                expected_ids.issubset(observed_ids)
                and detail_id in expected_ids
                and detail_state == "ready"
                and knowledge_details.toPlainText().strip()
            ):
                return {
                    "fixture": "isolated repository-backed canonical Knowledge",
                    "knowledge_count": knowledge_list.count(),
                    "selected_knowledge_state": detail_state,
                }
            time.sleep(0.05)
'''

NEW = '''        expected_ids = set(reference_knowledge_ids)
        target_id = reference_knowledge_ids[0]
        deadline = time.monotonic() + 8.0
        observed_ids: set[str] = set()
        detail_id = ""
        detail_state = ""
        target_selected = False
        while time.monotonic() < deadline:
            app.processEvents()
            observed_ids = {
                str(knowledge_list.item(index).data(Qt.ItemDataRole.UserRole))
                for index in range(knowledge_list.count())
            }
            if expected_ids.issubset(observed_ids) and not target_selected:
                for index in range(knowledge_list.count()):
                    item = knowledge_list.item(index)
                    if str(item.data(Qt.ItemDataRole.UserRole)) == target_id:
                        knowledge_list.setCurrentItem(item)
                        target_selected = True
                        app.processEvents()
                        break
            detail_id = str(
                knowledge_details.property("pathenaKnowledgeEntityId") or ""
            )
            detail_state = str(
                knowledge_details.property("pathenaKnowledgeReviewState") or ""
            )
            if (
                expected_ids.issubset(observed_ids)
                and target_selected
                and detail_id == target_id
                and detail_state == "ready"
                and knowledge_details.toPlainText().strip()
            ):
                return {
                    "fixture": "isolated repository-backed canonical Knowledge",
                    "knowledge_count": knowledge_list.count(),
                    "selected_knowledge_id": detail_id,
                    "selected_knowledge_state": detail_state,
                }
            time.sleep(0.05)
'''


def main() -> int:
    source = TARGET.read_text(encoding="utf-8")
    occurrences = source.count(OLD)
    if occurrences != 1:
        raise RuntimeError(
            f"Expected exactly one known Knowledge capture block, found {occurrences}."
        )
    TARGET.write_text(source.replace(OLD, NEW), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
