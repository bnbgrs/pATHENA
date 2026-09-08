# pATHENA Visual Gap Ledger

Baseline: `c775d37f50e332639007ba162b4ff7f591434f1c`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. The original 11 reference screenshots remain unavailable for direct visual comparison; therefore no pixel-level mismatch or `MATCH` claim is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract
- Category: `HIERARCHY`; Screen: `10 — Grounded Chat / Evidence & Activity`; Severity: `P1`; Status: `FIXED`.
- Product/Test: `1f0fd548431be122d13a403fe9e2387087edf8fa` / `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`.
- Verification: exact head `f31be028652095b18b8a98dfacd65b73be9af763`, Quality `33720745475 = success`; integrated in Develop.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive
- Category: `INTERACTION`; Screens: `01`, `10`; Severity: `P1`; Status: `FIXED`.
- Product/Test: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2` / `1685221150c724deceb5d150a4d2dcff2bdd867b`.
- Verification: exact head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb`, Quality `33745885426 = success`; integrated as `93a9344d3902c920da5ff283eb51bbb1f0d815b8`.

## UI-GAP-0003 — PALLAS full-view transition can hit a transient missing tab-order document binding
- Category: `INTERACTION`; Screen: `08 — PALLAS`; Severity: `P1`; Status: `FIXED`.
- Product/Test: `689da6c1dc2221f89825fffde947f792c7b503e7` / `034cb8d923d48bea708b48cac0ef0f6343511051`.
- Verification: exact head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d`, Quality `33751403354 = success`; bounded equivalents integrated in Develop.

## UI-GAP-0060 — Context disclosure help was not exposed to accessibility
- Category: `ACCESSIBILITY`; Screen: `10`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `0565720d2d3b3349e6fc8556083dc035fa8c389f` / `70f8867a2645cd2795853745f54844efe8c70d0c`; Quality `34113040437 = success`.

## UI-GAP-0061 — Settings control help is visual-only instead of screen-reader available
- Category: `ACCESSIBILITY`; Screen: `07 — Settings`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `ffac0e737c3c3457a49ce4b830492f26ba7127d1` / `930dc168f5700f03720601664caf23b08ecd7603`; Quality `34118404763 = success`.

## UI-GAP-0062 — Cancellation-requested Jobs help leaks an internal persisted-state token
- Category: `COPY`; Screen: `04 — Jobs`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `f82be0e672659ee74ce8aecae5a7b4f157cbe6a0` / `c37c8b17a5b33a68068c04c5b5b0fe41b53e927c`; Quality `34124133923 = success`.

## UI-GAP-0063 — Jobs action help exposes persistence/lifecycle implementation jargon
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `50eb723d18430735b5dcbb246563ae8e863c62a9` / `1a92d020d565424da147909f137779f7ce1e35fc`; Quality `34129349248 = success`.

## UI-GAP-0064 — Terminal Jobs help still uses lifecycle-domain jargon
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `717aee14e7a357bf1022dda5c4e5d9ac006ef0f8` / `d294b7a0e96464d5700c00af3565895a526622f1`; Quality `34134425435 = success`.

## UI-GAP-0065 — Empty Jobs action help exposes storage-domain terminology
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `0ac91c9f471bb14aa6094f78d017cd59d529d868` / `25f8c53cfef2f9524ec3ce2b696809bc1159893c`; Quality `34139713588 = success`.

## UI-GAP-0066 — Unknown Jobs state leaves a visible destructive action fail-open
- Category: `STATE`; Screen: `04`; Severity: `P1`; Status: `FIXED`.
- Product/Test: `83c57b7898515085c7ba4f9441029165c3123890` / `96891f1d68ee9e0242c41aa4b846fea39094ec54`; Quality `34144645412 = success`.

## UI-GAP-0067 — Jobs action help is visual-only instead of screen-reader available
- Category: `ACCESSIBILITY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `6543d82199f8f5360cc205f6303dc133f9468dd7` / `f823fe99c9c7ce78b3d0d70aaf257966ae692364`; Quality `34148642145 = success`.

