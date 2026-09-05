# Independent Windows EXE Test Build Handoff

## Purpose

User-requested disposable Windows executable for testing the current pATHENA Develop version.

## Source identity

- source branch: `develop/pathena-next`
- exact source SHA: `415debaae20fd84cd12fa0613dc063dc48dd134f`
- packaging branch: `independent/windows-exe-test-20260905`
- `main` is untouched.

## Ownership / collision avoidance

This branch must not be treated as product development. It adds packaging-only files:

- `scripts/pathena_frozen_entry.py`
- `.github/workflows/windows-test-exe.yml`
- this handoff

No Backend/Core/UI/Error-owned product or test file is modified. Bots should not merge this packaging branch into Develop as feature work.

## Packaging contract

The Windows test EXE is built with Python 3.12 and PyInstaller 6.22.2 from the locked desktop environment. The frozen entry point dispatches the self-launched child roles already expected by `DesktopCoreSupervisor` and `DesktopJobSchedulerSupervisor`:

- `-m athena.api.process ...` -> Core API process
- `-m athena ...` -> canonical ATHENA CLI / scheduler role
- no role arguments -> pATHENA desktop shell

The workflow smoke-tests both frozen role dispatch paths plus a headless Qt application startup before publishing an artifact.

## Artifact

Expected artifact name: `pathena-windows-test-415debaa`.
Expected executable: `pATHENA-Test-415debaa.exe`.

The executable is an unsigned development build. It is not a release, installer, promotion candidate, or claim of repository-wide Develop verification.
