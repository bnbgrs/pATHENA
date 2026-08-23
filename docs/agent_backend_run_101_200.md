# Backend agent run 101-200

Scope: `bnbgrs/pATHENA`, branch `agent/pathena`. Backend only. This run did not intentionally modify desktop/Qt/UI code or GitHub Actions/quality-gate code.

Status legend:

- **FIXED**: production code changed and a targeted regression test was added.
- **VERIFIED**: current production code already enforces the reviewed invariant; no change needed.
- **FINDING**: audit task completed and a real residual issue was identified, but the large/high-conflict production file was intentionally not replaced blindly on the shared branch.

No local pytest/Ruff/Mypy execution is claimed by this log.

## Tasks 101-200

101. **VERIFIED** — Confirmed the active backend branch is `agent/pathena` before writes.
102. **VERIFIED** — Established stale-SHA/409 as the no-overwrite rule for concurrent branch edits.
103. **VERIFIED** — Reviewed durable `JobPriority` enum identity after the service-level typed-priority fence.
104. **VERIFIED** — Reviewed `JobState` terminal-state semantics; no new transition defect found.
105. **VERIFIED** — Reviewed `WaitingReason` enum after the service-level typed waiting-reason fence.
106. **VERIFIED** — Restore job recovery rejects bool/non-integer/negative `now_us` before transaction ownership.
107. **VERIFIED** — Restore reconciliation refuses to adopt an already-active transaction.
108. **VERIFIED** — Scheduler lane lock rejects non-`Path` lock identities before filesystem access.
109. **VERIFIED** — Scheduler lane lock rejects non-text/empty lane identities before filesystem access.
110. **VERIFIED** — Scheduler lane lock rejects a direct symlink lock path and rechecks after parent creation.
111. **VERIFIED** — Lease sizing rejects bool/non-integer/nonpositive base lease extensions.
112. **VERIFIED** — Provider-isolation capability classification fails closed for malformed/non-string job types.
113. **VERIFIED** — SQLite write transactions reject nesting and unexpected early transaction termination.
114. **VERIFIED** — Stable SQLite reads validate `max_attempts`, restore `query_only`, and retry stale snapshots.
115. **VERIFIED** — Database preflight rejects a symlink primary database path.
116. **VERIFIED** — Database preflight rejects unsafe WAL/SHM sidecars and orphaned sidecars.
117. **VERIFIED** — Database preflight rejects foreign/missing ATHENA application identity and unsupported schema versions.
118. **VERIFIED** — Database preflight runs read-only `quick_check` before normal writer startup.
119. **FIXED** — `Argon2idParameters` direct construction now rejects bool-as-integer `format_version`.
120. **FIXED** — `Argon2idParameters` direct construction now rejects bool/non-integer `iterations`.
121. **FIXED** — `Argon2idParameters` direct construction now rejects bool/non-integer `lanes`.
122. **FIXED** — `Argon2idParameters` direct construction now rejects bool/non-integer `memory_cost_kib`.
123. **FIXED** — `Argon2idParameters` direct construction now rejects bool/non-integer `length`.
124. **FIXED** — Persisted Argon2 parameter decoding now requires textual JSON input.
125. **FIXED** — Persisted Argon2 parameter JSON now requires the exact current field set.
126. **FIXED** — Missing Argon2 parameter fields are rejected before object construction.
127. **FIXED** — Extra Argon2 parameter fields are rejected rather than silently ignored.
128. **FIXED** — Added a current Argon2 profile JSON roundtrip regression.
129. **FIXED** — Password KDF input now requires actual `bytes` and rejects empty passwords consistently.
130. **FIXED** — Argon2 salt input now requires actual `bytes` before length/KDF handling.
131. **FIXED** — Password derivation now requires an actual `Argon2idParameters` object.
132. **FIXED** — AES-256-GCM key input now requires actual `bytes` before key-length validation.
133. **FIXED** — Encrypt nonce input now requires actual `bytes` before nonce-length validation.
134. **FIXED** — Encrypt plaintext input now requires actual `bytes` before cryptography backend invocation.
135. **FIXED** — Encrypt AAD input now requires actual `bytes` before cryptography backend invocation.
136. **FIXED** — Malformed decrypt nonce/ciphertext/AAD inputs now share the generic authentication-failure channel.
137. **FIXED** — Ciphertext hashing now requires actual `bytes` instead of accepting arbitrary buffer-like surprises.
138. **FIXED** — Added a valid AES-GCM encrypt/decrypt roundtrip regression to guard the hardened adapter.
139. **VERIFIED** — Backup retention `daily` count is already bool-safe and nonnegative.
140. **VERIFIED** — Backup retention `weekly` count is already bool-safe and nonnegative.
141. **VERIFIED** — Backup retention `monthly` count is already bool-safe and nonnegative.
142. **VERIFIED** — Backup retention `yearly` count is already bool-safe and nonnegative.
143. **VERIFIED** — Retention planning requires a typed `BackupRetentionPolicy`.
144. **VERIFIED** — Retention candidates require a tuple of typed candidate records.
145. **VERIFIED** — Retention candidate snapshot UUID identities are validated and must be unique.
146. **VERIFIED** — Retention candidate timestamps are bool-safe/nonnegative and checked against datetime range.
147. **VERIFIED** — Deletion-ledger record codec requires an exact persisted field set.
148. **VERIFIED** — Deletion-ledger numeric fields are bool-safe and enforce their minimums.
149. **VERIFIED** — Deletion-ledger UUID text is canonicalized and rejected when noncanonical.
150. **VERIFIED** — Deletion-ledger `entity_type` is nonempty canonical text at backup decode.
151. **VERIFIED** — Deletion-ledger filesystem root rejects symlinks/non-directories.
152. **VERIFIED** — Deletion-ledger records reject symlinks/non-regular files.
153. **VERIFIED** — Deletion-ledger records must be byte-for-byte canonical JSON.
154. **VERIFIED** — Deletion-ledger record filenames bind the full canonical record payload hash.
155. **VERIFIED** — Deletion-ledger sequence must remain contiguous from 1.
156. **VERIFIED** — Deletion-ledger head requires exact fields, supported format and valid SHA-256 hex.
157. **VERIFIED** — Deletion-ledger head target identity must match the backup target descriptor.
158. **VERIFIED** — Deletion-ledger writes fsync staged bytes, use durable replace, and verify published bytes.
159. **FINDING** — `lifecycle/deletion.py` still has low-level scalar checks where bool/float can satisfy integer comparisons (`deleted_at_us`, `deletion_commit_seq`, `after_seq`). Large transactional file intentionally not blindly replaced.
160. **VERIFIED** — UUID arguments in deletion paths now benefit from the shared exact `uuid_to_blob()` boundary hardened earlier.
161. **VERIFIED** — Model domain file is value-object-only; provider normalization belongs at adapter/service boundaries.
162. **FIXED** — Embedding provider timeout now requires a finite positive numeric value and rejects bool/NaN/Inf.
163. **FIXED** — Embedding `model_id` now requires text before request construction.
164. **FIXED** — Embedding model IDs are normalized once and the normalized ID is the value sent to LM Studio.
165. **FIXED** — Embedding inputs reject naked `str`/`bytes`/`bytearray` pretending to be a sequence of texts.
166. **FIXED** — Embedding input sequences reject non-string members before network access.
167. **FIXED** — Embedding input sequences reject whitespace-only members before network access.
168. **VERIFIED** — Empty real embedding sequences remain a no-op and do not require a network call.
169. **FIXED** — Explicit embedding-model resolution now turns malformed IDs into controlled `ModelProviderError`.
170. **VERIFIED** — Embedding response `data` must have exactly the normalized input count.
171. **VERIFIED** — Embedding response indices already reject bool/non-integer values and duplicates.
172. **VERIFIED** — Missing embedding response indices are detected during ordered reconstruction.
173. **VERIFIED** — Embedding vectors reject empty/non-list payloads, bools and non-numbers.
174. **VERIFIED** — Embedding vector components reject NaN and infinities.
175. **VERIFIED** — Embedding result vectors must have one consistent dimensionality.
176. **FIXED** — Chunking algorithm input is now text-typed/nonempty before immutable configuration hashing.
177. **FIXED** — Optional chunking tokenizer is now text-typed/nonempty when supplied.
178. **FIXED** — Chunking `target_size` is now exact-int, bool-safe and positive when supplied.
179. **FIXED** — Chunking `overlap_size` is now exact-int, bool-safe and nonnegative when supplied.
180. **FIXED** — Chunking `profile_version` is now exact-int, bool-safe and positive.
181. **FIXED** — Chunking `structure_rules` now must be a JSON object rather than arbitrary JSON/Python data.
182. **FIXED** — Chunking nested JSON object keys now must be strings.
183. **FIXED** — Chunking nested floating-point values now must be finite.
184. **FIXED** — Chunking config rejects tuple/set/bytes/UUID/object-style Python-only values instead of JSON coercion.
185. **FIXED** — Chunking configuration hash is computed only from the normalized, strict JSON-safe configuration.
186. **FIXED** — Invalid chunking configurations are regression-tested to fail before opening a DB write transaction.
187. **FIXED** — Structured-model prompt wrapper now rejects non-text/empty schema identifiers.
188. **FIXED** — Structured-model prompt wrapper rejects leading/trailing whitespace in schema identifiers.
189. **FIXED** — Structured-model prompt wrapper rejects newline injection in schema identifiers.
190. **FIXED** — Structured-model prompt wrapper rejects carriage-return injection in schema identifiers.
191. **FIXED** — Added an exact control-line regression for the structured prompt prefix.
192. **VERIFIED** — Source-analysis model module is passive durable value objects/enums; active validation is correctly located in service/job contracts.
193. **FINDING** — External explicit authorization still permits bool-as-int TTL and lacks full runtime type checks for purpose/route/host sequence in the large gateway file.
194. **FINDING** — External `capture_url` still permits bool-as-int `max_bytes` and lacks finite-type timeout validation at the gateway entry.
195. **VERIFIED** — External URL authorization already restricts schemes to HTTP(S), prohibits URL credentials and enforces default ports.
196. **VERIFIED** — Tor Preferred transport does not silently fall back to Direct; explicit direct authorization remains required.
197. **VERIFIED** — Direct transport DNS resolution rejects every resolved non-global address before connection.
198. **VERIFIED** — Runtime/durable filesystem layers already enforce direct symlink rejection and durable publication barriers for reviewed paths.
199. **VERIFIED** — Final branch compare detected parallel desktop/settings/test commits; no stale full-file overwrite was performed by this run.
200. **VERIFIED** — Production diffs for Argon2, crypto, embedding, chunking and structured-schema fixes were re-read from committed GitHub diffs before closing the run.

