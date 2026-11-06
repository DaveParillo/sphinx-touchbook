import { MAX_MESSAGES, MAX_OUTPUT_BYTES } from "./limits.js";

// This function is serialized into the isolated preview, not executed here.
function previewDiagnostics(channel, maxBytes, maxMessages) {
  let bytes = 0;
  let count = 0;
  let truncated = false;
  const send = (kind, text) => {
    if (truncated) return;
    text = String(text);
    bytes += new TextEncoder().encode(text).length;
    count += 1;
    if (bytes > maxBytes || count > maxMessages) {
      truncated = true;
      parent.postMessage({ channel, kind: "log", text: "Output truncated." }, "*");
      return;
    }
    parent.postMessage({ channel, kind, text }, "*");
  };
  for (const name of ["log", "info", "warn", "error", "debug"]) {
    console[name] = (...values) => send("log", values.map((value) => {
      if (typeof value === "string") return value;
      try { return JSON.stringify(value) ?? String(value); }
      catch { return String(value); }
    }).join(" "));
  }
  addEventListener("error", (event) => send("error", event.message));
  addEventListener("unhandledrejection", (event) => send("error", event.reason));
}

export function previewDocument(source, channel) {
  const doc = new DOMParser().parseFromString(source, "text/html");
  const policy = doc.createElement("meta");
  policy.httpEquiv = "Content-Security-Policy";
  policy.content = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'";
  const diagnostics = doc.createElement("script");
  diagnostics.textContent = `(${previewDiagnostics.toString()})(${JSON.stringify(channel)}, ${MAX_OUTPUT_BYTES}, ${MAX_MESSAGES});`;
  doc.head.prepend(policy, diagnostics);
  // Refresh directives are navigation, rather than preview content.
  for (const meta of doc.querySelectorAll("meta[http-equiv]")) {
    if (meta.httpEquiv.toLowerCase() === "refresh") meta.remove();
  }
  return `<!doctype html>\n${doc.documentElement.outerHTML}`;
}

export function renderHtml(container, result, { onStatus } = {}) {
  const frame = document.createElement("iframe");
  frame.className = "tb-code__preview";
  frame.title = "HTML preview";
  frame.setAttribute("sandbox", "allow-scripts");
  frame.referrerPolicy = "no-referrer";
  const channel = crypto.randomUUID();
  const consoleOutput = document.createElement("pre");
  consoleOutput.className = "tb-code__preview-console";
  consoleOutput.setAttribute("aria-label", "Preview console");
  consoleOutput.hidden = true;
  let bytes = 0;
  let messages = 0;
  const receive = (event) => {
    const data = event.data;
    if (event.source !== frame.contentWindow || !data || data.channel !== channel
        || !["log", "error"].includes(data.kind) || typeof data.text !== "string") return;
    bytes += new TextEncoder().encode(data.text).length;
    if (bytes > MAX_OUTPUT_BYTES || messages >= MAX_MESSAGES + 1) return;
    messages += 1;
    consoleOutput.hidden = false;
    consoleOutput.append(document.createTextNode(`${data.text}\n`));
    if (data.kind === "error") onStatus?.("Preview reported an error.");
  };
  window.addEventListener("message", receive);
  container.append(frame, consoleOutput);
  frame.srcdoc = previewDocument(result.source, channel);
  return () => {
    window.removeEventListener("message", receive);
    frame.remove();
  };
}
