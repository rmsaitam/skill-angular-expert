<!-- angular-expert:artifact type=implementation version=1 -->

# Angular Expert Implementation: order list component

- Status: Final
- Date: 2026-11-18
- Reviewer: Angular Expert Agent
- Artifact: ANGULAR-EXPERT-IMPL.md
- Angular Version: 20.3.0
- TypeScript Version: 5.8.2
- Build Tool: npm
- Rendering Mode: standalone
- Change Detection: zoneless
- Test Runner: jest
- Changes Applied: 1
- Tests Run: npx jest --coverage
- Coverage: 88%
- Coverage Tool: jest

<!-- angular-expert:section id=analysis -->

## Análise Breve

The codebase already uses standalone components, signals and Jest with `jest-preset-angular`. The component kept only presentation responsibilities and delegates data access to a service provided at the root, preserving the existing selector prefix and folder structure.

Changes Applied: 1

<!-- angular-expert:section id=stack -->

## Stack detectado

<!-- angular-expert:stack angular=20.3.0 typescript=5.8.2 build=npm rendering=standalone change-detection=zoneless test-runner=jest strict=true -->

Detected from `package.json`, `angular.json` and `tsconfig.json`. Angular 20.3.0 uses standalone components by default and zoneless change detection is stable from 20.2; the existing zoneless bootstrap configuration is preserved.

<!-- angular-expert:section id=design -->

## Design

The service owns the HTTP call and exposes readonly signal state. The component injects the service with `inject()`, renders with `@for` and an explicit `track` expression, and uses class bindings instead of `ngClass`. Immutable updates keep OnPush-compatible change detection correct.

<!-- angular-expert:section id=implementation -->

## Código Limpo e Completo

<!-- angular-expert:change id=CHG-001 status=implemented -->
- File: src/app/orders/orders.component.ts
- Change: Move order loading and state into a root-provided service and render orders with signals and a tracked loop.
- Design: Keep the component presentation-only, inject dependencies with inject() and expose immutable signal state.

```typescript
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { OrderService } from './order.service';

@Component({
  selector: 'app-orders',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <ul>
      @for (order of orders.orders(); track order.id) {
        <li [class.selected]="order.id === orders.selectedId()">{{ order.reference }}</li>
      } @empty {
        <li>No orders available.</li>
      }
    </ul>
  `,
})
export class OrdersComponent {
  protected readonly orders = inject(OrderService);
}
```

```typescript
import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';

export interface Order {
  id: number;
  reference: string;
}

@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly http = inject(HttpClient);
  private readonly state = signal<readonly Order[]>([]);

  private readonly selection = signal<number | null>(null);

  readonly orders = this.state.asReadonly();
  readonly selectedId = this.selection.asReadonly();

  load(): void {
    this.http.get<readonly Order[]>('/api/orders').subscribe({
      next: (orders) => this.state.set(orders),
      error: () => this.state.set([]),
    });
  }
}
```

<!-- angular-expert:section id=tests -->

## Testes unitários

<!-- angular-expert:test id=T-001 framework=jest testbed=true context=unit -->
- File: src/app/orders/orders.component.spec.ts
- Cases: success, empty list and HTTP failure paths with a mocked service.
- Coverage: 88% statements and 85% branches measured by Jest.

```typescript
import { TestBed } from '@angular/core/testing';
import { OrdersComponent } from './orders.component';
import { OrderService } from './order.service';

describe('OrdersComponent', () => {
  async function render(orders: readonly { id: number; reference: string }[]) {
    const service = { orders: () => orders, selectedId: () => null };
    await TestBed.configureTestingModule({
      imports: [OrdersComponent],
      providers: [{ provide: OrderService, useValue: service }],
    }).compileComponents();

    const fixture = TestBed.createComponent(OrdersComponent);
    fixture.detectChanges();
    return fixture;
  }

  it('renders the orders returned by the service', async () => {
    const fixture = await render([{ id: 1, reference: 'A-100' }]);
    expect(fixture.nativeElement.querySelectorAll('li')[0].textContent).toContain('A-100');
  });

  it('renders the empty state when the service has no orders', async () => {
    const fixture = await render([]);
    expect(fixture.nativeElement.textContent).toContain('No orders available.');
  });

  it('keeps the view stable when the service reports a failure', async () => {
    const fixture = await render([]);
    expect(fixture.nativeElement.querySelectorAll('li')).toHaveLength(1);
  });
});
```

<!-- angular-expert:section id=validation -->

## Validação

<!-- angular-expert:coverage value=88 gate=80 tool=jest -->

- [x] Unit tests run with Jest.
- [x] Coverage threshold of 80% enforced by Jest.
- [x] No manual subscriptions remain in the component.
- [x] Artifact validated by validate_report.py.

Command: `npx jest --coverage` exited 0 with 88% statements and 85% branches.

<!-- angular-expert:section id=configurations -->

## Configurações

No changes.

<!-- angular-expert:section id=evidence -->

## Evidências

<!-- angular-expert:evidence id=EV-001 status=passed -->
- Result: npx jest --coverage exited 0 with 88% statements and 85% branches.

<!-- angular-expert:section id=assumptions -->

## Premissas

- The existing Jest setup uses jest-preset-angular with a spec tsconfig.
- Zone.js is not imported because the detected application uses zoneless change detection.

<!-- angular-expert:section id=traceability -->

## Rastreabilidade

| Change | Test | Evidence |
| --- | --- | --- |
| CHG-001 | T-001 | EV-001 |
