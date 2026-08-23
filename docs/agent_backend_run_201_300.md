# Backend agent run 201-300

Scope: `bnbgrs/pATHENA`, branch `agent/pathena`. Backend only. This run did not intentionally modify desktop/Qt/UI code or GitHub Actions/quality-gate code.

Status legend:

- **FIXED**: production code changed and a targeted regression test was added or updated.
- **VERIFIED**: current production code already enforces the reviewed invariant; no change needed.
- **FINDING**: audit task completed and a real residual issue was identified, but a large/high-conflict production file was intentionally not blindly replaced on the shared branch.

No local pytest/Ruff/Mypy execution is claimed by this log.

## Tasks 201-300

201. **VERIFIED** — Confirmed backend work remains on `agent/pathena` and stale-SHA writes must fail rather than overwrite concurrent edits.
202. **VERIFIED** — Re-read the current Source tree before touching Protected Content code.
203. **FIXED** — Protected Source metadata decoding now requires an actual `bytes` payload.
204. **FIXED** — Protected Source metadata `format_version` now rejects `bool` and non-integer values instead of accepting `True == 1`.
205. **FIXED** — Protected Source metadata continues to require the exact persisted field set.
206. **FIXED** — Persisted `original_modified_at_us` now rejects booleans.
207. **FIXED** — Persisted `original_modified_at_us` now rejects negative timestamps.
208. **FIXED** — Persisted plaintext byte length remains exact-int/bool-safe and nonnegative.
209. **FIXED** — Direct `ProtectedSourceMetadata` construction now validates actual `SourceType` identity.
210. **FIXED** — Direct Protected Source name and URI construction now requires non-empty text.
211. **FIXED** — Direct Protected Source MIME metadata is restricted to text or `None`.
212. **FIXED** — Direct Protected Source modification time and plaintext length now use exact nonnegative integer validation.
213. **FIXED** — Protected Source capture now rejects non-`Path` path arguments before filesystem access.
214. **FIXED** — Protected Source capture now requires a UUID protection-scope identity before crypto/storage work.
215. **FIXED** — Protected Source capture now requires a real `SourceType` before crypto/storage work.
216. **FIXED** — Protected Blob AAD construction now validates UUID identities, bool-safe chunk index range and plaintext frame length; current boundaries are regression-tested.
217. **VERIFIED** — Re-read observability logging before changing its public configuration boundary.
218. **FIXED** — Logging configuration no longer silently maps unknown level names to `INFO`.
219. **FIXED** — Logging level validation rejects booleans rather than accepting them as integers.
220. **FIXED** — Logging level validation rejects empty/whitespace-only names.
221. **FIXED** — Logging level validation rejects negative numeric levels.
222. **FIXED** — Logging level validation rejects floats, `None` and arbitrary objects.
223. **VERIFIED** — Standard named logging levels remain accepted case-insensitively.
224. **VERIFIED** — `NOTSET` and nonnegative custom integer logging levels remain supported.
225. **FIXED** — Added positive and negative regressions for the observability logging level boundary.
226. **VERIFIED** — Re-read the current health-state module before modification.
227. **FIXED** — Failure health details now require non-empty text.
228. **FIXED** — Recovery-required health details now require non-empty text.
229. **FIXED** — `HealthSnapshot` now requires an actual `HealthStatus` value.
230. **FIXED** — Optional HealthSnapshot detail is validated when present.
231. **FIXED** — The internal health mutation helper now rejects untyped statuses.
232. **VERIFIED** — Valid failure details are preserved verbatim rather than unexpectedly normalized.
233. **FIXED** — Added regressions for malformed failure and recovery health details.
234. **FIXED** — Added a regression for untyped HealthSnapshot status values.
235. **VERIFIED** — Re-read the current hierarchical Source Analysis value objects after parallel changes.
236. **FIXED** — `SourceAnalysisWorkInput.work_item_id` now requires an actual UUID.
237. **VERIFIED** — Analysis input ordinal was already bool-safe and is kept nonnegative.
238. **FIXED** — Analysis input kind now requires an actual `AnalysisInputKind` before tagged-reference branching.
239. **FIXED** — SOURCE_ANCHOR inputs now require exactly one UUID `source_anchor_id` and no artifact reference.
240. **FIXED** — ARTIFACT inputs now require exactly one UUID `artifact_id` and no source-anchor reference.
241. **VERIFIED** — Re-read current bootstrap settings rather than relying on the earlier finding.
242. **VERIFIED** — Bootstrap log level now already requires a string and an allowed normalized level.
243. **VERIFIED** — Runtime/archive/backup/projection roots now already require `Path` objects and absolute paths.
244. **VERIFIED** — LM Studio base URL now already requires text.
245. **VERIFIED** — LM Studio bootstrap URL catches invalid port syntax and restricts the host to loopback.
246. **VERIFIED** — LM Studio bootstrap URL rejects credentials, path, query and fragment components.
247. **VERIFIED** — Model request timeout is already bool-safe, finite and positive.
248. **VERIFIED** — Model generation timeout is already bool-safe, finite and positive.
249. **VERIFIED** — Environment timeout parsing routes defaults through the same finite-positive validator.
250. **VERIFIED** — Recovery CLI still bypasses normal Core startup for isolated restore and maps recovery/configuration errors to controlled exit status.
251. **VERIFIED** — Re-read the current Doctor before aligning its runtime-root checks.
252. **FIXED** — Doctor runtime-write check now rejects a direct symlink root instead of reporting it writable.
253. **FIXED** — Doctor rechecks the runtime root after directory creation before creating a write probe.
254. **FIXED** — Doctor runtime-write helper fails closed for a non-`Path` root.
255. **VERIFIED** — Optional archive/backup/projection Doctor checks already warn on symlink roots.
256. **FIXED** — `run_doctor()` now requires an actual `AthenaSettings` object.
257. **FIXED** — `run_doctor()` now requires an actual boolean `startup_smoke` flag.
258. **VERIFIED** — A real writable Doctor runtime directory remains accepted.
259. **FIXED** — Added a symlink-root regression ensuring no Doctor write probe is created through the link.
260. **FIXED** — Added Doctor entry-boundary regressions for settings and startup-smoke types.
261. **VERIFIED** — Re-read rank-fusion and lexical-threshold primitives before changing shared retrieval math.
262. **FIXED** — RRF rank now requires an exact positive integer.
263. **FIXED** — RRF rank rejects booleans rather than treating `True` as rank 1.
264. **FIXED** — RRF rank rejects floats, strings, `None`, zero and negatives.
265. **FIXED** — RRF `k` now requires an exact positive integer.
266. **FIXED** — RRF `k` rejects booleans, floats, strings, `None`, zero and negatives.
267. **VERIFIED** — The current RRF contribution formula is unchanged for valid inputs.
268. **FIXED** — Shared informative-term count now requires an exact positive integer.
269. **FIXED** — Informative-term count rejects bool-as-int values.
270. **FIXED** — Informative-term count rejects floats, strings, `None`, zero and negatives.
271. **VERIFIED** — Existing 1-3, 4-5 and two-thirds lexical threshold behavior is preserved for valid counts.
272. **FIXED** — Added a combined retrieval-scalar regression suite covering invalid and valid boundaries.
273. **VERIFIED** — API contract JSON serialization already rejects non-finite floating-point values.
274. **VERIFIED** — API contract JSON serialization already rejects non-string dictionary keys and recursively converts supported tuples to JSON arrays.
275. **FIXED** — Semantic retrieval fallback reason codes now require text before normalization.
276. **FIXED** — Empty semantic retrieval fallback reason codes are rejected while valid surrounding whitespace is normalized.
277. **FIXED** — Retrieval model IDs now require non-empty text before provider resolution.
278. **FIXED** — Retrieval degradation now rejects providers that do not expose callable `resolve_model()`.
279. **FIXED** — Provider validation was corrected to capability/duck typing rather than an unnecessarily strict concrete-class check.
280. **FIXED** — Added a regression proving a compatible duck-typed resolver remains accepted and returns hybrid mode.
281. **VERIFIED** — Shared UUID-to-blob conversion requires an actual `uuid.UUID` before database encoding.
282. **VERIFIED** — Shared blob-to-UUID conversion requires actual bytes and exactly 16 bytes.
283. **VERIFIED** — ResourceManager interactive lease duration already rejects bool/non-integer/nonpositive values.
284. **VERIFIED** — ResourceManager interactive timestamps already require exact nonnegative integers.
285. **VERIFIED** — Resource snapshot RAM/VRAM totals and available values are typed and cross-checked for available <= total.
286. **VERIFIED** — Resource CPU/GPU fractions already reject booleans, NaN, infinity and values outside `[0,1]`.
287. **VERIFIED** — Resource snapshot `model_loaded` already requires boolean or `None`, and degraded metrics require canonical text.
288. **VERIFIED** — Resource snapshot persistence receives a fresh identity and fails conservatively when telemetry sampling itself fails.
289. **FINDING** — `ResourceManager.set_mode()` still uses `mode.value` after actor creation without first requiring an actual `ResourceMode`; patch should be rebased on the then-current ~28 KB manager file.
290. **FINDING** — Low-level `record_deletion()` still calls `.strip()` on `entity_type` without a runtime text check.
291. **FINDING** — Low-level deletion timestamp comparison still accepts bool-as-int and can raise uncontrolled type errors for non-numeric values.
292. **FINDING** — Low-level deletion commit sequence comparison still accepts bool-as-int and lacks exact integer validation.
293. **FINDING** — `read_deletion_records(after_seq=...)` still relies on a raw comparison and therefore lacks exact-int/bool-safe cursor validation.
294. **VERIFIED** — Deletion UUID arguments now pass through the shared exact UUID-to-blob boundary before SQL identity use.
295. **FINDING** — External explicit authorization still calls `.strip()` on `purpose` without a runtime text check.
296. **FINDING** — External allowed-host input is typed as `Sequence[str]` but still permits malformed sequence shapes such as a naked string to reach host iteration.
297. **FINDING** — External authorization TTL and direct-fallback TTL still use numeric comparisons/minimum logic that accepts Python booleans as integers.
298. **FINDING** — External capture `max_bytes` still accepts bool-as-int, and timeout validation does not explicitly reject non-finite values before transport selection.
299. **VERIFIED** — External network policy still restricts HTTP(S), forbids credentials/non-default ports, prevents silent Tor→Direct fallback, and rejects non-global direct-resolution addresses.
300. **VERIFIED** — Final branch compare and current Protected-Blob re-read confirmed the run's core invariants remain present despite parallel commits; no stale full-file overwrite was forced.

