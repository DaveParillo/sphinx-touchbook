/** Browser runs are deliberately bounded and do not retain execution state. */
export const RUN_TIMEOUT_MS = 10000;
export const MAX_OUTPUT_BYTES = 1000000;
export const MAX_ROWS = 1000;
export const MAX_MESSAGES = 1000;
export const MAX_STATEMENTS = 100;
export const MAX_DATABASE_BYTES = 16 * 1024 * 1024;
export const MAX_SQLITE_HEAP_BYTES = 64 * 1024 * 1024;

export function validateBrowserRequest(request, { database = false } = {}) {
  if (Object.hasOwn(request, "input") || Object.keys(request.parameters || {}).length) {
    throw new Error("Browser runs do not accept standard input or execution arguments.");
  }
  const files = request.files || [];
  if (database) {
    if (files.length > 1 || files.some((file) => file.encoding !== "base64")) {
      throw new Error("SQLite accepts one binary database attachment, or no attachments.");
    }
  } else if (files.length) {
    throw new Error("HTML and browser JavaScript do not support file attachments.");
  }
}
