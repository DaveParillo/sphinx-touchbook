import { validateBrowserRequest } from "./limits.js";
import { runWorker } from "./worker.js";

export class SqliteRunner {
  async run(request, context) {
    validateBrowserRequest(request, { database: true });
    context.onStatus("Running SQLite...");
    return runWorker(new URL("sqlite-worker.js", import.meta.url), request, context);
  }
}
