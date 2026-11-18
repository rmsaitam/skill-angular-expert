# Jest unit tests with jest-preset-angular

Unit tests must be fast, isolated and honest about the Angular environment. Use the runner detected by `scripts/detect_stack.py`; if Karma or Vitest is already configured, keep it and ask before switching to Jest.

## Required configuration

When the project has no Jest setup, add these files after confirming the runner choice.

`jest.config.js`:

```javascript
module.exports = {
  preset: 'jest-preset-angular',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setup-jest.ts'],
  moduleNameMapper: {
    '^@app/(.*)$': '<rootDir>/src/app/$1',
  },
  collectCoverageFrom: [
    'src/app/**/*.ts',
    '!src/app/**/*.spec.ts',
    '!src/app/**/*.module.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

`setup-jest.ts` for a zone-based application:

```typescript
import { setupZoneTestEnv } from 'jest-preset-angular/setup-env/zone';

setupZoneTestEnv();
```

`setup-jest.ts` for a zoneless application on v20.2+:

```typescript
import { setupZonelessTestEnv } from 'jest-preset-angular/setup-env/zoneless';

setupZonelessTestEnv();
```

The setup function must be called; a side-effect-only import does not initialize TestBed.

`tsconfig.spec.json`:

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": ["jest", "node"],
    "esModuleInterop": true
  },
  "include": ["src/**/*.spec.ts", "src/**/*.d.ts", "setup-jest.ts"]
}
```

Keep `strict` inherited from `tsconfig.json`; do not disable strict typing in specs. Ensure `setup-jest.ts` is listed in the `tsconfig.spec.json` includes and that `moduleNameMapper` mirrors the path aliases declared in `tsconfig.json`.

## Standalone component with TestBed

```typescript
import { TestBed } from '@angular/core/testing';
import { OrdersComponent } from './orders.component';
import { OrderService } from './order.service';

describe('OrdersComponent', () => {
  const service = {
    orders: jest.fn(() => [{ id: 1, reference: 'A-100' }]),
    selectedId: jest.fn(() => null),
  };

  it('renders the orders returned by the service', async () => {
    await TestBed.configureTestingModule({
      imports: [OrdersComponent],
      providers: [{ provide: OrderService, useValue: service }],
    }).compileComponents();

    const fixture = TestBed.createComponent(OrdersComponent);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelectorAll('li')[0].textContent).toContain('A-100');
    expect(service.orders).toHaveBeenCalled();
  });

  it('renders an empty state when no orders exist', async () => {
    service.orders.mockReturnValue([]);

    await TestBed.configureTestingModule({
      imports: [OrdersComponent],
      providers: [{ provide: OrderService, useValue: service }],
    }).compileComponents();

    const fixture = TestBed.createComponent(OrdersComponent);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('No orders available.');
  });
});
```

For NgModule components, declare the component in `declarations` and import the module's dependencies instead of using `imports` for the component itself.

## Service with mocked HttpClient

```typescript
import { HttpClient, provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { throwError } from 'rxjs';
import { OrderService } from './order.service';

describe('OrderService', () => {
  let service: OrderService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [OrderService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(OrderService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads orders into the exposed signal state', () => {
    service.load();
    const request = httpMock.expectOne('/api/orders');
    expect(request.request.method).toBe('GET');
    request.flush([{ id: 1, reference: 'A-100' }]);
    expect(service.orders()).toEqual([{ id: 1, reference: 'A-100' }]);
  });

  it('maps a failure through the service boundary', () => {
    const http = TestBed.inject(HttpClient);
    jest.spyOn(http, 'get').mockReturnValue(throwError(() => new Error('offline')));

    service.load();
    expect(service.orders()).toEqual([]);
  });

  it('rejects an empty list without changing the selection', () => {
    service.load();
    httpMock.expectOne('/api/orders').flush([]);
    expect(service.orders()).toEqual([]);
    expect(service.selectedId()).toBeNull();
  });
});
```

Replace the mocked `HttpClient` with a plain object such as `{ get: jest.fn(() => of([])) }` when the project already uses that style.

## Pipe and pure functions

```typescript
import { ReferencePipe } from './reference.pipe';

describe('ReferencePipe', () => {
  const pipe = new ReferencePipe();

  it('formats a valid reference', () => {
    expect(pipe.transform('a100')).toBe('A-100');
  });

  it('rejects an invalid reference', () => {
    expect(() => pipe.transform('')).toThrow();
  });
});
```

## Signals and zoneless TestBed

```typescript
import { Component, provideZonelessChangeDetection, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';

@Component({
  selector: 'app-counter',
  template: `<span>{{ count() }}</span>`,
})
class CounterComponent {
  readonly count = signal(1);
}

describe('CounterComponent', () => {
  it('updates rendered state on a signal change', async () => {
    await TestBed.configureTestingModule({
      imports: [CounterComponent],
      providers: [provideZonelessChangeDetection()],
    }).compileComponents();

    const fixture = TestBed.createComponent(CounterComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('1');

    fixture.componentInstance.count.set(2);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('2');
  });
});
```

Use the zoneless TestBed provider for v20.2+ when the production application uses zoneless change detection; on v21+ rely on the default. Keep assertions focused on rendered state or emitted values.

## Mocking rules

- Use `jest.mock()` for module-level doubles and `jest.spyOn()` for focused collaborator checks.
- Restore spies in `afterEach()` when a spy is not scoped to a fresh TestBed instance.
- Assert observable outcomes; verify interactions only at boundaries such as HTTP, storage or logging.
- Cover success, validation and error paths for each changed behavior.
- Keep unit tests free of browser E2E tools and real network calls.

## Coverage and commands

```bash
npx jest --coverage
npx jest --coverage --runInBand
npx jest --coverage --config jest.config.js
npx jest --coverage --collectCoverageFrom='src/app/**/*.ts'
npx jest --coverage --coverageReporters=text-summary
```

The gate is 80% for branches, functions, lines and statements. Record the measured value from the actual run; never lower the threshold or exclude changed files to pass. Use the project's configured script when one exists and record the exact command in the artifact.
