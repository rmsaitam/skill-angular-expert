# Validation checklist

Use this checklist when the validator cannot be executed. Every box must be checked before handoff.

## 1. Artifact contract

- [ ] The `<!-- angular-expert:artifact type=implementation version=1 -->` marker appears once.
- [ ] All ten section markers appear once: analysis, stack, design, implementation, tests, validation, configurations, evidence, assumptions, traceability.
- [ ] The stack marker uses the detected Angular version, TypeScript version, build tool, rendering mode, change-detection mode, test runner and strict flag.
- [ ] The coverage marker uses `gate=80` and `tool=jest` with the measured `value`.
- [ ] `CHG-NNN`, `T-NNN`, `CFG-NNN` and `EV-NNN` IDs are unique and stable; every change links to a test and evidence row.
- [ ] No unfinished marker, blank section, dummy text or approval verdict remains.

## 2. Summary and stack

- [ ] All 14 metadata fields are present: Status, Date, Reviewer, Artifact, Angular Version, TypeScript Version, Build Tool, Rendering Mode, Change Detection, Test Runner, Changes Applied, Tests Run, Coverage and Coverage Tool.
- [ ] Versions and modes match `stack.json` and `package.json`, `angular.json`, `tsconfig.json` and the lockfile.
- [ ] Changes Applied equals the number of `CHG-NNN` entries.
- [ ] Unsupported Angular v2-v19 constraints are recorded without proposing a migration.

## 3. Implementation

- [ ] Components stay thin and services own business logic, HTTP access and state.
- [ ] Injection style and provider scopes match the detected version and local conventions.
- [ ] No manual component subscription or nested subscription remains; async pipe, `toSignal()`, `takeUntilDestroyed()` or `DestroyRef` is used where needed.
- [ ] OnPush with immutable updates and explicit `trackBy` or `track` is used where applicable.
- [ ] Version-gated APIs are justified by the detected major version; `@if`, `@for` and `signal()` are not used on unsupported versions.
- [ ] Templates are accessible, styles are encapsulated and sanitization is preserved.
- [ ] No credentials, tokens or fixed environment URLs are hardcoded.

## 4. Tests and coverage

- [ ] Jest with `jest-preset-angular` and TestBed is present, or an existing Karma/Vitest setup is retained with the decision recorded.
- [ ] Test entries use `framework=jest`, `testbed=true` and `context=unit`.
- [ ] Success, validation and error paths are covered with mocked boundaries.
- [ ] Jest coverage thresholds are at least 80% and the measured value is recorded.
- [ ] Every command in the report was actually executed.

## 5. Configurations and evidence

- [ ] New configuration keys are shown exactly with file and key, or the section says `No changes.`
- [ ] Each evidence row has a command and an observed result.
- [ ] Traceability links every change to at least one test and one evidence row.
- [ ] Sensitive values are redacted as `[REDACTED]`; only keys are reported.

## 6. Manual commands

```bash
python3 scripts/detect_stack.py . --output stack.json
npx jest --coverage
python3 scripts/validate_report.py ANGULAR-EXPERT-IMPL.md
```

The detector and report validator must exit with status 0. When the validator cannot run, state that the manual checklist was applied instead.
