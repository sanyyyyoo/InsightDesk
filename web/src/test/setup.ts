import "@testing-library/jest-dom/vitest";

// recharts' ResponsiveContainer needs ResizeObserver in jsdom
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
(globalThis as unknown as { ResizeObserver: typeof ResizeObserverStub }).ResizeObserver ??= ResizeObserverStub;
