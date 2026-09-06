# pATHENA Visual Gap Ledger

Baseline: `859e1a68e8d9a207a5094462aefe189f6f276c9d`
Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

Only evidence-backed gaps belong here. The original 11 reference screenshots remain unavailable for direct visual comparison; therefore all screenshot-level work remains `VISUAL_REFERENCE_PENDING` and no pixel-level `MATCH` claim is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract
- Screen: `10 — Grounded Chat / Evidence & Activity`; Category: `HIERARCHY`; Severity: `P1`; Status: `FIXED`.
- Product `1f0fd548431be122d13a403fe9e2387087edf8fa`; test `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`; exact Quality `33720745475` passed.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive
- Screens: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`; Category: `INTERACTION`; Severity: `P1`; Status: `FIXED`.
- Product `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`; test `1685221150c724deceb5d150a4d2dcff2bdd867b`; exact corrected head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed Quality `33745885426`.

## UI-GAP-0003 — PALLAS full-view transition can hit a transient missing tab-order document binding
- Screen: `08 — PALLAS`; Category: `INTERACTION`; Severity: `P1`; Status: `FIXED`.
- Product `689da6c1dc2221f89825fffde947f792c7b503e7`; focused regression `034cb8d923d48bea708b48cac0ef0f6343511051`; exact UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` passed Quality `33751403354`.

## UI-GAP-0008 — Local Core readiness could be mistaken for Internet-access state
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P1`; Status: `FIXED`.
- Product `9dd1836154a190fdcb9f9a690b46035f9dcacda6`; exact UI head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` passed Quality `33854660676`.

## UI-GAP-0009 — Core connection failure can retain stale loopback-only presentation metadata
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P1`; Status: `FIXED`.
- Product `ad416f76cd52eadd42aa7f2b09a96ce43bf737c7`; test `d7e85654db03eb21da35a5fa06d3bdf94cb4a1a5`; exact head `6d6869d4927a52e98158238f396b8d5855b771b9` passed Quality `33860150646`.

## UI-GAP-0010 — Fresh Core snapshot accessibility depended on delayed comprehension sync
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P1`; Status: `FIXED`.
- Product `0722d780b94d8d297bd89e417ae09fab08cb4dcf`; test `a2d7030101a01415af99b5a8cba31ad10550e5de`; exact head `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` passed Quality `33864721817`.

## UI-GAP-0011 — Pre-first-snapshot Settings runtime state lacks explicit fail-closed metadata
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P1`; Status: `FIXED`.
- Product `44ae9513ec5b77586d98a45c02afe0fe171af932`; test `b307a771860c455b1630c2885ca1295e08a900d0`; exact head `45e2b84d14bfc11b4878d9b945065063fdc40e6d` passed Quality `33874283635`.

## UI-GAP-0012 — Initial Settings persistence state lacked explicit non-success freshness metadata
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `d9797b5ff665b2c94ad7a9c34a6843d06f7cda4d`; test `5c9b49773ea16dfa6db341da37ab33d12f9ee7c5`; exact head `3a1be68c48dab4176e9258170147cf127c4b3d2a` passed Quality `33879947654`.

## UI-GAP-0013 — Runtime detail state lacks explicit freshness/accessibility transition metadata
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `046414551ad85bc418af0c7bdfdc2d8be7befd7d`; test `7de1ccb040083375fb31242f54b9515b18403113`; exact head `622f85338613b7d59ef5b1bd0fd05eae3d488c47` passed Quality `33891068183`.

## UI-GAP-0014 — No-model persistence state incorrectly claims fresh model persistence
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product lineage `e1218685577230fa6ad190291ad0f626912853ac`; test `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24`; exact head `3d3ac638ce35c2bd149cea2358ef726f243244f0` passed Quality `33897120327`.

## UI-GAP-0015 — Unsaved per-model defaults incorrectly present persistence freshness as fresh
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `e175de079fd30dc2fb1bc3c64065ebd40127cd0b`; test `0b0303e89c4fd358291e0fb180062212debdeff7`; exact head `be55343dcaab9eb2afe80fe869000c139e6e2de1` passed Quality `33902213148`.

## UI-GAP-0016 — Unreadable local settings expose opaque backend model identifier in user-facing error copy
- Screen: `07 — Settings`; Category: `COPY / ACCESSIBILITY / STATE`; Severity: `P2`; Status: `FIXED`.
- Product `b0bac270a461afdef3322550e6ddf3e49314653a`; test `5d819895dfbfecc6c7a24f46251d0e3a07791409`; exact head `f66a1cc2c80cf0cadc89ba1a4771345af79df934` passed Quality `33912482820`.

## UI-GAP-0017 — Fresh non-ready provider detail is styled as idle while provider state is error
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `a0c8ea842e6dfb4c029b7a722eeb4b43189941e5`; test `f668520bef1d2789b70cb7561b8e0f5dd4fd6041`; exact head `72c143fae1e339b254e5dc7be884c8efb79c7f84` passed Quality `33917796701`.

## UI-GAP-0018 — Unavailable provider detail remains idle while provider state is error
- Screen: `07 — Settings`; Category: `STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `82fb17da950f8234e28c69bd576e38047ba9b2bb`; test `6aad966258288a7519af6d261dea4695e7ffde76`; corrective product `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`; exact corrective head passed Quality `33926653411`.

