# pATHENA Visual Gap Ledger

Baseline: `2bc57c4c84a0ed13ca9adbbc61f8fd00fc87fb8f`
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
- Verification evidence: exact UI head `062440397c9330ac23e9f8b3293d822f2451c902` passed ATHENA Quality Gate `34007202893` with conclusion `success`; documentation successor `3c5fe2e16293e9bfb8228e62b0f7a183b34a92f7` passed Quality `34009763554`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0033 — Library lists lacked row-level focused-current presentation
- Screen: `02 — Library / Knowledge`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `persistentKnowledgeList`, `persistentClaimList`, and `semanticReviewList` are keyboard-focusable. The shared foundation provided widget-level focus border but previously no object-specific `:focus::item:current` rule, so the active keyboard row was visually identical to the corresponding unfocused selected row.
- Product `5b6f8a5740d463524daf4cfae14c0335b2207693` adds only the three object-specific focused-current selectors using canonical readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d` verifies all three selectors and canonical focus tokens. Selection routing, item content, refresh behavior, provenance, persistence and backend/runtime semantics are unchanged.
- Verification evidence: exact UI head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea` passed ATHENA Quality Gate `34012079406` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0034 — Research job list lacks row-level focused-current presentation
- Screen: `03 — Research`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `ResearchWorkspace` creates keyboard-focusable `QListWidget#researchJobList`. The shared foundation supplies a widget focus border and selected-row presentation, but before this slice it had no `researchJobList:focus::item:current` rule, so the active keyboard row was not separately expressed from the unfocused selected row.
- Product `0da430fdccb469b1edf8fd7adf01773b5ec5340f` adds `QListWidget#researchJobList:focus::item:current` to the existing canonical focused-current selector block, using readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `3d9339295f3c413c4c7a31c2a7037600bc3b93f6` locks the selector and canonical tokens. Research selection routing, durable-job state, cancellation semantics, scheduler behavior and backend/runtime semantics are unchanged.
- Verification evidence: exact UI documentation head `5a40e75ed78293ddd8c1ea3533c5632d6dea2910` passed ATHENA Quality Gate `34014713429` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0035 — Research detail reader lacks explicit keyboard-focus presentation
- Screen: `03 — Research`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `ResearchWorkspace` creates read-only `QPlainTextEdit#researchDetails`. The surface remains keyboard-focusable for reading/copying, but the shared explicit focus block covered the Help and Library detail readers while omitting `researchDetails`.
- Product `f9d0a01de648ea806bfd725c3b35a68fc9eb425d` adds only `QPlainTextEdit#researchDetails:focus` to the existing canonical accent-border focus selector. Focused regression `4183addc10689496101c2b4d6ae7d45fcb4cf3d1` locks the selector and canonical accent border.
- Durable research content, selection routing, cancellation, scheduler behavior, read-only semantics and backend/storage/security/runtime behavior are unchanged.
- Verification evidence: exact UI head `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4` passed canonical ATHENA Quality Gate `34019891561` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0036 — Jobs detail reader lacks explicit keyboard-focus presentation
- Screen: `04 — Jobs`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `PathenaJobsExperience._configure_tab_order()` explicitly places `workspace.details` between the durable jobs list and Refresh control; `_configure_accessibility()` identifies it as `Durable job details`, and `_configure_details()` keeps the `QPlainTextEdit#jobDetails` reader presentation. The specialized `jobDetails` stylesheet had no focus state and the canonical reader-focus selector covered Help, Library and Research readers but omitted Jobs.
- Product `605c63992e112a168ddeda403b561740d524c018` adds only `QPlainTextEdit#jobDetails:focus` to the existing canonical accent-border focus block. Focused regression `8ae0f51e0637e75d7619e7fb9c4fe65679c6f626` locks the selector and canonical accent border.
- Durable job content, filtering, action enablement, transitions, scheduler behavior, read-only semantics and backend/storage/security/runtime behavior are unchanged.
- Verification evidence: exact UI documentation head `8cbec3ef97a13caf626450a0111ee3dc50b262cc` passed canonical ATHENA Quality Gate `34022762486` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0037 — Durable jobs list lacks row-level focused-current presentation
- Screen: `04 — Jobs`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `JobsWorkspace` creates keyboard-focusable `QListWidget#durableJobList`, and the shared foundation provides widget-level focus plus selected-row presentation. Before this slice, the canonical focused-current selector block covered Library and Research lists but omitted the durable Jobs list, so the active keyboard row did not receive the same explicit row-level focus treatment.
- Product `7a518d2ab2e7b0255187650ff961c6fa7132a284` adds only `QListWidget#durableJobList:focus::item:current` to the existing canonical focused-current block, using readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `3f17c1e68be68e6f560cd27e70dfca9f3961db95` locks the selector and canonical focus tokens. Durable job content, selection routing, refresh, action availability/transitions, scheduler behavior and backend/storage/security/runtime semantics remain unchanged.
- Verification evidence: exact UI documentation head `6558031bb31e5e35f5c8639bf4f5c8591f7fa250` passed canonical ATHENA Quality Gate `34025529919` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0038 — Sources list lacks row-level focused-current presentation
- Screen: `05 — Sources / Files`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `FilesWorkspace` creates keyboard-focusable `QListWidget#sourceList`; before this slice the canonical focused-current selector block covered Library, Research and Jobs but omitted Sources.
- Product `ea1d62fedc1fa67715f4f1f7c20621931a4a3db8` adds only `QListWidget#sourceList:focus::item:current` using readable text, `surface_hover`, and the existing 2px accent left edge. Focused regression `bc20c308e97cfdf88a8109f2b4a4d1d60b387a62` locks the selector and canonical focus tokens.
- Verification evidence: exact UI documentation head `3d89bffeef82244361e701738ebc05862d1a2b64` passed ATHENA Quality Gate `34028122788` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0039 — Sources detail reader lacks explicit keyboard-focus presentation
- Screen: `05 — Sources / Files`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `FilesWorkspace` creates read-only `QPlainTextEdit#sourceDetails`; the reader remains keyboard-focusable for reading/copying, while the canonical object-specific reader-focus block covered Help, Library, Research and Jobs but omitted Sources.
- Product `6d2d0eb32fa0bcd6b2c1112070a36ce1401f6bfa` adds only `QPlainTextEdit#sourceDetails:focus` to the existing canonical accent-border focus block. Focused regression `57636da80d3f3db586d1d728b4e6d39dd11896bd` locks the selector and canonical accent token.
- Source content, import/retrieval processing, selection routing, read-only semantics, provenance and backend/storage/security/runtime behavior are unchanged.
- Verification evidence: exact UI head `d955ccd53e3e2c7f98af0f6f3838be1ffa9b6fe6` passed canonical ATHENA Quality Gate `34031028328` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0040 — System detail text lacks explicit keyboard-focus presentation
- Screen: `06 — System`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `SystemWorkspace` creates `QLabel#systemDetail` and explicitly enables `TextSelectableByKeyboard`; the shared canonical focus block previously covered buttons, inputs, lists and read-only plain-text readers, but not this keyboard-selectable System detail label.
- Product `330fd20ec285b44dee8c9f89597a9c75e55c9c95` adds only `QLabel#systemDetail:focus` to the existing canonical accent-border focus block. Focused regression `4cba0e0235ea5094f9f39b4d3f615879ca4362df` locks the selector and canonical accent token.
- Runtime facts, refresh routing, Core/provider/storage/security semantics and text-selection behavior are unchanged.
- Verification evidence: exact UI head `0d5a89b879ee0959a42734181adb129f4c3de024` passed canonical ATHENA Quality Gate `34034051224` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0041 — System runtime status values lack explicit keyboard-focus presentation
- Screen: `06 — System`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: each `_SystemStatusRow` creates `QLabel#settingsValue` and explicitly enables `TextSelectableByKeyboard`; these live runtime values are therefore keyboard-interactive for reading/copying, while the canonical focus block covered `QLabel#systemDetail:focus` but not the status-value object family.
- Product `96b6f2525bf2572fe2eeaa09eda8cddc80ae18a1` adds only `QLabel#settingsValue:focus` to the existing canonical accent-border focus block. Focused regression `36b3b9441f1202353cab42b867292ff292f8cb4a` locks the selector and canonical accent token.
- Runtime values, snapshot projection, refresh routing, text-selection behavior and Core/provider/storage/security semantics are unchanged.
- Verification evidence: exact UI head `c249c0ec1c3a3a19617bcb5c6f3c2d4899d4a0fd` passed canonical ATHENA Quality Gate `34036984000` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0042 — System Security posture values are not keyboard-selectable
- Screen: `06 — System`; Category: `ACCESSIBILITY / KEYBOARD / INTERACTION`; Severity: `P1`; Status: `FIXED`.
- Evidence: `_PostureRow` exposes snapshot-backed Loopback only, Local processing, Encrypted at rest and Tor status values through the same `QLabel#settingsValue` presentation as major runtime facts, but unlike `_SystemStatusRow` it did not enable text selection. Keyboard users therefore could not focus/select/copy these truthful live posture facts even though `settingsValue` already has the verified canonical focus treatment.
- Product `f7086b9838bdbb29a3fbfef7dd1eeb070ff4fead` enables only `TextSelectableByMouse | TextSelectableByKeyboard` on `_PostureRow.value`; focused regression `50c483a985053bb6450de93e6ddae3e03b6720ff` locks the object family and both interaction flags.
- Security facts, snapshot projection, state vocabulary, Core/provider/storage/security semantics and control routing are unchanged; this is read/copy accessibility only.
- Verification evidence: exact UI head `81b8d6c2c250a412bb2947b2b356d9111c10b995` passed canonical ATHENA Quality Gate `34040342678` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0043 — Settings checkbox lacks explicit keyboard-focus presentation
- Screen: `07 — Settings`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: Settings exposes the keyboard-focusable reasoning/thinking control as a `QCheckBox`; the shared canonical focus block covered buttons, line edits, combo boxes, spin boxes, lists and reader controls but omitted `QCheckBox:focus`.
- Product `05c9ee062ae29b3ba075521fc645bc63aea31b23` adds only `QCheckBox:focus` to the existing canonical accent-border focus selector family; focused regression `74f8d885a5a8ede339545f282bc42bdf1f1199e5` locks that selector and canonical focus border.
- Checkbox value semantics, thinking/reasoning request routing, model persistence, provider/Core state and backend/storage/security behavior are unchanged.
- Verification evidence: exact UI head `b021424a3d6b79786b695b00356c2f98fa7390dc` passed canonical ATHENA Quality Gate `34043271088` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0044 — Settings runtime facts are not keyboard-selectable with explicit focus presentation
- Screen: `07 — Settings`; Category: `ACCESSIBILITY / KEYBOARD / INTERACTION`; Severity: `P1`; Status: `FIXED`.
- Evidence: the snapshot-backed Provider, Connection, Persistence and runtime-detail labels expose important live/local state through `settingsProviderState`, `settingsNetworkState`, `settingsPersistenceState` and `settingsRuntimeDetail`, but previously used plain-text QLabel presentation without keyboard text selection or object-specific focus styling. Keyboard users therefore could not select/copy these truthful Settings facts consistently with System runtime facts.
- Product `caa288717e3eb8f403cece7c43affbb6e3282be2` enables only `TextSelectableByMouse | TextSelectableByKeyboard` on the four existing runtime labels; coupled presentation product `fd013674ff126d3f7a6429fe08c7240fcd7b2b50` adds only their four object-specific `:focus` selectors to the existing canonical accent-border focus block. Focused regression `691011884825a91227d35eb6d42b915e9a5bc4e6` locks both selection flags, all four object identities and their canonical focus selectors.
- Runtime text/state vocabulary, snapshot projection, persistence behavior, provider/Core semantics, network truthfulness and backend/storage/security behavior are unchanged; this is read/copy/focus accessibility only.
- Verification evidence: exact UI head `c9762d1b65dd6c9db1c30ae9cba9510f83ab942f` passed canonical ATHENA Quality Gate `34049733492` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0045 — PALLAS semantic canvas lacks explicit keyboard-focus presentation
- Screen: `08 — PALLAS`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `FIXED`.
- Evidence: `_PallasCanvas` is a `StrongFocus` frameless `QGraphicsView`. Semantic nodes have their own focus outlines after node focus exists, but the canvas itself previously had no explicit pATHENA widget-focus presentation when keyboard focus first enters the canvas.
- Product `73653063f4922d1e7168f06560c7f0e6bfda1fb7` adds only `QGraphicsView#pallasSemanticCanvas:focus` to the existing canonical accent-border focus block. Focused regression `1bbecf2c9a3a8ed738b7203e39085e65477a0f28` locks the selector and canonical accent border.
- PALLAS graph data, node selection, keyboard traversal, pan/zoom, Inspector synchronization and backend/Core semantics are unchanged.
- Verification evidence: exact UI head `59b2046d5e127664195f7ecf17245c45f70f00ca` passed canonical ATHENA Quality Gate `34052665337` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0046 — PALLAS full synchronized workspace lacks a conflict-free keyboard opening path
- Screen: `08 — PALLAS`; Category: `ACCESSIBILITY / KEYBOARD / INTERACTION`; Severity: `P1`; Status: `FIXED`.
- Evidence: the compact semantic field exposes a real double-click path to the synchronized full PALLAS workspace, but keyboard users had no equivalent opening path. Plain Enter, keypad Enter and Space are already intentionally owned by semantic-node selection in `_PallasCanvas.keyPressEvent`, so intercepting them would break the verified keyboard selection contract.
- Product `4b4eb8c0ee1ea66f7f9c50a03c464330b02f7143` installs the full-view event filter on the real compact canvas in addition to its viewport and adds only `Ctrl+Enter` as the full-view keyboard command. Existing left-button double-click remains unchanged. Target/canvas tooltip and accessible description expose the same shortcut.
- Focused regression `5ce4d87f7360741087d7a59a91441faa8e6d8a83` proves plain Enter does not open the full view, Ctrl+Enter opens the single synchronized full workspace, focus lands on the full semantic canvas, and the keyboard path is exposed in accessibility copy.
- Graph state, node selection, Enter/Space selection behavior, pan/zoom, Inspector synchronization, Core/backend/storage/security and runtime semantics are unchanged.
- Verification evidence: exact UI head `38a28f61af16d0b12500b4056b586ba934a2ba1a` passed canonical ATHENA Quality Gate `34056114998` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0047 — Command Palette results lack row-level focused-current presentation
- Screen: `09 — Command Palette / Help`; Category: `ACCESSIBILITY / KEYBOARD / STATE`; Severity: `P1`; Status: `IMPLEMENTED_PENDING_VERIFY`.
- Evidence: `CommandPaletteController` creates keyboard-focusable `QListWidget#commandPaletteResults`, routes Up/Down movement and Enter activation, and the shared foundation already provides normal/hover/selected item styling plus a widget-level `QListWidget:focus` border. The canonical focused-current row block covered Library, Research, Jobs and Sources lists but omitted Command Palette results, so the active keyboard row was not separately expressed from an unfocused selected row.
- Product `ca27570a842a98754dfcce0741bd946ba2711689` adds only `QListWidget#commandPaletteResults:focus::item:current` to the existing canonical focused-current selector block using readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `5a2351300fc46974e68bdd7ce120848995f12c5f` locks the selector and canonical focus tokens.
- Query filtering, command ordering, Up/Down movement, Enter activation, command routing, F1 help and backend/storage/security/runtime semantics are unchanged.
- Verification evidence: canonical Quality on the exact final product/test/documentation successor is pending; no PASS is claimed yet.
- Visual status: `IMPLEMENTED_PENDING_VERIFY`; no screenshot-level `MATCH` claim.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
