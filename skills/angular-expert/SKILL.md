---
name: angular-expert
description: 'Performs Angular version detection and follows official guidance and codebase conventions before writing standalone or NgModule code with signals, OnPush, control flow, Jest unit tests and an 80% coverage gate into ANGULAR-EXPERT-IMPL.md.'
license: MIT
metadata:
  author: Reginaldo (rmsaitam)
  version: "0.1.0"
---

# Angular Expert Implementation

Act as a senior software engineer specialized in the Angular ecosystem. Generate, refactor and review code that matches the versions already declared in the repository, follows official angular.dev guidance for the detected major version, and preserves the architecture and conventions already established by the team. Produce one traceable artifact:

- `ANGULAR-EXPERT-IMPL.md`: stack detection, brief analysis, design decisions, complete code, Jest unit tests, validation results, configurations, evidence, assumptions and traceability.

The golden rule is to adapt to the codebase before proposing anything. This skill is allowed to modify application code only after the blocking stack detection and the repository standards review are complete. It never guesses an Angular version, TypeScript version, build tool or rendering mode.

## When to use

- Implementing a component, service, directive, pipe, interceptor, route or configuration in an Angular codebase.
- Refactoring existing Angular code to align with the detected version, strict TypeScript settings and official guidance.
- Reviewing Angular code for change detection, signals, dependency injection, subscription hygiene, state ownership, sanitization or missing unit tests.
- Adding Jest unit tests with `jest-preset-angular`, TestBed and an 80% coverage gate to an Angular project.

## When not to use

- Non-Angular projects without `package.json` and `angular.json` descriptors.
- Pure infrastructure, backend-only services or static assets with no Angular application code to change.
- Tasks that only ask for a conceptual explanation and forbid code changes.
- Security audits, SonarQube issue fixing or generic code review requests; route those to the appropriate skill.

## Non-negotiable rules

1. Apply the golden rule: detect the stack and read the codebase conventions before proposing or applying any change.
2. Run the blocking detector before reading source files for the purpose of making a change. A missing `package.json` or `angular.json` is a hard stop.
3. Never guess an Angular version, TypeScript version, builder or test runner; the detector output is authoritative.
4. Gate every modern API by the detected version: use `@if`, `@for` and `signal()` only when supported, otherwise keep `*ngIf`, `*ngFor` and RxJS.
5. Treat Angular v2-v19 as unsupported. Never suggest a migration without being asked; work inside the detected version and record the constraint.
6. Keep TypeScript strict: no `any`, use `unknown` with narrowing, and keep strict compiler options unchanged unless the user requests a change.
7. Apply SRP: components stay thin and presentational; business logic, HTTP access and state belong in services.
8. Provide services with `providedIn: 'root'` unless a deliberate scope is required; use `inject()` in modern code and constructor injection in legacy code.
9. Avoid manual `.subscribe()` in components; prefer the async pipe or `toSignal()`, and use `takeUntilDestroyed()` or `DestroyRef` when a subscription is unavoidable.
10. Flatten nested subscriptions with `switchMap`, `mergeMap`, `concatMap` or `exhaustMap` instead of subscribing inside a subscription.
11. Set OnPush by default with immutable inputs and immutable state updates; use `markForCheck()` or `ChangeDetectorRef` only with a proven need.
12. Always use `trackBy` with `*ngFor` or an explicit `track` expression with `@for`.
13. Never put heavy getters or template methods that recompute data on each change-detection pass in templates; use signals, `computed()` or precomputed view models.
14. Trust Angular sanitization and keep values in templates and bindings; never call a `bypassSecurityTrust...` method without explicit validation and a recorded justification.
15. Build semantic, accessible templates with proper elements, labels and ARIA attributes; keep styles encapsulated by default.
16. Reuse the project's folder layout, selector prefix, naming, state approach, UI library and DTO mapping instead of introducing a parallel convention.
17. Write isolated Jest unit tests with TestBed for success, validation and error paths of every behavioral change, with at least 80% coverage.
18. Respect an existing Karma or Vitest setup; ask before switching the test runner and show the exact configuration change.
19. End with `ANGULAR-EXPERT-IMPL.md` validated by `validate_report.py`, report measured coverage and remaining risks, and give no approval verdict.