## Commits created by this run

- `75d3698e1613816f81a407058b8b2705ac5280c4` — security: make Argon2 parameter contract exact and bool-safe
- `c4761700e8ac7ebe42d552dff093a309b44b2596` — test: cover exact Argon2 parameter boundary
- `3e368e70ed030f434beee60c0ab438668266cdcf` — security: harden crypto adapter byte boundaries
- `9d37ceaa0a68e17f5c23f5c1537409986a670342` — test: cover crypto adapter byte boundaries
- `29cda9c8f29b857deea5a14596f6c78a3d133513` — model: harden embedding adapter input boundaries
- `4083c60213ec40c47133d985632464a853500d24` — test: cover embedding adapter scalar boundaries
- `b244299b8fc3631a9e01218d7aa4c25b70afe68e` — source: harden chunking profile configuration boundary
- `c334c3fe75e8b88adee82607bfb0e5561092bbb8` — test: fence invalid chunking profile configuration before database
- `494956dd7ca7aa48d3a6d28cd4dd79908f174f46` — model: fence structured schema identifier before prompt wrapper
- `f7e9aedaa528b7993408415a798d4f9471f1d5fe` — test: cover structured schema identifier fence

## Residual high-value backend findings

The next coherent backend slice should patch these only after reading the then-current full files and rebasing around concurrent writers:

1. `src/athena/external/gateway.py`: exact runtime types for authorization purpose/route/TTL/host sequences, capture `max_bytes`, finite timeout, and malformed URL port normalization.
2. `src/athena/lifecycle/deletion.py`: exact-int/bool-safe deletion timestamps, commit sequence and read cursor before SQL access.
3. `src/athena/source/protected_blob.py`: persisted protected-source metadata should reject negative `original_modified_at_us` and keep exact scalar typing.
4. `src/athena/resource/manager.py` (or current equivalent): verify/set typed `ResourceMode` at the mutation entry, while preserving the already strict resource scalar helpers.

This run intentionally did not run or edit GitHub Actions/quality-gate workflows.