## UI-GAP-0019 — Unavailable provider detail copy describes generic readiness instead of the actual unavailable state
- Screen: `07 — Settings`; Category: `COPY / STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `6bfce859c177dfc75119a63c270c028b5b3c5772`; test `de688468ff3265d997a2b4c5a39d0aebdf89a9da`; exact final head `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` passed Quality `33937005854`.

## UI-GAP-0020 — Model-list failure hides a still-known provider behind generic unavailable copy
- Screen: `07 — Settings`; Category: `COPY / STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `64b9956601f2ec21ee3624d27323221dc2aba10c`; focused test `7b4569dd55c93cb19b5dfe2d53ea0c2ccc34fe71`; exact UI head `9ca1cb04031d618bd6d34d2df4a46d331d110a82` passed Quality `33942660590`.

## UI-GAP-0021 — Empty Core connection-failure text produces an empty visible/accessibility error detail
- Screen: `07 — Settings`; Category: `COPY / STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `43a62eeb393a8929a92b3273ca49d427d6eb095d`; focused test `f2cc20321c79809a37079b0525b2aab676ac8682`; exact UI head `f2cc20321c79809a37079b0525b2aab676ac8682` passed Quality `33947967906`.

## UI-GAP-0022 — Empty Core health status produces an incomplete visible/accessibility connection label
- Screen: `07 — Settings`; Category: `COPY / STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Evidence: `HealthResponse.core_status` has no non-empty invariant; empty/whitespace values previously rendered `Local Core · `.
- Product `afe37f4a4a6677239ae4e0ea8fa5d8681d273b1d`; focused test `cdca131585b15559145c43eef204f34518dad39e`.
- Verification evidence: exact UI head `f36ffd143ae51b5e6e0fd653cefddbd33ce0b886` passed ATHENA Quality Gate `33953459102` with conclusion `success`.