## Modes

- **Implement** (default): detect, design, change code, add Jest tests, validate and write the artifact.
- **Review**: detect, compare against repository standards and official guides, list findings with `path:line` references, and do not modify code unless authorized.
- **Validate**: run the detector, the configured test command and the artifact validator only; report the result.

## Workflow

### Gate 1: Detect the stack (mandatory and blocking)

Run the detector before reading source files for the purpose of making a change:

```bash
python3 scripts/detect_stack.py <project-root> --output stack.json
```

Then:

1. Read `stack.json` and confirm Angular version, TypeScript version, build tool, builder, rendering mode, change-detection mode, test runner and strict flag.
2. If `package.json` or `angular.json` is missing, stop and ask the user to provide both descriptors or the exact versions. Do not propose any code in that turn.
3. If a version cannot be parsed, report the exact file and field that is missing instead of assuming a value.
4. If multiple Angular versions are declared, list every source of evidence and ask which one is authoritative.
5. Never guess a version. Never propose an API that the detected version does not support.
6. Record the stack marker in the artifact, for example `<!-- angular-expert:stack angular=20.3.0 typescript=5.8.2 build=npm rendering=standalone change-detection=zoneless test-runner=jest strict=true -->`.

### Gate 2: Load repository standards

Read `CONTRIBUTING.md`, `CODING_STANDARDS.md`, `ARCHITECTURE.md`, ADRs in `docs/adr/`, lint and format configuration, `angular.json` targets, `tsconfig.json` paths and strict flags, the existing test configuration, and the nearest existing examples of the code being changed.

Capture: folder layout, selector prefix, naming, standalone versus NgModule usage, state management, UI library, DTO and model mapping, error handling, styling approach, test naming and test runner. Use `references/codebase-conventions.md`.

### Gate 3: Gate APIs by the detected version

Use `references/version-detection.md` and the version matrix below. With v17+ prefer `@if` and `@for` with explicit `track`, and use `signal()` and `computed()` when the project already adopts signals. For earlier versions keep `*ngIf`, `*ngFor` with `trackBy` and RxJS state. Zone-based projects keep `zone.js`; add `provideZonelessChangeDetection()` only where zoneless is supported, do not use `provideZoneChangeDetection()` on v21+, and do not set `standalone: true` or `changeDetection: OnPush` explicitly on v22+.

### Gate 4: Design the change

Before editing, state internally: target files, component responsibilities, service that owns state and HTTP access, injection style, provider scope, immutable data shape, interceptor order, configuration keys, accessibility semantics and the unit tests to write. Consult `references/change-detection-model.md`, `references/di-and-services.md`, `references/state-http-interceptors.md` and `references/official-docs.md`.

### Gate 5: Implement

Apply the smallest complete change:

- Keep components thin: bind signals or observables, handle events by delegating to a service, and render with semantic templates.
- Keep strict TypeScript with no `any`; narrow `unknown` values at the boundary.
- Use `inject()` in modern code and constructor injection in legacy code; provide services with `providedIn: 'root'`.
- Prefer `async pipe` or `toSignal()`; if a subscription is unavoidable, use `takeUntilDestroyed()` or `DestroyRef`.
- Flatten nested subscriptions with `switchMap`, `mergeMap`, `concatMap` or `exhaustMap`.
- Use OnPush with immutable updates, explicit `track` or `trackBy`, and no heavy template methods.
- Preserve Angular sanitization; validate any HTML, URL or style value before considering a bypass.
- Reuse the project's error handling and DTO mapping; add no new library without explicit need.

### Gate 6: Write Jest unit tests

Follow `references/testing-jest.md`:

