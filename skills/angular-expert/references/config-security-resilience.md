# Configuration, security and resilience

## Configuration

Use `environment.ts` and `environment.prod.ts` for build-time values selected by `angular.json` file replacements. Use a runtime configuration fetched at bootstrap when values must change without rebuilding. Keep the runtime loader in a root-provided service and expose readonly state.

```typescript
export interface AppConfig {
  apiBaseUrl: string;
  page_size: number;
}
```

`strict` TypeScript settings and strict templates must stay enabled; narrow unknown runtime values before use instead of asserting a type without validation.

## Secrets

- Never put passwords, tokens, API keys or fixed environment URLs in TypeScript, templates, tests or the artifact.
- Reference secrets through build-time or runtime injection points and report keys only.
- Redact accidental values as `[REDACTED]` and report the exposure as a risk.
- The detector emits configuration keys only; never paste raw environment files into the artifact.

## Sanitization and XSS

Angular sanitizes untrusted values in interpolations, property bindings and attribute bindings. Keep values in bindings and avoid constructing HTML from user input. A `bypassSecurityTrust...` call through `DomSanitizer` disables protection: use it only for values from a trusted source after explicit validation, and record the reason.

- Validate URLs and resource URLs against an allowlist before binding them to `src`, `href` or `iframe`.
- Prefer `[ngStyle]` with plain objects or class bindings over trusted style strings.
- Sanitize rich text on the server or with a reviewed parser before rendering it.
- Treat query parameters, route fragments and `document` values as untrusted input.

## Images and assets

Use `NgOptimizedImage` for critical images with explicit width and height, set `loading="lazy"` for offscreen images where appropriate, and keep remote image hosts in the project's allowlist. Avoid dynamic resource URLs assembled from untrusted input.

## Lazy loading and resilience

Load feature areas with lazy routes; keep guards and resolvers small and delegate to services. For external HTTP calls, reuse the project's timeout, retry or error-reporting approach rather than adding a new resilience library for one change. Preserve cancellation semantics by using operators that unsubscribe from stale requests.

## Accessibility

Use semantic elements, associate labels with controls, provide text alternatives, maintain a logical heading order and add ARIA attributes only when native semantics are insufficient. Keep focus visible, support keyboard interaction for custom controls, and announce async state changes with a live region where the project already uses one.

## CSP and CORS notes

- Content Security Policy often blocks inline styles, scripts and eval; keep templates, styles and scripts in project-managed files and align with the deployed policy.
- CORS is a server concern: do not add proxy or header workarounds in the client without confirming the API contract.
- Report required CSP or CORS configuration keys in the **Configurações** section without including secrets.
- Keep styles encapsulated; use `ViewEncapsulation.None` only with a documented project-wide reason.
