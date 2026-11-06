/** Deadlines and cancellation shared by the execution adapters. */
export function withAbort(promise, signal) {
  if (!signal) return promise;
  if (signal.aborted) return Promise.reject(new DOMException("Run cancelled.", "AbortError"));
  return new Promise((resolve, reject) => {
    const abort = () => reject(new DOMException("Run cancelled.", "AbortError"));
    signal.addEventListener("abort", abort, { once: true });
    Promise.resolve(promise).then(resolve, reject).finally(() => {
      signal.removeEventListener("abort", abort);
    });
  });
}

export async function fetchWithTimeout(
  url, options, timeoutMs, signal, readResponse = (response) => response,
) {
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener("abort", abort, { once: true });
  if (signal?.aborted) controller.abort();
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);
  try {
    const pending = fetch(url, { ...options, signal: controller.signal }).then(readResponse);
    return await withAbort(pending, controller.signal);
  } catch (error) {
    if (timedOut) throw new Error("Execution request timed out.");
    throw error;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", abort);
  }
}
