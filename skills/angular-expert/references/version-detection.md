# Stack detection

This gate is mandatory and blocking. Run it before reading source code for the purpose of proposing or applying a change.

```bash
python3 scripts/detect_stack.py <project-root> --output stack.json
```

The detector output is authoritative. Convert it into the artifact stack marker without adding values from memory.

## What the detector reads

| Source | Extracted values |
| --- | --- |
| `package.json` | `@angular/core`, `@angular/cli`, `typescript` and `rxjs` versions; `zone.js`, `@angular/material`, Jest, `ts-jest`, `jest-preset-angular`, Karma, Jasmine and Vitest indicators |
| `angular.json` | Build and test builder names, `ssr` flag and the `@schematics/angular:component.standalone` default |
| `tsconfig.json` | `compilerOptions.strict`, `baseUrl` and `paths` aliases; JSON comments are tolerated |
| `nx.json` | Presence of an Nx workspace; sets `buildTool` to `nx` |
| `environment*.ts` and other TypeScript config files | Configuration keys only; values are never emitted |

`package.json` is the preferred descriptor. `angular.json` alone is accepted but does not contain versions, so a missing Angular version becomes a blocker.

A detected dependency name alone does not enable an API. Cross-check the Angular major version and the official guide for that major before using a version-gated feature.

## Emitted JSON fields

- `projectRoot`, `descriptor`, `buildTool`: `npm` or `nx`; the descriptor used and the detected workspace tool.
- `angular.version` and `angular.major`: declared Angular version and major line.
- `typescript.version` and `rxjs.version`: declared versions when available.
- `rendering`: `standalone`, `ngmodule`, `mixed` or `unknown`, from the Angular major, the schematic default and source NgModule evidence.
- `changeDetection`: `zoneless`, `zone`, `mixed` or `unknown`, from `zone.js`, `provideZonelessChangeDetection()` and the Angular major.
- `testRunner`: `jest`, `karma`, `vitest`, `mixed` or `unknown`.
- `strict`: boolean from `compilerOptions.strict`.
- `capabilities`: booleans for `jest`, `testbed`, `signals`, `ssr`, `zoneless` and `material`.
- `configKeys`: sorted, unique configuration keys without values.
- `warnings` and `blockers`: objects with `code`, `message` and `source`.

These fields map directly to the artifact marker: `angular`, `typescript`, `build`, `rendering`, `change-detection`, `test-runner` and `strict`.

## Stop conditions

1. No `package.json` or `angular.json`: ask the user for a descriptor or the exact Angular and TypeScript versions. Do not continue in the same turn.
2. Missing or unparseable Angular version: report the exact file and field that is missing. Do not guess.
3. Conflicting Angular majors across dependencies: ask which source is authoritative before proposing code.
4. Missing strict flag: ask before applying strictness changes; never silently flip `strict`.
5. Unsupported Angular v2-v19: recorded as a warning; report the constraint and do not propose an upgrade unless the user asks.

## Test-runner detection

| Indicators | Interpretation |
| --- | --- |
| `jest`, `jest-preset-angular`, `ts-jest`, Jest builder in `angular.json` | Jest runner; use TestBed and the existing preset setup. |
| `@angular-devkit/build-angular:karma`, `karma`, `jasmine-core` | Karma runner; keep it and ask before switching. |
| `vitest`, Vitest builder in `angular.json` | Vitest runner; keep it and ask before switching. |
| More than one runner | Reported as `mixed` with a `mixed-test-runners` warning; ask which runner is authoritative. |

## Exit codes

`0` on success, `1` in `--strict` mode when warnings exist, `2` for a configuration error or blockers, and `3` for a parse error. Use `--json` to print the report to stdout and `--output PATH` to write it to a file.

## Security boundary

The detector reads configuration keys only. It never emits values that look like passwords, tokens, API keys or URLs with embedded credentials. Feed its JSON into the report; never paste raw configuration files into the artifact. Redact accidental values as `[REDACTED]`.