## UI-GAP-0023 — Empty provider identity/status produces incomplete provider presentation
- Screen: `07 — Settings`; Category: `COPY / STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `c2c681f2a9a60baf43afa0b11eae81ef0db11110`; focused test `90447e0ba08ed7d3e41723702d16ea624d524e1b`; exact UI head `d70147b804447ef9834d3ce27661682cf0ea98f7` passed Quality `33956094573`.

## UI-GAP-0024 — Whitespace provider detail can render an effectively blank runtime detail
- Screen: `07 — Settings`; Category: `COPY / STATE / ACCESSIBILITY`; Severity: `P2`; Status: `FIXED`.
- Product `8b986323cabcb459e4203af1e5bdbe1fbb62375c`; focused coverage consolidated by `216c3270df0658ac19d16b043531b48d05bcae93`; exact UI head `77b3f9582d4530dbe081e3c81b8768ad00d3f050` passed Quality `33966822035`.

## UI-GAP-0025 — Glyph-only primary navigation lacks human accessible item text
- Screen: `01 — Workspace / Chat`; Category: `ACCESSIBILITY / NAVIGATION`; Severity: `P1`; Status: `FIXED`.
- Product `b3deae1671a8832e94fd8b3ef85fefa916ced468`; focused shell coverage `b25bc07059bc116ec25a4e7ce924a89f4508e2df`.
- Acceptance: visible glyphs, rail width, destination ordering, tooltips and navigation behavior remain unchanged; every rail item exposes Workspace/Library/Research/Jobs/Sources/System/Settings through `Qt.ItemDataRole.AccessibleTextRole`.
- Verification evidence: exact synchronized UI head `fb98e47fde410137b971a303678d4e63f66e1d6d` passed ATHENA Quality Gate `33978582156` with conclusion `success`; the prior full-suite PySide6 SIGSEGV from `33975657049` did not recur.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0026 — Global top navigation lacks an explicit keyboard-focus treatment
- Screen: `01 — Workspace / Chat`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: the specialized top-bar stylesheet explicitly defined normal, hover and checked presentation for `topNavButton` and normal/hover presentation for glyph-only `topUtilityButton`, but no `:focus` presentation existed for either keyboard-focusable control family. Because the specialized stylesheet suppresses native borders, keyboard focus had no explicit pATHENA focus contract.
- Product `6cc37912531c648ed8374f6585efd7cbdec9db3d`; focused stylesheet coverage `d40aee5fdc98571f725f644806b272726ad74041`.
- Verification evidence: exact UI head `074c7b9a4ccf9271a91dd1e56784601f749ac020` passed ATHENA Quality Gate `33981877292` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0027 — Glyph primary rail suppresses native outline without an explicit focused-current state
- Screen: `01 — Workspace / Chat`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `QListWidget#navigation` explicitly sets `outline: none` and previously provided item normal/hover/selected styling but no keyboard-focused current-item rule.
- Product/test candidate `38793f4e116900d4d06db0aff9a8e42c69272141` adds `QListWidget#navigation:focus::item:current` using canonical readable text, `surface_hover`, and the existing 2px accent left edge while preserving visible glyphs, selection semantics, accessible item labels, rail dimensions and navigation routing.
- Verification evidence: exact synchronized UI head `779b28a0845e80bb16feadca28f5eaba26124db9` passed ATHENA Quality Gate `33987939232` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0028 — Composer Send button lacks an explicit keyboard-focus treatment
- Screen: `01 — Workspace / Chat`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `QPushButton#sendButton` explicitly defined normal, hover and pressed presentation while the adjacent `QLineEdit#promptInput` has an explicit focus state; no `sendButton:focus` rule existed.
- Product/test `8c132673f7a991ae1fc16e27b0d65342bdae02e9` adds a canonical-token focus state using `accent_hover` plus a 2px readable-text border. The existing 48px fixed control geometry, hover/pressed states and send routing are unchanged.
- Verification evidence: exact UI head `5a5ba2681412c32c181e63026ce1b92574675d64` passed ATHENA Quality Gate `33991088294` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0029 — Workspace action controls lack explicit keyboard-focus presentation
- Screen: `01 — Workspace / Chat`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `detailsToggle`, `contextToggle`, `newChatButton`, `deleteChatButton`, `rememberMessageButton`, `addKnowledgeButton`, and `groundButton` define transparent normal borders plus hover and/or checked/disabled states but previously had no explicit `:focus` presentation.
- Product `d25d563ed02ac677a038f522c050e7942d6b0462` adds a shared explicit focus state using canonical readable text, `surface_hover`, and accent border color without changing routing, labels, enabled/disabled semantics, or checked-state behavior.
- Focused regression `a4cfa5522cb666c9cf53ae53c5a297746fee2f38` verifies all seven selectors and canonical focus tokens.
- Verification evidence: exact UI head `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa` passed ATHENA Quality Gate `33996745959` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0030 — Help reader lacks explicit keyboard-focus presentation
- Screen: `09 — Command Palette / Help`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Corrected evidence: the prior query-focus hypothesis was false because the later-applied Foundation already contains `QLineEdit:focus` with canonical accent border, so `commandPaletteQuery` is covered without another rule. `CommandPaletteController.open_help()` deliberately lands focus on read-only `QPlainTextEdit#helpText`, while the Foundation focus selector did not include `QPlainTextEdit` and the specialized `helpText` rule had no `:focus` state.
- Product `811b43c37e6010667b6779ccbf886715647e23dc` adds only `QPlainTextEdit#helpText:focus` to the existing canonical focus selector; focused regression finalized at `9875e1c4e3a33753225398d0f2a08971e78977fe` verifies the selector shares the canonical accent-border declaration. Existing F1 focus landing, read-only behavior, text content, shortcuts and backend/runtime semantics are unchanged.
- Verification evidence: exact documentation successor `f09406daab9440ee77a06e907add84280b3ae936` passed ATHENA Quality Gate `34001923188` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0031 — Canonical memory tabs lack an explicit focused-selected keyboard state
- Screen: `02 — Library / Knowledge`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `canonicalMemoryTabs` has specialized normal, hover and selected tab presentation, but no focused-selected rule. The selected tab therefore did not distinguish keyboard focus on the tab bar from an unfocused selected tab.
- Product `089f005aa6d81a6a4a15cc8594c74eeeed417373` adds `QTabWidget#canonicalMemoryTabs QTabBar:focus::tab:selected` using only canonical readable text, `surface_hover`, and the existing 2px accent bottom edge.
- Focused regression `e18fe9945e805230aa9c1af95202d8b9c81ba822` verifies the selector and canonical tokens. Existing tab labels, routing, selected semantics, accessibility metadata and backend/runtime behavior are unchanged.
- Verification evidence: exact documentation successor `856d9f56fac059f257451c2e31fd35b4e554e55f` passed ATHENA Quality Gate `34004718037` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0032 — Library detail readers lack explicit keyboard-focus presentation
- Screen: `02 — Library / Knowledge`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `KnowledgeWorkspace` creates read-only `QPlainTextEdit#persistentKnowledgeDetails`, `QPlainTextEdit#persistentClaimDetails`, and `QPlainTextEdit#semanticReviewDetails`. These surfaces are keyboard-focusable for reading/copying, but the shared explicit focus block previously covered only `QPlainTextEdit#helpText` among plain-text readers.
- Product `4be86b946333e88160d4f7a11fe4199c23d2c0ec` adds only the three object-specific `:focus` selectors to the existing canonical accent-border focus block.
- Focused regression `ebe9aaa0d465df78e52782ce0f2d4d5dab6a2086` verifies all three selectors and the canonical accent border. Read-only behavior, detail content, selection routing, provenance, persistence and backend/runtime semantics remain unchanged.
- Verification evidence: exact UI head `062440397c9330ac23e9f8b3293d822f2451c902` passed ATHENA Quality Gate `34007202893` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
