import { RUN_TIMEOUT_MS } from "./limits.js";

/** One fresh worker per run, terminated on success, failure, Stop, or timeout. */
export function runWorker(url, request, { signal, timeoutMs = RUN_TIMEOUT_MS, type = "classic" } = {}) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException("Run cancelled.", "AbortError"));
      return;
    }
    let worker;
    let timer;
    const finish = (error, result) => {
      clearTimeout(timer);
      signal?.removeEventListener("abort", abort);
      worker?.terminate();
      if (error) reject(error);
      else resolve(result);
    };
    const abort = () => finish(new DOMException("Run cancelled.", "AbortError"));
    try {
      worker = new Worker(url, { type });
      worker.onmessage = ({ data }) => data.error
        ? finish(new Error(data.error)) : finish(null, data.result);
      worker.onerror = (event) => {
        event.preventDefault();
        finish(new Error(event.message || "Unable to load the execution worker."));
      };
      worker.onmessageerror = () => finish(new Error("Unable to read worker results."));
      signal?.addEventListener("abort", abort, { once: true });
      timer = setTimeout(() => finish(new Error("Execution timed out after 10 seconds.")), timeoutMs);
      worker.postMessage(request);
    } catch (error) {
      finish(error);
    }
  });
}