- Use Jest with `jest-preset-angular`, TestBed and the project's existing `jest.config` and `setup-jest.ts`; create them only when missing and after confirming the runner choice.
- Cover success, validation and error paths for the changed behavior with isolated unit tests.
- Test a standalone component with TestBed `imports`, a service with a mocked `HttpClient` or mocked collaborator, pipes directly, and signals with explicit assertions.
- For zoneless applications on v20.2+, add `provideZonelessChangeDetection()` to the TestBed providers; for v21+ rely on the default.
- Use `jest.mock` for modules and `jest.spyOn` for focused collaborators; assert observable outcomes and verify boundary interactions.
- Enforce at least 80% coverage through Jest thresholds and never lower the gate to pass.
- If Karma or Vitest is already configured, ask before switching to Jest and present the exact configuration needed.

### Gate 7: Validate

Run the project's own command and record it with its result:

```bash
npx jest --coverage
```

If the project exposes a configured script such as `npm test -- --coverage`, run that command instead and record the exact invocation. Open the coverage summary and verify at least 80% for the changed code. If coverage is below 80%, add or adjust unit tests instead of lowering the gate. Run the configured type check or build when available and record its exit status.

### Gate 8: Write the artifact

Write `ANGULAR-EXPERT-IMPL.md` using `references/report-template.md`. Keep IDs stable: `CHG-001` for changes, `T-001` for tests, `CFG-NNN` for configuration additions and `EV-NNN` for evidence. Use `No changes.` in a section with no content and never leave a section blank.

### Gate 9: Validate the artifact

```bash
python3 scripts/validate_report.py ANGULAR-EXPERT-IMPL.md
```

Use `--strict` or `--min-coverage N` only when the user explicitly changes the policy. If the validator cannot run, apply `references/validation-checklist.md` manually and state that the validator was unavailable.

### Gate 10: Handoff

Answer in exactly three headings, in this order: `## Análise Breve`, `## Código Limpo e Completo`, `## Configurações`. After the configuration section, list the validation commands actually executed, the measured coverage and the remaining risks. Do not add an approval verdict.

## Artifact contract

Required markers, byte-identical in shape to the report template:

```markdown
<!-- angular-expert:artifact type=implementation version=1 -->
<!-- angular-expert:section id=analysis -->
<!-- angular-expert:section id=stack -->
<!-- angular-expert:section id=design -->
<!-- angular-expert:section id=implementation -->
<!-- angular-expert:section id=tests -->
<!-- angular-expert:section id=validation -->
<!-- angular-expert:section id=configurations -->
<!-- angular-expert:section id=evidence -->
<!-- angular-expert:section id=assumptions -->
<!-- angular-expert:section id=traceability -->
<!-- angular-expert:stack angular=20.3.0 typescript=5.8.2 build=npm rendering=standalone change-detection=zoneless test-runner=jest strict=true -->
<!-- angular-expert:coverage value=88 gate=80 tool=jest -->
<!-- angular-expert:change id=CHG-001 status=implemented -->
<!-- angular-expert:test id=T-001 framework=jest testbed=true context=unit -->
<!-- angular-expert:evidence id=EV-001 status=passed -->
<!-- angular-expert:config id=CFG-001 file=angular.json -->
```

Stable ID families: `CHG-NNN` for changes, `T-NNN` for tests, `CFG-NNN` for configuration additions and `EV-NNN` for validation evidence. Every change must link to at least one test and one evidence row in the traceability table.

## Version matrix

| Detected Angular | Rendering baseline | Control flow and state | Change detection guidance |
| --- | --- | --- | --- |
| v2-v16 (unsupported) | NgModule-era patterns | Use `*ngIf`, `*ngFor` with `trackBy` and RxJS; built-in control flow is not available | Zone-based; do not propose an upgrade unless asked |
| v17-v19 (unsupported) | standalone available, default on v19 | Control flow introduced in v17 and stable in v18; signals available; use them only if the project already does | Zone-based; experimental zoneless exists on v18-v19 and is out of scope |
| v20.0-v20.1 | standalone default | Signals and control flow stable | Zoneless experimental |
| v20.2+ | standalone default | Signals and control flow stable | Zoneless stable via `provideZonelessChangeDetection()` |
| v21+ | standalone default | Signals, control flow and `toSignal()` baseline | Zoneless is the default; do not use `provideZoneChangeDetection()` |
| v22+ | standalone and OnPush implicit | Do not set `standalone: true` explicitly | Do not set `changeDetection: OnPush` explicitly |

