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
    revisionLabel: "Source revision",
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

async function flushPromises() {
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
  await new Promise((resolve) => setTimeout(resolve, 0));
}

describe("tb-code Web Component", () => {
  it("enhances fallback code with run, edit, status, output, and revision controls", () => {
    const element = appendCode();
    const buttons = element.querySelectorAll("button.tb-code__button");
    const editButton = buttons[1];
    const editor = element.querySelector("textarea.tb-code__editor");
    const revisionControl = element.querySelector(".tb-code__revision-control");
    const revisionSlider = element.querySelector("input.tb-code__revision-slider");
    const revisionOutput = element.querySelector("output.tb-code__revision-output");
    const runtimeInputs = element.querySelector(".tb-code__runtime-inputs");
    const status = element.querySelector(".tb-code__status");
    const output = element.querySelector(".tb-code__output");

    expect(customElements.get("tb-code")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(buttons[0].textContent).toBe("Run");
    expect(editButton.textContent).toBe("Edit source");
    expect(editButton.getAttribute("aria-expanded")).toBe("false");
    expect(editButton.getAttribute("aria-controls")).toBe(editor.id);
    expect(editor.hidden).toBe(true);
    expect(revisionControl.hidden).toBe(true);
    expect(revisionSlider.type).toBe("range");
    expect(revisionSlider.min).toBe("1");
    expect(revisionSlider.max).toBe("1");
    expect(revisionOutput.value).toBe("1 of 1");
    expect(runtimeInputs.hidden).toBe(true);
    expect(status.getAttribute("role")).toBe("status");
    expect(status.getAttribute("aria-live")).toBe("polite");
    expect(output.getAttribute("aria-labelledby")).toBeTruthy();
  });

  it("toggles editor visibility and records revisions with the slider", () => {
    const element = appendCode();
    const editButton = element.querySelectorAll("button.tb-code__button")[1];
    const editor = element.querySelector("textarea.tb-code__editor");
    const revisionControl = element.querySelector(".tb-code__revision-control");
    const revisionSlider = element.querySelector("input.tb-code__revision-slider");
    const revisionOutput = element.querySelector("output.tb-code__revision-output");
    const status = element.querySelector(".tb-code__status");

    click(editButton);
    expect(editButton.textContent).toBe("Hide source");
    expect(editButton.getAttribute("aria-expanded")).toBe("true");
    expect(editor.hidden).toBe(false);
    expect(revisionControl.hidden).toBe(false);

    editor.value = 'print("two")';
    input(editor);
    change(editor);
    expect(revisionSlider.max).toBe("2");
    expect(revisionSlider.value).toBe("2");
    expect(revisionOutput.value).toBe("2 of 2");

    revisionSlider.value = "1";
    input(revisionSlider);
    expect(editor.value).toBe('print("one")');
    expect(revisionOutput.value).toBe("1 of 2");
    expect(status.textContent).toBe("Loaded editor revision 1.");

    click(editButton);
    expect(editButton.textContent).toBe("Edit source");
    expect(editButton.getAttribute("aria-expanded")).toBe("false");
    expect(editor.hidden).toBe(true);
    expect(revisionControl.hidden).toBe(true);
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
    const runButton = element.querySelectorAll("button.tb-code__button")[0];
    const editButton = element.querySelectorAll("button.tb-code__button")[1];
    const editor = element.querySelector("textarea.tb-code__editor");
    const runtimeInputs = Array.from(element.querySelectorAll("input.tb-code__runtime-input"));
    const output = element.querySelector(".tb-code__output");
    const status = element.querySelector(".tb-code__status");

    click(editButton);
    editor.value = 'print("two")';
    change(editor);
    click(editButton);
    runtimeInputs[0].value = "Alice Bob";
    runtimeInputs[1].value = '--name "Alice Bob" --limit=5';
    await click(runButton);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledOnce();
    expect(runButton.disabled).toBe(false);
    expect(runButton.getAttribute("aria-busy")).toBe("false");
    expect(output.textContent).toBe("two\n");
    expect(status.textContent).toBe("Run complete.");
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
    const runButton = element.querySelectorAll("button.tb-code__button")[0];

    expect(attachedFiles.hidden).toBe(false);
    expect(fileEditor.value).toBe("original file");
    expect(fileNote.textContent).toBe("image/png file");

    fileEditor.value = "edited file";
    await click(runButton);
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
    const runButton = element.querySelectorAll("button.tb-code__button")[0];
    const output = element.querySelector(".tb-code__output");
    const status = element.querySelector(".tb-code__status");

    await click(runButton);
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe("https://example.test/languages");
    expect(output.textContent).toContain("does not currently report support for ruby");
    expect(status.textContent).toBe("Run failed.");
    expect(runButton.disabled).toBe(false);
  });

  it("renders service errors in the status and output regions", async () => {
    globalThis.fetch = vi.fn(async () => ({ ok: false, status: 500 }));
    const element = appendCode();
    const runButton = element.querySelectorAll("button.tb-code__button")[0];
    const output = element.querySelector(".tb-code__output");
    const status = element.querySelector(".tb-code__status");

    await click(runButton);
    await flushPromises();

    expect(output.textContent).toBe("Execution service returned 500.");
    expect(status.textContent).toBe("Run failed.");
    expect(runButton.disabled).toBe(false);
  });
});