## Commits created by this run

- `36fb396b56ad71b3ce278c61f15a001c9f6b1d6d` — source: harden protected blob metadata boundaries
- `76af230fa243dc53d22db4d4d769726e75e86c52` — test: cover protected blob metadata boundaries
- `1f641a2860733c2dd16f884377042048e4bfe9fd` — observability: reject malformed logging levels
- `dd381aa730328f2631d928a731736347d35173f8` — test: cover observability logging level boundary
- `51cf51edc34a1c8876bcc170e0d76869754e446a` — observability: validate health state boundaries
- `744fc113803db9025429daa8e1e5fc41bc4f7141` — test: cover health state boundaries
- `b9c530397348cca9c1c1fb7b85e3d32181f6d553` — source: harden analysis work input identities
- `d2f52ee97a4534d03eb5548fd1bbbd700e0cd48d` — test: cover analysis work input identity boundaries
- `2e3db43e5d018fd99e32bc1380ff7ac7ea5d7c96` — doctor: align runtime root checks with storage contract
- `705d5aee9d611db8f242168f97a86d280833b68e` — test: align doctor runtime boundary with storage contract
- `48e4571dc2887e4931077589d7b373250779bc19` — retrieval: validate reciprocal rank scalar boundaries
- `392cac6408b798089432f2183cfdb417e8df12a7` — retrieval: require exact informative term count
- `8ff9ba8436fd93cbc3ec2e5c2d456ea7c2c66d4a` — test: cover retrieval scalar boundaries
- `2e8baaa947b077a46d4b1fc04ae6edced920f90f` — retrieval: harden degradation boundary types
- `3c96f8d5794825515312f89b530907c9e3016e54` — test: cover retrieval degradation boundaries
- `24924d6cf16854907e68146376bed3d620fc662d` — retrieval: preserve provider duck typing at degradation boundary
- `6c5798139c978d772bc6c5bce4fe65d8f1119d9d` — test: preserve duck typed retrieval resolvers

## Residual high-value backend findings

1. `src/athena/external/gateway.py`: exact runtime types for purpose/route/TTL/host sequences, capture `max_bytes`, finite timeout and controlled malformed URL-port handling.
2. `src/athena/lifecycle/deletion.py`: exact-int/bool-safe deletion timestamp, commit sequence and read cursor, plus text typing before `entity_type.strip()`.
3. `src/athena/resources/manager.py`: typed `ResourceMode` before actor creation and persistence in `set_mode()`.
4. Continue repository-level defense-in-depth only after re-reading the then-current large files; service-level durable-job validation remains the primary persistence fence.

This run intentionally did not run or edit GitHub Actions/quality-gate workflows.