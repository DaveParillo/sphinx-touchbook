import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { createRequire } from "node:module";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { executeSql } from "../../src/sphinx_touchbook/static/tb-code/sqlite-engine.js";
import { createRunner } from "../../src/sphinx_touchbook/static/tb-code/runners.js";
import { JobeRunner, interpretJobeResult } from "../../src/sphinx_touchbook/static/tb-code/jobe.js";
import { BrowserRunner } from "../../src/sphinx_touchbook/static/tb-code/browser.js";
import { SqliteRunner } from "../../src/sphinx_touchbook/static/tb-code/sqlite.js";
import { runWorker } from "../../src/sphinx_touchbook/static/tb-code/worker.js";
import { fetchWithTimeout } from "../../src/sphinx_touchbook/static/tb-code/transport.js";
import { renderOutput } from "../../src/sphinx_touchbook/static/tb-code/output.js";
import { MAX_ROWS } from "../../src/sphinx_touchbook/static/tb-code/limits.js";

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  document.body.replaceChildren();
});

describe("runner selection and JOBE interpretation", () => {
  it("keeps existing JavaScript on JOBE and selects browser runners explicitly", () => {
    expect(createRunner({ language: "js" })).toBeInstanceOf(JobeRunner);
    expect(createRunner({ language: "js", runner: "browser" })).toBeInstanceOf(BrowserRunner);
    expect(createRunner({ language: "html", runner: "browser" })).toBeInstanceOf(BrowserRunner);
    expect(createRunner({ language: "sql", runner: "browser" })).toBeInstanceOf(SqliteRunner);
    expect(() => createRunner({ runner: "unknown" })).toThrow("Unknown execution runner");
  });

  it("preserves program output, diagnostics, and non-success outcomes", () => {
    expect(interpretJobeResult({ outcome: 12, stdout: "out", stderr: "err", cmpinfo: "compile" }))
      .toEqual({ kind: "text", text: "out\nerr\ncompile", status: "Run finished with outcome 12." });
    expect(interpretJobeResult({ outcome: 15 }).text).toBe("(no output)");
  });

  it("does not contact JOBE for browser runs", async () => {
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);
    const runner = createRunner({ language: "html", runner: "browser", validateLanguage: true,
      endpoint: "https://example.test/runs", languagesEndpoint: "https://example.test/languages" });
    const result = await runner.run({ source: "<p>Hello</p>", parameters: {}, files: [] }, {});
    expect(result.kind).toBe("html");
    expect(fetch).not.toHaveBeenCalled();
  });

  it("rejects unsupported browser inputs instead of silently dropping them", async () => {
    const runner = new BrowserRunner({ language: "js" });
    await expect(runner.run({ source: "", input: "", files: [] }, {})).rejects.toThrow("standard input");
    await expect(runner.run({ source: "", files: [{ filename: "a.js" }] }, {})).rejects.toThrow("attachments");
    const sqlite = new SqliteRunner();
    await expect(sqlite.run({ source: "", files: [{ encoding: "text" }] }, {})).rejects.toThrow("binary database");
  });
});

describe("fresh workers and cancellation", () => {
  function mockWorker() {
    const workers = [];
    vi.stubGlobal("Worker", class {
      constructor(url) { this.url = url; this.terminate = vi.fn(); this.postMessage = vi.fn(); workers.push(this); }
    });
    return workers;
  }

  it("returns worker results and terminates the worker", async () => {
    const workers = mockWorker();
    const pending = runWorker("worker.js", { source: "SELECT 1;" });
    expect(workers[0].postMessage).toHaveBeenCalledWith({ source: "SELECT 1;" });
    workers[0].onmessage({ data: { result: { kind: "text", text: "1" } } });
    await expect(pending).resolves.toEqual({ kind: "text", text: "1" });
    expect(workers[0].terminate).toHaveBeenCalledOnce();
  });

  it("terminates and rejects on Stop", async () => {
    const workers = mockWorker();
    const controller = new AbortController();
    const pending = runWorker("worker.js", {}, { signal: controller.signal });
    controller.abort();
    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
    expect(workers[0].terminate).toHaveBeenCalledOnce();
  });

  it("terminates a worker that exceeds its deadline", async () => {
    vi.useFakeTimers();
    const workers = mockWorker();
    const pending = runWorker("worker.js", {});
    const rejection = expect(pending).rejects.toThrow("timed out");
    await vi.advanceTimersByTimeAsync(10000);
    await rejection;
    expect(workers[0].terminate).toHaveBeenCalledOnce();
  });

  it("surfaces worker errors and cleans up", async () => {
    const workers = mockWorker();
    const pending = runWorker("worker.js", {});
    workers[0].onmessage({ data: { error: "SQLite load failed" } });
    await expect(pending).rejects.toThrow("SQLite load failed");
    expect(workers[0].terminate).toHaveBeenCalledOnce();
  });

  it("keeps the JOBE deadline active while reading the response body", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", vi.fn(async () => ({ json: () => new Promise(() => {}) })));
    const pending = fetchWithTimeout("https://example.test", {}, 100, undefined, (response) => response.json());
    const rejection = expect(pending).rejects.toThrow("timed out");
    await vi.advanceTimersByTimeAsync(100);
    await rejection;
  });
});

