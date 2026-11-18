# Angular Expert

[![skills.sh](https://skills.sh/b/rmsaitam/skill-angular-expert)](https://skills.sh/rmsaitam/skill-angular-expert)

A version-aware Angular and TypeScript implementation skill for coding agents. Before suggesting any dependency, API or configuration, the skill inspects `package.json`, `angular.json` and `tsconfig.json` to identify the exact Angular version, TypeScript version, build tool and installed packages. If no manifest is available, it stops and asks for the manifest or the versions instead of guessing.

The skill follows the conventions already present in the codebase and the official Angular guides. It prefers standalone components, `inject()`, signals, immutable state, `OnPush` change detection and zoneless support when the detected version allows it, respects the existing RxJS and test conventions, and writes Jest unit tests with `jest-preset-angular` under an 80% coverage gate.

## Supported agents

| Agent | Manifest |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json` |
| Codex | `.codex-plugin/plugin.json` |
| Cursor | `.cursor-plugin/plugin.json` |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` |
| Antigravity | `plugin.json` |
| skills.sh / generic Agent Skills | `skills/angular-expert/SKILL.md` |

## Install

```bash
npx skills add rmsaitam/skill-angular-expert
npx skills add rmsaitam/skill-angular-expert -g -y
npx skills add rmsaitam/skill-angular-expert --list
```

Claude Code:

```text
/plugin marketplace add rmsaitam/skill-angular-expert
/plugin install angular-expert
```

Manual install for generic Agent Skills:

```bash
mkdir -p ~/.agents/skills
cp -R skills/angular-expert ~/.agents/skills/angular-expert
python3 scripts/validate_plugin.py .
```

## What it does

1. Runs `detect_stack.py` to produce a normalized stack report: Angular version, TypeScript version, build tool, rendering mode, change detection mode, test runner and available test dependencies.
2. Loads repository standards and mirrors existing folder, component, service, state and test patterns.
3. Implements the change with the correct standalone or module setup, version-appropriate APIs, signals, `OnPush` and zoneless behavior when supported.
4. Adds isolated Jest unit tests using `jest-preset-angular` when Jest is the configured runner, and checks coverage against the 80% gate.
5. Writes and validates a traceable `ANGULAR-EXPERT-IMPL.md` artifact with `validate_report.py`.

The final answer always follows this format: **Análise Breve**, **Código Limpo e Completo**, **Configurações**.

## Artifact markers

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
```

## Development

```bash
make test        # run the test suite
make coverage    # run tests with an 80% coverage gate
make validate    # validate the plugin structure
make check       # coverage plus plugin validation
```

The executable test suite of this plugin uses pytest and covers `detect_stack.py`, `validate_report.py` and `validate_plugin.py`. The generated Angular code contract requires Jest unit tests with `jest-preset-angular` and 80% coverage in the target codebase.

## Official documentation

The `references/official-docs.md` file maps each rule to the official Angular guides for components, signals, dependency injection, change detection, RxJS and testing.

## License

MIT
