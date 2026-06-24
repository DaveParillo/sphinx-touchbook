import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { change, click, input, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-code.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
  vi.restoreAllMocks();
  customElements.get("tb-code").languagesByEndpoint?.clear?.();
  customElements.get("tb-code").languagePreloadsByEndpoint?.clear?.();
});

function appendCode(config = {}) {
  const data = {
    language: "python",
    jobeLanguage: "python3",
    source: 'print("one")',
    endpoint: "https://example.test/runs/",
    languagesEndpoint: "https://example.test/languages",
    validateLanguage: false,
    stdin: "",
    parameters: {},
    editable: true,
    runLabel: "Run",
    editLabel: "Edit source",
    hideEditLabel: "Hide source",
    revisionLabel: "Source version",
    ...config,
  };
  const element = document.createElement("tb-code");
  element.id = "code-example";
  element.setAttribute("language", data.language);
  element.setAttribute("editable", String(data.editable));
  element.innerHTML = `
    <figure class="tb-code__fallback"><pre><code>${data.source}</code></pre></figure>
    <script type="application/json" class="tb-code__config">${JSON.stringify(data)}</script>
  `;
  document.body.appendChild(element);
  return element;
}

function appendSphinxHighlightedCode(config = {}) {
  const data = {
    language: "python",
    jobeLanguage: "python3",
    source: 'print("one")',
    endpoint: "https://example.test/runs/",
    languagesEndpoint: "https://example.test/languages",
    validateLanguage: false,
    stdin: "",
    parameters: {},
    editable: true,
    runLabel: "Run",
    editLabel: "Edit source",
    hideEditLabel: "Hide source",
    revisionLabel: "Source version",
    ...config,
  };
  const element = document.createElement("tb-code");
  element.id = "sphinx-code-example";
  element.setAttribute("language", data.language);
  element.setAttribute("editable", String(data.editable));
  element.innerHTML = `
    <figure class="tb-code__fallback">
      <div class="highlight"><pre><span></span><span class="nb">print</span><span class="p">(</span><span class="s2">&quot;one&quot;</span><span class="p">)</span></pre></div>
    </figure>
    <script type="application/json" class="tb-code__config">${JSON.stringify(data)}</script>
  `;
  document.body.appendChild(element);
  return element;
}

async function flushPromises() {
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
  await new Promise((resolve) => setTimeout(resolve, 0));
}

function codeButton(element, label) {
  return Array.from(element.querySelectorAll("button.tb-code__button"))
    .find((button) => button.textContent === label);
}

function runButton(element) {
  return codeButton(element, "Run");
}

function editButton(element) {
  return codeButton(element, "Edit source");
}

function tutorButton(element) {
  return Array.from(element.querySelectorAll("button.tb-code__button"))
    .find((button) => button.textContent.startsWith("Show in ") && button.textContent.endsWith(" Tutor"));
}

