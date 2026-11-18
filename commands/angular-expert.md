---
description: Implement Angular changes using the detected project versions, official guides, codebase conventions, and Jest unit tests with an 80% coverage gate.
argument-hint: "[--project-root PATH] [--scope DESCRIPTION] [--output PATH]"
---

# Angular Expert

Invoke the `angular-expert` skill. The skill must first detect the stack; it must not suggest dependencies, APIs or code before that gate is complete.

## Instructions

- Run `python3 skills/angular-expert/scripts/detect_stack.py <project-root> --output stack.json` from the plugin repository root as the first action. If there is no `package.json` or `angular.json`, stop and ask for a descriptor or the exact Angular, TypeScript and Node versions.
- Use the detected Angular major version to decide standalone defaults, control-flow syntax, signal APIs and zoneless support. Do not mix APIs from different majors.
- Follow the existing folder layout, naming, selector prefix, formatting, state management and test style. Do not introduce a new library or architecture without an explicit need.
- Prefer standalone components, `inject()`, signals, immutable state, `ChangeDetectionStrategy.OnPush` and a zoneless provider only when the detected version and existing setup support them. Keep RxJS usage idiomatic and avoid manual subscriptions in components.
- Respect the existing test runner. When Jest is already configured, keep Jest and `jest-preset-angular` instead of switching to Karma or another framework. When another runner is in place, keep it and adapt the coverage configuration rather than replacing it without a stated need.
- Write isolated Jest unit tests with `jest-preset-angular` for the detected runner where applicable, enforce at least 80% coverage and record the exact commands and measured result.
- Write only `ANGULAR-EXPERT-IMPL.md` at the repository root unless the user supplies another path.
- Before finishing, validate the artifact:

  ```bash
  python3 skills/angular-expert/scripts/validate_report.py ANGULAR-EXPERT-IMPL.md
  ```

- Report the artifact path, detected Angular and TypeScript versions, main changes, test commands, measured coverage and remaining risks.