## UI-GAP-0068 — Jobs receipt validation errors expose implementation-domain language
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `998e28ccd9b3c4739e658c2efe55ba164f2bc98b` / `849b72a882f8d07a5678bc0e4770b55229c18723`; Quality `34152552680 = success`.

## UI-GAP-0069 — Jobs verification-failure surface still exposes receipt jargon
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `9ea12288a2e0363787c64fb8ded9a5302a4a52bd`; Quality `34156844241 = success`.

## UI-GAP-0070 — Jobs success state exposes transition/persistence implementation language
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `869821057ee1af071f72e37d9aa8d593e3ba52f6` / `a91f9ecf06531ec6dd3bcf6424076096aee0651a`; Quality `34160631088 = success`.

## UI-GAP-0071 — Jobs empty-state guidance exposes storage implementation language
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `b7e96e01e5690d914be62d489faae92bf0e59571` / `067983b6613a42526ac48cbd5d21b3e36d1e3e74`; Quality `34164101918 = success`.

## UI-GAP-0072 — Jobs workspace intro exposes implementation architecture
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test: `c3637e08e64c1f08438b477a940b073b504de3` / `b927515fb5371f02f5da4cf4a90aa3d596d34ed0`; Quality `34167675010 = success`.

## UI-GAP-0073 — Jobs progress/status copy exposes persistence-oriented implementation terms
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED`.
- Product/Test/Harness: `4315a744a097c35ab46be4df883f0853544446b9` / `cf777ca08ac0885c636aed95b5f6ddd6cd381386` / `352b4c72c39d5cafe866c604a050a1b93df71940`.
- Verification: exact head `352b4c72c39d5cafe866c604a050a1b93df71940`, Quality `34174030199 = success`.

## UI-GAP-0074 — Jobs nonzero-exit status exposes command-oriented implementation language
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED_INTEGRATOR_READY`.
- Evidence: `_process_finished()` previously exposed `Jobs command ... failed (exit N)` for refresh/detail/action failures.
- Product/Test: `ee2dafc9453c8e3b5d67aed107a955b086111f68` / `10ddf88043757628906480541e179323f5af7247`.
- Verification: exact descendant head `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` carrying unchanged product/test passed Quality `34187727628 = success`.
- Acceptance: failures identify the user operation and retain exit code/background ownership without command/lifecycle/storage/scheduler/worker/backend semantic changes.

## UI-GAP-0075 — Jobs QProcess error surface exposes process/command implementation language
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `FIXED_INTEGRATOR_READY`.
- Evidence: `_process_error()` previously described failures as local/Jobs command failures. The bounded candidate now names `Jobs refresh`, `Job details`, or the actual job action while retaining the underlying QProcess error class.
- Product/Test: `86444c8a762f910d9929f50841f78376312a0afe` / `9af7d23d2daccdee78236b6da335090d512d7fcd`.
- Verification: exact descendant head `4d6d1f7b3bc99dbff3015ddb8c499af885859ac8` passed Quality `34187727628 = success`; no process-spawn/relaunch/runtime semantics changed.

## UI-GAP-0076 — Cancellation-requested action help exposes Worker architecture
- Category: `COPY`; Screen: `04`; Severity: `P2`; Status: `IMPLEMENTED_PENDING_VERIFY`.
- Evidence: `JobActionAvailability.reason()` visibly said cancellation was waiting for `worker acknowledgement`, exposing internal Worker architecture through tooltip/accessibility help.
- Product commit: `08d64fd4c9ffbbea428c4e18c8ffd784394adf0e`.
- Focused regression commit: `bcc471caef3b902f8cd4b07c969d896e9ae349cc`.
- Acceptance: cancellation-requested help says it is waiting to complete and contains no Worker/persistence/lifecycle jargon; enabled/disabled action matrix, cancellation state, scheduler/worker/storage/backend semantics remain unchanged.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
