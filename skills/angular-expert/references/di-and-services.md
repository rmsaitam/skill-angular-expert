# Dependency injection and services

Match the injection style already present in the repository. Modern Angular code uses `inject()`; legacy code uses constructor injection. Both are valid when they align with the detected version and local conventions.

## Root-provided services

Use `providedIn: 'root'` for stateless or application-wide services. It lets Angular tree-shake the service and avoids duplicate instances from repeated module providers.

```typescript
import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Order } from './order.model';

@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly http = inject(HttpClient);

  load() {
    return this.http.get<readonly Order[]>('/api/orders');
  }
}
```

Legacy constructor style:

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import type { Order } from './order.model';

@Injectable({ providedIn: 'root' })
export class OrderService {
  constructor(private readonly http: HttpClient) {}

  load() {
    return this.http.get<readonly Order[]>('/api/orders');
  }
}
```

## inject() versus constructor injection

- Use `inject()` in fields or factory functions of modern components, services, guards and interceptors.
- Use constructor injection in legacy classes and when the codebase consistently follows that style.
- Call `inject()` in an injection context; for deferred contexts pass an explicit `Injector` or use `runInInjectionContext()`.
- Keep collaborators `readonly` so they cannot be reassigned.

## Provider scopes

| Scope | Use when |
| --- | --- |
| `providedIn: 'platform'` | A singleton shared by all applications on the same platform. |
| `providedIn: 'root'` | The default shared application instance; the usual choice for services. |
| Component `providers: [MyService]` | A separate instance per component subtree, such as per-widget state; `providedIn` has no `'component'` value. |
| Lazy-loaded route providers | A service scoped to one feature and its child routes. |

Do not list a `providedIn: 'root'` service again in a module or component provider array unless a distinct scope is intentional and recorded in the design.

## HttpClient and interceptor hierarchy

Register `HttpClient` once with `provideHttpClient(withInterceptors([...]))` at the root, or with `withFetch()` where the project uses the fetch backend. Functional interceptors run in the order they are registered; use `withInterceptorsFromDi()` only for legacy class-based interceptors already present.

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './auth.interceptor';
import { loggingInterceptor } from './logging.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptors([authInterceptor, loggingInterceptor])),
  ],
};
```

`provideZoneChangeDetection()` is for zone-based applications only; on v21+ zoneless is the default and that provider must not reintroduce ZoneJS behavior.

## Rules

- Keep components free of HTTP calls; delegate to a service.
- Do not create a second instance through duplicated providers.
- Keep provider scope deliberate, especially for stateful services and interceptors.
- Inject abstract tokens or interfaces through `InjectionToken` when the project already uses them; avoid ad hoc service locators.
- Do not add a DI library or facade without an explicit need.
