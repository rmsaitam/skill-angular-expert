# State, HTTP and interceptors

Components stay thin. A service owns state, HTTP access and error mapping, then exposes readonly signals or observables for the view.

## Service-owned state with signals

```typescript
import { inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface Order {
  id: number;
  reference: string;
}

@Injectable({ providedIn: 'root' })
export class OrderStore {
  private readonly http = inject(HttpClient);
  private readonly items = signal<readonly Order[]>([]);
  readonly orders = this.items.asReadonly();

  load(): void {
    this.http.get<readonly Order[]>('/api/orders').subscribe({
      next: (items) => this.items.set(items),
      error: () => this.items.set([]),
    });
  }
}
```

Prefer an observable exposed by the service and `toSignal()` or the async pipe in the component when the view only consumes a stream. Keep writes private so consumers cannot mutate shared state.

## Flattening operators

Use the operator that matches the intended concurrency:

| Operator | Use when |
| --- | --- |
| `switchMap` | A new input should cancel the previous request, such as type-ahead search. |
| `mergeMap` | All inner requests should run and be kept, such as independent item updates. |
| `concatMap` | Inner requests must run in order, such as queued writes. |
| `exhaustMap` | Ignore new inputs while a request is running, such as form submission. |

```typescript
import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, of, Subject, switchMap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private readonly http = inject(HttpClient);
  private readonly query$ = new Subject<string>();

  readonly results$ = this.query$.pipe(
    switchMap((query) =>
      this.http.get<readonly string[]>('/api/search', { params: { query } }).pipe(
        catchError(() => of([] as readonly string[])),
      ),
    ),
  );

  search(query: string): void {
    this.query$.next(query);
  }
}
```

## Error handling and caching

Map HTTP failures at the service or interceptor boundary, expose an error signal or a typed error stream, and keep components free of catch blocks that duplicate logic. Cache with `shareReplay({ bufferSize: 1, refCount: true })` when multiple consumers need one request; avoid caching user-specific or secret-bearing responses without an invalidation policy.

## Interceptor order

Functional interceptors run in registration order. Place authentication or context headers before logging and retry logic so every outgoing request is decorated. Map errors in a dedicated interceptor only when the project already centralizes errors; otherwise keep mapping in the owning service.

## No nested subscriptions and no component subscriptions

Never subscribe inside another `subscribe()` callback; replace the nesting with `switchMap`, `mergeMap`, `concatMap` or `exhaustMap`. Components should read state through signals, the async pipe or `toSignal()`. When a component must subscribe to an event stream, clean it up:

```typescript
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { EventsService } from './events.service';

@Component({
  selector: 'app-events',
  template: `<span>{{ count() }}</span>`,
})
export class EventsComponent {
  private readonly events = inject(EventsService);
  private readonly destroyRef = inject(DestroyRef);
  readonly count = signal(0);

  constructor() {
    this.events.updates$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.count.update((value) => value + 1));
  }
}
```

Use `takeUntilDestroyed()` without an argument only inside an injection context; pass `DestroyRef` otherwise. Keep business logic in services, not in component subscription callbacks.
