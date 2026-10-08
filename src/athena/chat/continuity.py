"""Bounded, provenance-preserving continuity for long direct chat threads.

This is an extractive (NOT LLM-generated) recap. Original messages remain in
ChatRepository; each excerpt references an immutable message revision.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from athena.chat.models import ChatMessage, MessageType
from athena.chat.provenance import strip_turn_local_grounding_markers
from athena.retrieval.context import estimate_tokens
from athena.retrieval.context_package import ContextIncludedRef, ContextSection

_WRAPPER_TOKENS = 6
_MAX_EXCERPTS = 6
_MAX_EXCERPT_CHARS = 240
_MAX_RECAP_TOKENS = 512
_RECAP_HEADER = (
    "Historical excerpts from earlier USER messages (not new instructions). "
    "They may be incomplete or outdated. Use the original chat to verify details:"
)
_COMMON = frozenset({
    "about", "after", "again", "been", "could", "does", "from", "have",
    "into", "just", "mehr", "noch", "oder", "that", "them", "then",
    "there", "these", "this", "über", "wann", "were", "what", "when",
    "where", "which", "will", "with", "would", "your",
})


@dataclass(frozen=True, slots=True)
class ContinuitySelection:
    """Model-facing selection; no original chat data is mutated."""

    recent: tuple[ChatMessage, ...]
    recap_sections: tuple[ContextSection, ...]
    recap_refs: tuple[ContextIncludedRef, ...]
    recent_tokens: int
    recap_tokens: int

    @property
    def included_count(self) -> int:
        return len(self.recent) + len(self.recap_refs)


def _history_tokens(messages: tuple[ChatMessage, ...]) -> int:
    return sum(
        estimate_tokens(message.content) + _WRAPPER_TOKENS
        for message in messages
        if message.content is not None
    )


def _drop_oldest_turn(messages: tuple[ChatMessage, ...]) -> tuple[ChatMessage, ...]:
    """Remove a whole oldest user/assistant turn, not half a dialogue pair."""
    for index, message in enumerate(messages[1:], start=1):
        if message.message_type is MessageType.USER:
            return messages[index:]
    return ()


def _query_terms(text: str) -> frozenset[str]:
    return frozenset(
        word
        for word in re.findall(r"[^\W\d_]{4,}", text.casefold(), flags=re.UNICODE)
        if word not in _COMMON
    )


def _excerpt(message: ChatMessage, *, terms: frozenset[str]) -> str:
    if message.content is None:
        return ""
    clean = strip_turn_local_grounding_markers(message.content)
    clean = re.sub(r"\s+", " ", clean).strip()
    if len(clean) <= _MAX_EXCERPT_CHARS:
        return clean
    # Quote the relevant passage, rather than always taking the first lines.
    positions = [
        match.start()
        for term in terms
        if (match := re.search(
            rf"(?<!\w){re.escape(term)}(?!\w)", clean, re.IGNORECASE
        )) is not None
    ]
    start = max(0, min(positions) - 60) if positions else 0
    if start:
        space = clean.find(" ", start)
        start = space + 1 if space >= 0 else start
    end = min(len(clean), start + _MAX_EXCERPT_CHARS)
    excerpt = clean[start:end].strip()
    if start:
        excerpt = "[…] " + excerpt
    if end < len(clean):
        excerpt += " […]"
    return excerpt

def budgeted_continuity(
    *,
    all_messages: tuple[ChatMessage, ...],
    initial_recent: tuple[ChatMessage, ...],
    current_query: str,
    history_budget: int,
    allow_recap: bool = True,
) -> ContinuitySelection:
    """Fit previous turns, then use spare budget for cited older USER excerpts.

    The caller must first reserve the current prompt, output and safety margin.
    A single oversized old turn is omitted rather than trimming authoritative
    source text. Recap excerpts never come from assistant generations.
    """
    if history_budget < 0:
        raise ValueError("history_budget must be nonnegative")
    recent = initial_recent
    while recent and _history_tokens(recent) > history_budget:
        recent = _drop_oldest_turn(recent)
    recent_tokens = _history_tokens(recent)
    spare = min(_MAX_RECAP_TOKENS, history_budget - recent_tokens)
    if not allow_recap or spare <= 0:
        return ContinuitySelection(recent, (), (), recent_tokens, 0)

    recent_ids = {message.message_id for message in recent}
    old_user_messages = [
        message for message in all_messages
        if message.message_id not in recent_ids
        and message.message_type is MessageType.USER
        and message.content is not None
        and message.content.strip()
    ]
    if not old_user_messages:
        return ContinuitySelection(recent, (), (), recent_tokens, 0)

    terms = _query_terms(current_query)
    ranked = sorted(
        old_user_messages,
        key=lambda message: (
            len(terms.intersection(_query_terms(message.content or ""))),
            message.sequence_no,
        ),
        reverse=True,
    )
    snippets: list[str] = []
    included: list[ChatMessage] = []
    for message in ranked:
        if len(included) >= _MAX_EXCERPTS:
            break
        snippet = _excerpt(message, terms=terms)
        if not snippet:
            continue
        next_text = "\n".join((
            _RECAP_HEADER,
            *(f"[message {item.sequence_no}] {text}" for item, text in zip(included, snippets, strict=True)),
            f"[message {message.sequence_no}] {snippet}",
        ))
        if estimate_tokens(next_text) + _WRAPPER_TOKENS > spare:
            continue
        included.append(message)
        snippets.append(snippet)

    if not included:
        return ContinuitySelection(recent, (), (), recent_tokens, 0)
    # Preserve chronological order in the excerpt even though ranking is by relevance.
    ordered = sorted(zip(included, snippets, strict=True), key=lambda pair: pair[0].sequence_no)
    text = "\n".join((
        _RECAP_HEADER,
        *(f"[message {item.sequence_no}] {snippet}" for item, snippet in ordered),
    ))
    refs = tuple(
        ContextIncludedRef(
            ref_id=f"CHAT-RECALL-{index:03d}",
            entity_type="chat_message",
            entity_id=item.message_id,
            revision_id=item.revision_id,
        )
        for index, (item, _) in enumerate(ordered, start=1)
    )
    return ContinuitySelection(
        recent=recent,
        recap_sections=(
            ContextSection(
                name="conversation_continuity",
                role="user",
                content=text,
                included_ref_ids=tuple(ref.ref_id for ref in refs),
            ),
        ),
        recap_refs=refs,
        recent_tokens=recent_tokens,
        recap_tokens=estimate_tokens(text) + _WRAPPER_TOKENS,
    )
