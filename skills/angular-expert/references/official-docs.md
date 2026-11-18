# Official documentation map

Consult these official angular.dev guides when a rule needs version-specific confirmation. They are the authority over memory or generic framework knowledge. Use the version selector on angular.dev so the page matches the version reported by the detector.

| Topic | Official guide |
| --- | --- |
| Angular style guide | https://angular.dev/style-guide |
| Components, inputs, outputs and lifecycle | https://angular.dev/guide/components |
| Dependency injection | https://angular.dev/guide/di |
| Signals, computed and effects | https://angular.dev/guide/signals |
| Templates, built-in control flow and bindings | https://angular.dev/guide/templates |
| Routing and lazy-loaded routes | https://angular.dev/guide/routing |
| Testing with TestBed | https://angular.dev/guide/testing |
| Zoneless change detection | https://angular.dev/guide/zoneless |
| Migration guides | https://angular.dev/reference/migrations |
| Release notes and version support | https://angular.dev/reference/releases |
| CLI configuration and builders | https://angular.dev/tools/cli |
| HTTP client and interceptors | https://angular.dev/guide/http |

For MCP-enabled agents, these Context7 IDs expose the same documentation:

- `/websites/angular_dev`: official angular.dev guides and API references.
- `/angular/angular-cli`: CLI workspace configuration, builders and generators.
- `/jestjs/jest`: Jest configuration, mocking and coverage options.
- `/thymikee/jest-preset-angular`: preset, environment setup and TestBed integration.

Check the documentation for the detected version before recommending `standalone`, NgModule declarations, `@if`, `@for`, `track`, `trackBy`, signals, `toSignal()`, `provideZonelessChangeDetection()` or test setup. Never migrate a codebase without an explicit request.
