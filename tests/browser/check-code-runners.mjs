/** Run the real worker/iframe checks against a built author guide.
 * node tests/browser/check-code-runners.mjs /tmp/touchbook-html [guide-page-url]
 * CHROME_PATH may override the Chromium/Brave executable.
 * Requires Node.js with built-in WebSocket support; no test dependency install.
 */
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { dirname, extname, resolve, sep } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { setTimeout as delay } from "node:timers/promises";

const root = resolve(process.argv[2] || "/tmp/tb-code-runners-html");
const fixture = await readFile(resolve(dirname(fileURLToPath(import.meta.url)), "tb-code.html"));
const misses = [];
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    if (pathname === "/project/nested/examples/runner-check.html") {
      response.writeHead(200, { "Content-Type": "text/html" });
      response.end(fixture);
      return;
    }
    if (!pathname.startsWith("/project/")) throw new Error("Outside fixture root");
    const path = resolve(root, pathname.slice("/project/".length));
    if (!path.startsWith(root + sep)) throw new Error("Outside fixture root");
    const content = await readFile(path);
    response.writeHead(200, { "Content-Type": {
      ".js": "text/javascript", ".html": "text/html", ".wasm": "application/wasm",
      ".css": "text/css",
    }[extname(path)] || "application/octet-stream" });
    response.end(content);
  } catch {
    misses.push(request.url);
    response.writeHead(404);
    response.end("Not found");
  }
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const profile = await mkdtemp(resolve(tmpdir(), "tb-code-browser-"));
const executable = process.env.CHROME_PATH || "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser";
const child = spawn(executable, ["--headless", "--disable-gpu", "--no-first-run",
  "--no-default-browser-check", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank"],
{ stdio: ["ignore", "ignore", "pipe"] });
let browserLog = "";
child.stderr.on("data", chunk => { browserLog += chunk; });
child.on("error", error => { browserLog += error.message; });
let socket;
try {
  let port;
  for (let attempt = 0; attempt < 200; attempt++) {
    try { port = (await readFile(resolve(profile, "DevToolsActivePort"), "utf8")).split("\n")[0]; break; }
    catch { await delay(50); }
  }
  if (!port) throw new Error(`Browser did not start: ${browserLog}`);
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = targets.find(target => target.type === "page");
  socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });
  let serial = 0;
  const pending = new Map();
  socket.addEventListener("message", event => {
    const message = JSON.parse(event.data);
    const task = pending.get(message.id);
    if (!task) return;
    pending.delete(message.id);
    if (message.error) task.reject(new Error(message.error.message));
    else task.resolve(message.result);
  });
  const command = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++serial;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
  await command("Page.navigate", { url: `http://127.0.0.1:${server.address().port}/project/nested/examples/runner-check.html` });
  let result;
  for (let attempt = 0; attempt < 800; attempt++) {
    const evaluation = await command("Runtime.evaluate", { expression: "window.runnerCheck", returnByValue: true });
    result = evaluation.result.value;
    if (result && result.status !== "running") break;
    await delay(50);
  }
  if (result?.status !== "passed") {
    throw new Error(`${JSON.stringify(result)}\nMissing asset requests: ${misses.join(", ")}`);
  }
  if (misses.some(url => /jobe|discover|_static/.test(url))) {
    throw new Error(`Unexpected requests: ${misses.join(", ")}`);
  }
  // Exercise Sphinx's script tags and the real theme as well as the isolated
  // runner fixture. In particular, a broken module entry point hides all UI.
  const guideUrl = process.argv[3]
    || `http://127.0.0.1:${server.address().port}/project/components/tb-code.html`;
  await command("Page.navigate", { url: guideUrl });
  let guide;
  for (let attempt = 0; attempt < 200; attempt++) {
    const evaluation = await command("Runtime.evaluate", {
      expression: `(() => {
        const blocks = [...document.querySelectorAll('tb-code')];
        return { count: blocks.length, ready: blocks.length > 0 && blocks.every(block =>
          block.querySelector('.tb-code__controls') &&
          block.querySelector('.tb-code__editor') &&
          block.querySelector('.tb-code__controls button')) };
      })()`,
      returnByValue: true,
    });
    guide = evaluation.result.value;
    if (guide?.ready) break;
    await delay(50);
  }
  if (!guide?.ready) throw new Error(`Generated guide controls failed: ${JSON.stringify(guide)}`);
  result.passed.push(`Generated author guide: ${guide.count} tb-code blocks initialized`);
  console.log(JSON.stringify(result, null, 2));
} finally {
  socket?.close();
  child.kill("SIGTERM");
  await new Promise(resolve => server.close(resolve));
  await Promise.race([new Promise(resolve => child.once("exit", resolve)), delay(2000)]);
  await rm(profile, { recursive: true, force: true });
}
