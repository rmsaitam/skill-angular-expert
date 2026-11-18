# Change detection model

Angular schedules checks differently depending on the detected version and the application provider setup. The detector decides whether the application is zone-based or zoneless.

## Zone-based versus zoneless

- Zone-based applications import `zone.js` and rely on ZoneJS notifications to trigger change detection.
- Zoneless applications schedule checks through Angular APIs. From v20.2, add `provideZonelessChangeDetection()` at bootstrap when zoneless is chosen.
- Zoneless is the default from v21+; do not use `provideZoneChangeDetection()` to override that default.
- Match the production setup in TestBed for v20+ so tests observe the same scheduling behavior.

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { provideZonelessChangeDetection } from '@angular/core';
import { AppComponent } from './app.component';

bootstrapApplication(AppComponent, {
  providers: [provideZonelessChangeDetection()],
});
```

## OnPush semantics

With `ChangeDetectionStrategy.OnPush`, a component is checked when an input reference changes, an event originates in its template, a signal it reads changes, an observable piped through the async pipe emits, or `markForCheck()` is called. OnPush requires immutable updates: replace arrays and objects instead of mutating them.

On v22+ standalone and OnPush are implicit defaults, so do not set `standalone: true` or `changeDetection: OnPush` explicitly. On earlier versions keep the project's existing metadata style.

```typescript
import { ChangeDetectionStrategy, Component, computed, input, signal } from '@angular/core';
import type { Order } from './order.model';

@Component({
  selector: 'app-order-list',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>{{ summary() }}</p>
    @for (order of orders(); track order.id) {
      <span [class.selected]="order.id === selected()">{{ order.reference }}</span>
    }
  `,
})
export class OrderListComponent {
  readonly orders = input.required<readonly Order[]>();
  private readonly selected = signal<number | null>(null);
  readonly summary = computed(() => `${this.orders().length} orders`);
}
```

## Signals and computed values

Use `signal()` for mutable state owned by a service or component, expose `asReadonly()` to consumers, and derive view data with `computed()`. Signals notify templates and OnPush components without manual change-detection calls.

## Async pipe and toSignal

Prefer the async pipe or `toSignal()` in components instead of manual subscriptions. `toSignal()` needs an injection context or an explicit injector, and it requires an initial value when the source may emit later:

```typescript
import { inject, Component } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { OrderService } from './order.service';

@Component({
  selector: 'app-orders',
  template: `<span>{{ orders().length }}</span>`,
})
export class OrdersComponent {
  private readonly service = inject(OrderService);
  readonly orders = toSignal(this.service.orders$, { initialValue: [] });
}
```

## Tracking and identity

Always use an explicit `track` expression with `@for` and `trackBy` with `*ngFor`. Stable identities prevent unnecessary DOM recreation and keep state such as focus and animations intact.

## Immutable inputs and ChangeDetectorRef

Replace data rather than mutating it in place. Use `ChangeDetectorRef.markForCheck()` only for values that Angular cannot observe, such as a field updated by a non-Angular callback; `detectChanges()` is reserved for narrow, proven cases and should not be routine.

## Templates without heavy work

Do not call methods that filter, sort, allocate or perform HTTP work from a template or a getter used in a template. Precompute with `computed()`, a pipe or a view model so each change-detection pass only reads a value.
