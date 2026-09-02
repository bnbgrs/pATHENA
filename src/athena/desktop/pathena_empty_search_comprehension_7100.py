"""Differentiate empty data from zero-match filtering on existing search surfaces.

The command palette and canonical-memory filter already own their search behavior.
This presentation-only controller only annotates their existing status labels after
filtering has run, so zero matches are explicit without adding search controls,
changing filtering, or fabricating results.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QLabel, QListWidget, QWidget

from athena.desktop.canonical_memory_extensions import CanonicalMemoryExtension
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_command_palette_truth_6500 import (
    CommandPaletteTruthController,
)


class EmptySearchComprehensionController(QObject):
    """Add explicit no-match semantics to current filtering results."""

    def __init__(
        self,
        window: QWidget,
        palette: CommandPaletteController,
        palette_truth: CommandPaletteTruthController,
        canonical: CanonicalMemoryExtension,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.palette = palette
        self.palette_truth = palette_truth
        self.canonical = canonical
        self.knowledge_search = canonical.workspace.search_input
        self.counts = getattr(canonical, "counts", None)

        palette.query.textChanged.connect(self._schedule_palette_sync)
        self.knowledge_search.textChanged.connect(self._schedule_knowledge_sync)
        for listing in (
            canonical.workspace.knowledge_list,
            canonical.workspace.claim_list,
            canonical.workspace.review_list,
        ):
            model = listing.model()
            model.rowsInserted.connect(self._schedule_knowledge_sync)
            model.rowsRemoved.connect(self._schedule_knowledge_sync)
            model.modelReset.connect(self._schedule_knowledge_sync)
        self._schedule_palette_sync()
        self._schedule_knowledge_sync()

    def _schedule_palette_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync_palette)

    def _schedule_knowledge_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync_knowledge)

    def sync_palette(self) -> None:
        query = " ".join(self.palette.query.text().split())
        count = self.palette.results.count()
        status = self.palette_truth.status
        self.palette.results.setProperty("pathenaSearchResultCount", count)
        self.palette.results.setProperty("pathenaSearchQuery", query)
        if query and count == 0:
            message = f"No commands match “{query}”. Try a broader command or workspace term."
            status.setText(message)
            status.setAccessibleName("No matching commands")
            status.setAccessibleDescription(message)
            status.show()
            self.palette.results.setProperty("pathenaSearchResultState", "no-match")
        else:
            self.palette.results.setProperty(
                "pathenaSearchResultState",
                "matches" if count else "empty",
            )

    def sync_knowledge(self) -> None:
        if not isinstance(self.counts, QLabel):
            return
        query = " ".join(self.knowledge_search.text().split())
        listing = self._active_list()
        visible = self._visible_count(listing)
        total = listing.count()
        self.counts.setProperty("pathenaSearchQuery", query)
        self.counts.setProperty("pathenaSearchVisibleCount", visible)
        self.counts.setProperty("pathenaSearchTotalCount", total)

        base = self._base_counts_text()
        if query and visible == 0 and total > 0:
            suffix = f" · No matches for “{query}”"
            self.counts.setText(base + suffix)
            self.counts.setAccessibleDescription(
                f"Canonical memory filter has no matches for {query}. {total} items exist "
                "in the current view before filtering."
            )
            self.counts.setProperty("pathenaSearchResultState", "no-match")
        elif total == 0:
            self.counts.setText(base + " · Current view is empty")
            self.counts.setProperty("pathenaSearchResultState", "empty")
        else:
            self.counts.setText(base)
            self.counts.setProperty("pathenaSearchResultState", "matches")

    def _active_list(self) -> QListWidget:
        index = max(0, min(2, self.canonical.workspace.browser_tabs.currentIndex()))
        return (
            self.canonical.workspace.knowledge_list,
            self.canonical.workspace.claim_list,
            self.canonical.workspace.review_list,
        )[index]

    def _base_counts_text(self) -> str:
        workspace = self.canonical.workspace
        visible = self._visible_count(self._active_list())
        return (
            f"Knowledge {workspace.knowledge_list.count()} · "
            f"Claims {workspace.claim_list.count()} · "
            f"Decisions {workspace.review_list.count()} · Visible {visible}"
        )

    @staticmethod
    def _visible_count(listing: QListWidget) -> int:
        return sum(
            1
            for index in range(listing.count())
            if not listing.item(index).isHidden()
        )


def install_empty_search_comprehension(
    window: QWidget,
    palette: CommandPaletteController,
    palette_truth: CommandPaletteTruthController,
    canonical: CanonicalMemoryExtension,
) -> EmptySearchComprehensionController:
    """Install no-match comprehension on existing palette and Knowledge filters."""
    controller = EmptySearchComprehensionController(
        window,
        palette,
        palette_truth,
        canonical,
    )
    window.setProperty("pathenaEmptySearchComprehensionController", controller)
    window.setProperty("pathenaEmptySearchComprehensionManaged", True)
    return controller
