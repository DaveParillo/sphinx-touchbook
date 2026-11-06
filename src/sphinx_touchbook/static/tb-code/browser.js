import { validateBrowserRequest } from "./limits.js";
import { runWorker } from "./worker.js";

export class BrowserRunner {
  constructor(config) {
    this.language = String(config.language || "").toLowerCase();
    if (!["javascript", "js", "html", "html5"].includes(this.language)) {
      throw new Error(`The browser runner does not support ${config.language}.`);
    }
  }

  async run(request, context) {
    validateBrowserRequest(request);
    if (["html", "html5"].includes(this.language)) {
      return { kind: "html", source: request.source, status: "Preview ready." };
    }
    context.onStatus("Running JavaScript...");
    return runWorker(new URL("javascript-worker.js", import.meta.url), request,
      { ...context, type: "module" });
  }
}
