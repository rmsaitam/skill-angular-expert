---
description: Validate an ANGULAR-EXPERT-IMPL.md artifact against the implementation report contract and its 80% coverage gate.
argument-hint: "[path/to/ANGULAR-EXPERT-IMPL.md]"
---

# Validate Angular Expert Report

Validate an existing `ANGULAR-EXPERT-IMPL.md` produced by the `angular-expert` skill.

## Instructions

- Default to `ANGULAR-EXPERT-IMPL.md` at the repository root when no path is provided.
- Run:

  ```bash
  python3 skills/angular-expert/scripts/validate_report.py ANGULAR-EXPERT-IMPL.md
  ```

- From an installed skill directory, prefix the script path with `skills/angular-expert/` only if the layout requires it.
- Use `--strict` to treat warnings as failures, `--json` for machine-readable output and `--min-coverage N` to change the default 80% gate.
- Check that the detected stack and the existing test runner match the report, including Jest with `jest-preset-angular` when that is the configured runner.
- Do not modify the report unless the user explicitly asks for fixes. If fixes are requested, preserve the artifact markers and re-run the validator.
