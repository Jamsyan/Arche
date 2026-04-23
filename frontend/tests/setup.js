/**
 * Global test setup — runs before any test file.
 * Clears localStorage so dock.js doesn't load stale data.
 */
export function setup() {
  if (typeof globalThis.localStorage !== 'undefined') {
    globalThis.localStorage.clear()
  }
}