describe("SQLite with the actual bundled engine", () => {
  let SQL;
  beforeAll(async () => {
    const root = resolve("src/sphinx_touchbook/static/tb-code/vendor");
    const init = createRequire(import.meta.url)(`${root}/sql-wasm.js`);
    SQL = await init({ wasmBinary: await readFile(`${root}/sql-wasm.wasm`) });
  });

  const run = (source, files = []) => executeSql(SQL, { source, files });

  it("executes multi-statement SQL and keeps semicolons inside strings", () => {
    const result = run("CREATE TABLE t(x); INSERT INTO t VALUES ('semi;colon'); SELECT * FROM t;");
    expect(result.status).toBe("Run complete.");
    expect(result.results).toEqual([{ columns: ["x"], values: [["semi;colon"]] }]);
  });

  it("supports triggers without splitting their bodies into separate statements", () => {
    const result = run("CREATE TABLE t(x); CREATE TABLE audit(x); CREATE TRIGGER log AFTER INSERT ON t BEGIN INSERT INTO audit VALUES (new.x); INSERT INTO audit VALUES ('logged'); END; INSERT INTO t VALUES ('one'); SELECT * FROM audit;");
    expect(result.results[0].values).toEqual([["one"], ["logged"]]);
  });

  it("retains empty-result headers, duplicate names, NULL, and exact large integers", () => {
    const result = run("SELECT 1 AS x, 2 AS x, NULL AS missing, 9223372036854775807 AS big; SELECT 1 AS empty WHERE 0;");
    expect(result.results).toEqual([
      { columns: ["x", "x", "missing", "big"], values: [[1, 2, null, "9223372036854775807"]] },
      { columns: ["empty"], values: [] },
    ]);
  });

  it("discards mutations between runs", () => {
    expect(run("CREATE TABLE fresh(x);").status).toBe("Run complete.");
    expect(run("SELECT * FROM fresh;").messages.join()).toContain("no such table");
  });

  it("starts from a fresh copy of an attached seed each run", () => {
    const seed = new SQL.Database();
    seed.run("CREATE TABLE t(x); INSERT INTO t VALUES (1);");
    const content = Buffer.from(seed.export()).toString("base64");
    seed.close();
    const files = [{ filename: "seed.db", encoding: "base64", content }];
    expect(run("UPDATE t SET x = 2; SELECT x FROM t;", files).results[0].values).toEqual([[2]]);
    expect(run("SELECT x FROM t;", files).results[0].values).toEqual([[1]]);
    expect(() => run("SELECT 1;", [{ content: btoa("not a database") }])).toThrow("not an SQLite database");
  });

  it("bounds collected rows and reports truncation", () => {
    const result = run("WITH RECURSIVE n(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM n WHERE x<2000) SELECT x FROM n;");
    expect(result.results[0].values).toHaveLength(MAX_ROWS);
    expect(result.status).toContain("truncated");
  });

  it("reports syntax errors with earlier results intact", () => {
    const result = run("SELECT 1 AS ok; NOT SQL;");
    expect(result.results[0].values).toEqual([[1]]);
    expect(result.status).toBe("Run failed.");
    expect(result.messages.join()).toContain("syntax error");
  });

  it("applies the SQLite allocation ceiling inside the engine", () => {
    const result = run("PRAGMA hard_heap_limit;");
    expect(result.results[0].values).toEqual([[67108864]]);
  });
});

describe("result rendering", () => {
  it("renders SQL values as text in accessible tables", () => {
    const container = document.createElement("div");
    renderOutput(container, { kind: "sql", results: [{ columns: ["<b>x</b>", "missing"],
      values: [["<img src=x onerror=alert(1)>", null]] }], messages: [] });
    expect(container.querySelector("caption").textContent).toContain("1 row");
    expect(container.querySelector("th").scope).toBe("col");
    expect(container.querySelector("th").textContent).toBe("<b>x</b>");
    expect(container.querySelectorAll("td")[1].textContent).toBe("NULL");
    expect(container.querySelector("img")).toBeNull();
  });

  it("creates an isolated preview and ignores messages from other windows", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("test-channel");
    const container = document.createElement("div");
    document.body.append(container);
    const status = vi.fn();
    const dispose = renderOutput(container, { kind: "html", source: "<p>hello</p><script>console.log('hello')</script>" }, { onStatus: status });
    const frame = container.querySelector("iframe");
    expect(frame.getAttribute("sandbox")).toBe("allow-scripts");
    expect(frame.title).toBe("HTML preview");
    expect(frame.srcdoc).toContain("Content-Security-Policy");
    const data = { channel: "test-channel", kind: "error", text: "example error" };
    window.dispatchEvent(new MessageEvent("message", { data, source: window }));
    expect(status).not.toHaveBeenCalled();
    window.dispatchEvent(new MessageEvent("message", { data, source: frame.contentWindow }));
    expect(status).toHaveBeenCalledWith("Preview reported an error.");
    expect(container.querySelector("pre").textContent).toContain("example error");
    dispose();
    expect(container.querySelector("iframe")).toBeNull();
  });
});
