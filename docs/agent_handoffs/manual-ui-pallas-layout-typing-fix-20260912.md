# UI PALLAS layout typing repair — 2026-09-12

## Exact lineage

- UI source candidate: `postmerge/ui@67994fd72ba9f496b50aa407b36d789a4edfb804`.
- Isolated repair branch: `manual/ui-pallas-layout-typing-fix-20260912`.
- Product repair commit: `70519a423e0e206eb682e24901bbdb789fa95670`.
- The active `postmerge/ui` ref was not mutated.

## Failure evidence

Canonical Quality run `34676666912@67994fd72ba9f496b50aa407b36d789a4edfb804` completed with:

- specification validator: SUCCESS;
- Ruff: SUCCESS;
- full pytest: `4897 passed, 3 skipped`;
- Windows path safety: SUCCESS;
- Linux storage regressions: SUCCESS;
- Local install smoke: SUCCESS;
- mypy: FAILURE with exactly three diagnostics, all in `src/athena/desktop/pathena_pallas_full_view.py`.

The diagnostics were:

- line 86: `QLayout | None` has no `insertWidget`;
- line 86: possible `None` has no `insertWidget`;
- line 125: possible `None` has no `removeWidget`.

## Root cause

Runtime construction already checked that the shell body layout is a `QHBoxLayout`:

```python
if not isinstance(self._body_layout, QHBoxLayout) or self._center is None:
    raise RuntimeError(...)
```

However, `_body_layout` was first assigned from `QWidget.layout()`, so mypy fixed the attribute type as `QLayout | None`. The later `isinstance` check proved the runtime invariant but did not permanently narrow the instance-attribute declaration at later method use sites.

The full test suite passing confirms this was a static typing contract defect, not a reproduced runtime PALLAS failure.

## Repair

Keep the raw layout in a local variable, validate/narrow that local variable first, and only then assign the narrowed `QHBoxLayout` to the instance attribute:

```python
body_layout = self._reference_body.layout() if ... else None
if not isinstance(body_layout, QHBoxLayout) or self._center is None:
    raise RuntimeError(...)
self._body_layout = body_layout
```

This preserves the existing fail-closed shell invariant and changes no widget hierarchy, navigation behavior, PALLAS state, focus behavior, accessibility behavior or visual presentation.

## Bot coordination rules

1. Do not replace the runtime `QHBoxLayout` guard with an unchecked cast merely to satisfy mypy; the fail-closed shell invariant is intentional.
2. Do not weaken or delete PALLAS tests: the canonical run already proved the runtime test surface green.
3. The active `postmerge/ui` branch remains owned by the UI bot. Consume this one-file fix after exact CI evidence rather than rewriting that branch from this lane.
4. If UI advances, compare `src/athena/desktop/pathena_pallas_full_view.py` first. Reapply only if the layout is still stored before type narrowing.
5. This failure is independent from ERR-0035 and the Backend schedule-policy failure. Keep evidence and integration separate.
6. The Errors worker may register the exact canonical mypy failure if it remains current; do not invent an `ERR-####` ID here.
7. No Skip/XFail, `type: ignore`, unchecked cast, assertion weakening or force-push is required or allowed for this repair.

## Required verification

- UI Focused Candidate SUCCESS;
- canonical mypy SUCCESS;
- canonical full pytest SUCCESS;
- canonical Ruff and specification validator SUCCESS;
- Windows/Linux/local-install lanes remain green.
