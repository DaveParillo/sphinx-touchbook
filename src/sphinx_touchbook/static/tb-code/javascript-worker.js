import { MAX_MESSAGES, MAX_OUTPUT_BYTES } from "./limits.js";

/* Editable code never runs in the textbook's window. */
self.onmessage = async ({ data }) => {
  const lines = [];
  let length = 0;
  let truncated = false;
  const print = (...values) => {
    if (truncated) return;
    const line = values.map((value) => {
      if (typeof value === "string") return value;
      try { return JSON.stringify(value) ?? String(value); }
      catch { return String(value); }
    }).join(" ");
    length += new TextEncoder().encode(line).length + 1;
    if (length > MAX_OUTPUT_BYTES || lines.length >= MAX_MESSAGES) {
      truncated = true;
      return;
    }
    lines.push(line);
  };
  const output = { log: print, info: print, warn: print, error: print,
    debug: print, clear: () => { lines.length = 0; length = 0; } };
  // Capture both console.log and self.console.log, as well as asynchronous
  // errors that occur while the returned promise is still running.
  self.console = output;
  const send = (error) => {
    if (truncated) lines.push("Output truncated.");
    if (error) lines.push(String(error.message || error));
    self.postMessage({ result: { kind: "text",
      text: lines.join("\n") || "(no output)",
      status: error ? "Run failed." : "Run complete.",
    } });
    self.close();
  };
  self.addEventListener("error", (event) => {
    event.preventDefault();
    send(event.error || event.message);
  });
  self.addEventListener("unhandledrejection", (event) => {
    event.preventDefault();
    send(event.reason);
  });
  try {
    const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
    await new AsyncFunction("console", data.source)(output);
    send();
  } catch (error) {
    send(error);
  }
};