describe("tb-code Web Component", () => {
  it("enhances fallback code with run, edit, status, output, and source version controls", () => {
    const element = appendCode();
    const run = runButton(element);
    const edit = editButton(element);
    const tutor = tutorButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const revisionControl = element.querySelector(".tb-code__revision-control");
    const revisionLabel = element.querySelector("label.tb-code__revision-label");
    const revisionSlider = element.querySelector("input.tb-code__revision-slider");
    const revisionOutput = element.querySelector("output.tb-code__revision-output");
    const runtimeInputs = element.querySelector(".tb-code__runtime-inputs");
    const status = element.querySelector(".tb-code__status");
    const output = element.querySelector(".tb-code__output");

    expect(customElements.get("tb-code")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(run).toBeTruthy();
    expect(tutor.hidden).toBe(true);
    expect(tutor.textContent).toBe("Show in Python Tutor");
    expect(edit.textContent).toBe("Edit source");
    expect(edit.getAttribute("aria-expanded")).toBe("false");
    expect(edit.getAttribute("aria-controls")).toBe(editor.id);
    expect(editor.hidden).toBe(true);
    expect(revisionControl.hidden).toBe(true);
    expect(revisionLabel.textContent).toBe("Source version");
    expect(revisionSlider.type).toBe("range");
    expect(revisionSlider.min).toBe("1");
    expect(revisionSlider.max).toBe("1");
    expect(revisionOutput.value).toBe("1 of 1");
    expect(runtimeInputs.hidden).toBe(true);
    expect(status.getAttribute("role")).toBe("status");
    expect(status.getAttribute("aria-live")).toBe("polite");
    expect(output.getAttribute("aria-labelledby")).toBeTruthy();
  });

  it("toggles editor visibility and records source versions with the slider", () => {
    const element = appendCode();
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const revisionControl = element.querySelector(".tb-code__revision-control");
    const revisionSlider = element.querySelector("input.tb-code__revision-slider");
    const revisionOutput = element.querySelector("output.tb-code__revision-output");
    const status = element.querySelector(".tb-code__status");

    click(edit);
    expect(edit.textContent).toBe("Hide source");
    expect(edit.getAttribute("aria-expanded")).toBe("true");
    expect(editor.hidden).toBe(false);
    expect(revisionControl.hidden).toBe(true);

    editor.value = 'print("two")';
    input(editor);
    change(editor);
    expect(revisionControl.hidden).toBe(false);
    expect(revisionSlider.max).toBe("2");
    expect(revisionSlider.value).toBe("2");
    expect(revisionOutput.value).toBe("2 of 2");

    revisionSlider.value = "1";
    input(revisionSlider);
    expect(editor.value).toBe('print("one")');
    expect(revisionOutput.value).toBe("1 of 2");
    expect(status.textContent).toBe("Loaded source version 1.");

    click(edit);
    expect(edit.textContent).toBe("Edit source");
    expect(edit.getAttribute("aria-expanded")).toBe("false");
    expect(editor.hidden).toBe(true);
    expect(revisionControl.hidden).toBe(false);
  });

  it("keeps the source version slider hidden if only one version exists", () => {
    const element = appendCode();
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const revisionControl = element.querySelector(".tb-code__revision-control");
    const revisionSlider = element.querySelector("input.tb-code__revision-slider");

    click(edit);
    expect(editor.hidden).toBe(false);
    expect(revisionSlider.max).toBe("1");
    expect(revisionControl.hidden).toBe(true);

    click(edit);
    expect(editor.hidden).toBe(true);
    expect(revisionSlider.max).toBe("1");
    expect(revisionControl.hidden).toBe(true);
  });

  it("runs a selected source version after the editor is hidden", async () => {
    const fetchMock = vi.fn(async (url, options) => {
      const payload = JSON.parse(options.body);
      expect(payload.run_spec.sourcecode).toBe('print("one")');
      return {
        ok: true,
        json: async () => ({ outcome: 15, stdout: "one\n", stderr: "", cmpinfo: "" }),
      };
    });
    globalThis.fetch = fetchMock;

    const element = appendCode({ source: 'print("one")' });
    const run = runButton(element);
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const revisionControl = element.querySelector(".tb-code__revision-control");
    const revisionSlider = element.querySelector("input.tb-code__revision-slider");
    const displayedSource = element.querySelector(".tb-code__fallback code");

    click(edit);
    editor.value = 'print("two")';
    input(editor);
    click(edit);
    expect(editor.hidden).toBe(true);
    expect(revisionControl.hidden).toBe(false);
    expect(revisionSlider.max).toBe("2");

    revisionSlider.value = "1";
    input(revisionSlider);
    expect(displayedSource.textContent).toBe('print("one")');

    await click(run);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("renders editable stdin and runargs fields when those directive options are configured", () => {
    const element = appendCode({
      stdin: "Alice",
      parameters: { runargs: ["--count", "2"] },
    });
    const runtimeInputs = element.querySelector(".tb-code__runtime-inputs");
    const fields = Array.from(element.querySelectorAll(".tb-code__runtime-field"));
    const inputs = Array.from(element.querySelectorAll("input.tb-code__runtime-input"));

    expect(runtimeInputs.hidden).toBe(false);
    expect(fields).toHaveLength(2);
    expect(fields[0].querySelector("label").textContent).toBe("Standard input");
    expect(fields[1].querySelector("label").textContent).toBe("Run arguments");
    expect(inputs[0].value).toBe("Alice");
    expect(inputs[1].value).toBe("--count 2");
  });

  it("shows the Python Tutor button only for requested supported languages", () => {
    const python = appendCode({ showTutor: true, language: "python", jobeLanguage: "python3" });
    expect(tutorButton(python).hidden).toBe(false);
    expect(tutorButton(python).textContent).toBe("Show in Python Tutor");

    const cpp = appendCode({ showTutor: true, language: "c++", jobeLanguage: "cpp" });
    expect(tutorButton(cpp).hidden).toBe(false);
    expect(tutorButton(cpp).textContent).toBe("Show in C++ Tutor");

    const java = appendCode({ showTutor: true, language: "java", jobeLanguage: "java" });
    expect(tutorButton(java).hidden).toBe(false);
    expect(tutorButton(java).textContent).toBe("Show in Java Tutor");

    const ruby = appendCode({ showTutor: true, language: "ruby", jobeLanguage: "ruby" });
    expect(tutorButton(ruby).hidden).toBe(true);

    const notRequested = appendCode({ showTutor: false, language: "python", jobeLanguage: "python3" });
    expect(tutorButton(notRequested).hidden).toBe(true);
  });

  it("opens Python Tutor with the current execution source", () => {
    const openMock = vi.spyOn(window, "open").mockImplementation(() => null);
    const element = appendCode({
      language: "c++",
      jobeLanguage: "cpp",
      source: "int answer() { return 41; }",
      showTutor: true,
      runBefore: ["#include <iostream>"],
      runAfter: ["int main() { std::cout << answer(); }"],
    });
    const edit = editButton(element);
    const tutor = tutorButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");

    expect(tutor.hidden).toBe(false);
    expect(tutor.textContent).toBe("Show in C++ Tutor");
    expect(Array.from(element.querySelectorAll("button.tb-code__button")).map((button) => button.textContent)).toEqual([
      "Run",
      "Edit source",
      "Show in C++ Tutor",
    ]);

    click(edit);
    editor.value = "int answer() { return 42; }";
    input(editor);
    click(tutor);

    expect(openMock).toHaveBeenCalledOnce();
    const [url, target, features] = openMock.mock.calls[0];
    const params = new URLSearchParams(url.split("#")[1]);
    expect(url.startsWith("https://pythontutor.com/visualize.html#")).toBe(true);
    expect(params.get("code")).toBe(
      "#include <iostream>\n" +
      "int answer() { return 42; }\n" +
      "int main() { std::cout << answer(); }",
    );
    expect(params.get("curInstr")).toBe("0");
    expect(params.get("mode")).toBe("display");
    expect(params.get("py")).toBe("cpp");
    expect(target).toBe("_blank");
    expect(features).toBe("noopener");
  });

  it("runs the selected revision with modified stdin and runargs values", async () => {
    const fetchMock = vi.fn(async (url, options) => {
      expect(url).toBe("https://example.test/runs/");
      const payload = JSON.parse(options.body);
      expect(payload).toEqual({
        run_spec: {
          language_id: "python3",
          sourcecode: 'print("two")',
          parameters: { interpreterargs: ["-B"], runargs: ["--name", "Alice Bob", "--limit=5"] },
          input: "Alice Bob",
        },
      });
      return {
        ok: true,
        json: async () => ({ outcome: 15, stdout: "two\n", stderr: "", cmpinfo: "" }),
      };
    });
    globalThis.fetch = fetchMock;

    const element = appendCode({
      source: 'print("one")',
      stdin: "stdin text",
      parameters: { interpreterargs: ["-B"], compileargs: [], runargs: ["--limit", "1"] },
    });
    const run = runButton(element);
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const runtimeInputs = Array.from(element.querySelectorAll("input.tb-code__runtime-input"));
    const output = element.querySelector(".tb-code__output");
    const status = element.querySelector(".tb-code__status");

    click(edit);
    editor.value = 'print("two")';
    change(editor);
    click(edit);
    runtimeInputs[0].value = "Alice Bob";
    runtimeInputs[1].value = '--name "Alice Bob" --limit=5';
    await click(run);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledOnce();
    expect(run.disabled).toBe(false);
    expect(run.getAttribute("aria-busy")).toBe("false");
    expect(output.textContent).toBe("two\n");
    expect(status.textContent).toBe("Run complete.");
  });

  it("sends run-before and run-after fragments without showing them in the editor", async () => {
    const fetchMock = vi.fn(async (url, options) => {
      const payload = JSON.parse(options.body);
      expect(payload.run_spec.sourcecode).toBe(
        "# hidden setup\n" +
        'print("edited visible")\n' +
        "# hidden tests",
      );
      return {
        ok: true,
        json: async () => ({ outcome: 15, stdout: "ok\n", stderr: "", cmpinfo: "" }),
      };
    });
    globalThis.fetch = fetchMock;

    const element = appendCode({
      source: 'print("visible")',
      runBefore: ["# hidden setup"],
      runAfter: ["# hidden tests"],
    });
    const run = runButton(element);
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const displayedSource = element.querySelector(".tb-code__fallback code");

    click(edit);
    expect(editor.value).toBe('print("visible")');
    expect(editor.value).not.toContain("hidden setup");
    expect(editor.value).not.toContain("hidden tests");

    editor.value = 'print("edited visible")';
    input(editor);
    click(edit);

    expect(displayedSource.textContent).toBe('print("edited visible")');
    expect(displayedSource.textContent).not.toContain("hidden setup");
    expect(displayedSource.textContent).not.toContain("hidden tests");

    await click(run);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("updates the displayed source when edited code is hidden before running", async () => {
    const fetchMock = vi.fn(async (url, options) => {
      const payload = JSON.parse(options.body);
      expect(payload.run_spec.sourcecode).toBe('print("hidden edit")');
      return {
        ok: true,
        json: async () => ({ outcome: 15, stdout: "hidden edit\n", stderr: "", cmpinfo: "" }),
      };
    });
    globalThis.fetch = fetchMock;

    const element = appendCode({ source: 'print("original")' });
    const run = runButton(element);
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const displayedSource = element.querySelector(".tb-code__fallback code");

    click(edit);
    editor.value = 'print("hidden edit")';
    input(editor);
    click(edit);

    expect(editor.hidden).toBe(true);
    expect(displayedSource.textContent).toBe('print("hidden edit")');

    await click(run);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledOnce();
    expect(displayedSource.textContent).toBe('print("hidden edit")');
  });

  it("updates the displayed source when edited code is run before hiding", async () => {
    const fetchMock = vi.fn(async (url, options) => {
      const payload = JSON.parse(options.body);
      expect(payload.run_spec.sourcecode).toBe('print("visible edit")');
      return {
        ok: true,
        json: async () => ({ outcome: 15, stdout: "visible edit\n", stderr: "", cmpinfo: "" }),
      };
    });
    globalThis.fetch = fetchMock;

    const element = appendCode({ source: 'print("original")' });
    const run = runButton(element);
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const displayedSource = element.querySelector(".tb-code__fallback code");

    click(edit);
    editor.value = 'print("visible edit")';
    input(editor);
    await click(run);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledOnce();
    expect(displayedSource.textContent).toBe('print("visible edit")');

    click(edit);
    expect(editor.hidden).toBe(true);
    expect(displayedSource.textContent).toBe('print("visible edit")');
  });

  it("updates Sphinx-highlighted fallback source after editing", () => {
    const element = appendSphinxHighlightedCode({ source: 'print("one")' });
    const edit = editButton(element);
    const editor = element.querySelector("textarea.tb-code__editor");
    const displayedSource = element.querySelector(".tb-code__fallback pre");

    click(edit);
    editor.value = 'print("sphinx shape")';
    input(editor);
    click(edit);

    expect(displayedSource.textContent).toBe('print("sphinx shape")');
    expect(displayedSource.querySelector("span.nb")?.textContent).toBe("print");
    expect(displayedSource.querySelector("span.s2")?.textContent).toBe('"sphinx shape"');
  });

  it("renders attached file editors and sends current file contents with runs", async () => {
    const uploadedIds = [];
    const fetchMock = vi.fn(async (url, options) => {
      if (options.method === "PUT") {
        const fileId = url.split("/").pop();
        uploadedIds.push(fileId);
        expect(fileId).toMatch(/^[a-z0-9]{8,}$/);
        expect(url).toMatch(/^https:\/\/example\.test\/files\/[a-z0-9]+$/);
        const payload = JSON.parse(options.body);
        expect(payload).toEqual({
          file_contents: uploadedIds.length === 1 ? "ZWRpdGVkIGZpbGU=" : "QUJD",
        });
        return { ok: true, status: 204 };
      }
      const payload = JSON.parse(options.body);
      expect(payload.run_spec.file_list).toEqual([
        [uploadedIds[0], "input.txt"],
        [uploadedIds[1], "images/pic.png"],
      ]);
      return {
        ok: true,
        json: async () => ({ outcome: 15, stdout: "done\n", stderr: "", cmpinfo: "" }),
      };
    });
    globalThis.fetch = fetchMock;

    const element = appendCode({
      filesEndpoint: "https://example.test/files/",
      files: [
        {
          filename: "input.txt",
          content: "original file",
          mime_type: "text/plain",
          is_text: true,
          editable: true,
        },
        {
          filename: "images/pic.png",
          data_url: "data:image/png;base64,QUJD",
          mime_type: "image/png",
          is_text: false,
          editable: false,
        },
      ],
    });
    const attachedFiles = element.querySelector(".tb-code__attached-files");
    const fileEditor = element.querySelector("textarea.tb-code__attached-file-editor");
    const fileNote = element.querySelector(".tb-code__attached-file-note");
    const run = runButton(element);

    expect(attachedFiles.hidden).toBe(false);
    expect(fileEditor.value).toBe("original file");
    expect(fileNote.textContent).toBe("image/png file");

    fileEditor.value = "edited file";
    await click(run);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("preloads languages and reports unsupported service languages", async () => {
    const fetchMock = vi.fn(async (url) => ({
      ok: true,
      json: async () => (url.endsWith("/languages") ? [["python3", "3.12"]] : { outcome: 15, stdout: "" }),
    }));
    globalThis.fetch = fetchMock;

    const element = appendCode({
      jobeLanguage: "ruby",
      validateLanguage: true,
    });
    await flushPromises();
    const run = runButton(element);
    const output = element.querySelector(".tb-code__output");
    const status = element.querySelector(".tb-code__status");

    await click(run);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe("https://example.test/languages");
    expect(output.textContent).toContain("does not currently report support for ruby");
    expect(status.textContent).toBe("Run failed.");
    expect(run.disabled).toBe(false);
  });

  it("renders service errors in the status and output regions", async () => {
    globalThis.fetch = vi.fn(async () => ({ ok: false, status: 500 }));
    const element = appendCode();
    const run = runButton(element);
    const output = element.querySelector(".tb-code__output");
    const status = element.querySelector(".tb-code__status");

    await click(run);
    await flushPromises();

    expect(output.textContent).toBe("Execution service returned 500.");
    expect(status.textContent).toBe("Run failed.");
    expect(run.disabled).toBe(false);
  });
});
