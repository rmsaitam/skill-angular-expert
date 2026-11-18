# Codebase conventions

The detected stack defines what is legal; the codebase defines what is idiomatic. Read the following before designing a change:

- `CONTRIBUTING.md`, `CODING_STANDARDS.md`, `SECURITY.md` and `ARCHITECTURE.md`.
- ADRs under `docs/adr/`.
- ESLint, Prettier and stylelint configuration, plus the lint target in `angular.json`.
- `tsconfig.json` path aliases and strictness options.
- The existing Jest, Karma or Vitest configuration and the closest existing spec files.
- The closest existing component, service, interceptor, pipe, model and test for the area being changed.
- Recent approved commits touching the same folders.

## Capture these facts

| Topic | Question to answer |
| --- | --- |
| Folder layout | Where do components, services, state stores, models, pipes, interceptors and specs live? |
| Selector prefix | Which prefix is used in component and directive selectors? |
| Naming | Which suffixes are used for components, services, interceptors, pipes, models and specs? |
| Standalone vs NgModule | Are components standalone, declared in NgModules, or mixed? Where is bootstrap configured? |
| State management | Are values held in signals, RxJS subjects, a store library, or component fields? |
| UI library | Which component library, icon set and utility CSS classes are already in use? |
| DTO and model mapping | Are API shapes mapped in services, adapters or models, or bound directly? |
| Error handling | Are errors mapped in interceptors, services or components, and how are messages surfaced? |
| Tests | Which runner, naming convention, TestBed helpers and mocking style are used? |
| Styling | Are styles inline, in `.css`/`.scss` files, and which encapsulation and preprocessor are set? |

## Rules

- Copy the local style before introducing anything new.
- Keep the established selector prefix, folder layout and naming; do not reformat unrelated code.
- Do not introduce a state library, UI library, CSS framework or test runner unless the project already uses it or the user explicitly requests it.
- If the project exposes API shapes directly, do not silently add a mapper layer; mention it as a design option instead.
- If no local example exists, prefer the smallest official Angular pattern compatible with the detected version and record the assumption in the artifact.