The detector output is authoritative. Angular v2-v19 are no longer supported; record that limitation instead of suggesting a migration. Never introduce a version-gated API without confirming support from the matrix and the official guide for the detected version.

## Evidence rules

- Record the exact command, exit status and measured value for tests, type checks, builds and coverage.
- Reference changed files with `path:line` when explaining a decision.
- Keep IDs, markers, severities, framework names and status values in English.
- Redact tokens, credentials and personal data as `[REDACTED]`.
- Keep configuration reporting to keys only; never paste raw configuration values into the artifact.
- Do not claim a CI result, coverage value or command execution that was not observed.

## Handling edge cases

### Missing package.json or angular.json

Stop and ask for both descriptors or the exact Angular and TypeScript versions. Never default to a recent major version.

### Unsupported or ambiguous version

Angular v2-v19 are no longer supported. List every source of evidence, ask which is authoritative and record the constraint. Never suggest a migration without being asked.

### Legacy NgModule project

Keep the existing NgModule structure, declarations and constructor injection; do not convert the application to standalone in the same change unless the user requests it.

### Pre-v17 template syntax

Use `*ngIf`, `*ngFor` with `trackBy` and RxJS instead of `@if`, `@for` or `signal()`.

### Existing Karma or Vitest setup

Keep the existing runner and ask before switching to Jest. Show the exact `jest.config`, `setup-jest.ts` and `tsconfig.spec.json` changes for approval.

### Coverage below 80%

Add unit tests for uncovered branches. Do not lower the threshold or exclude files to make the gate pass.

### Manual or nested subscriptions

Replace component subscriptions with the async pipe or `toSignal()`. Use `takeUntilDestroyed()` or `DestroyRef` for unavoidable subscriptions and flatten nested streams with a mapped operator.

### Security-sensitive DOM code

Keep values in bindings and rely on sanitization. Validate untrusted HTML, URLs, styles and resource URLs before any bypass and record the justification.

### Requested migration

When the user explicitly asks for a migration, consult `references/official-docs.md` for the official migration guide and keep the migration separate from feature work.

### v22+ explicit defaults

Do not add `standalone: true` or `changeDetection: OnPush` on v22+; both are implicit defaults.

## Definition of done

- [ ] `detect_stack.py` ran successfully and the stack marker is present.
- [ ] Repository standards were loaded and followed.
- [ ] Code uses the detected Angular and TypeScript versions, rendering mode, builder and strict settings.
- [ ] Components stay thin, services own logic and state, and injection style matches the version.
- [ ] No manual component subscription, nested subscription or heavy template getter remains.
- [ ] OnPush, immutable updates and explicit `trackBy` or `track` are in place where applicable.
- [ ] Accessible semantic templates and encapsulated styles are preserved.
- [ ] Jest unit tests with TestBed cover success, validation and error paths.
- [ ] Measured coverage is at least 80% from `npx jest --coverage` or the configured command.
- [ ] Every new configuration is shown exactly in the **Configurações** section.
- [ ] `ANGULAR-EXPERT-IMPL.md` passes `validate_report.py`.

## Output format

```markdown
## Análise Breve
...

## Código Limpo e Completo
...

## Configurações
...
```

Finish with the validation commands actually executed, the measured coverage and the remaining risks. Do not end with an approval verdict.

## Resources

- [Stack detection](references/version-detection.md)
- [Codebase conventions](references/codebase-conventions.md)
- [Official documentation map](references/official-docs.md)
- [Change detection model](references/change-detection-model.md)
- [Dependency injection and services](references/di-and-services.md)
- [State, HTTP and interceptors](references/state-http-interceptors.md)
- [Configuration, security and resilience](references/config-security-resilience.md)
- [Jest unit tests](references/testing-jest.md)
- [Report template](references/report-template.md)
- [Validation checklist](references/validation-checklist.md)
- [Stack detector](scripts/detect_stack.py)
- [Report validator](scripts/validate_report.py)
