import { beforeEach, describe, expect, it } from "vitest";
import { loadComponentScript } from "./helpers.js";

beforeEach(async () => {
  document.body.innerHTML = "";
  await loadComponentScript("tb-file.js");
});

function appendTbFile(config = {}) {
  const data = {
    filename: "input.txt",
    content: "Alice",
    mimeType: "text/plain",
    isText: true,
    editable: true,
    editLabel: "Edit",
    hideEditLabel: "Hide editor",
    ...config,
  };
  const element = document.createElement("tb-file");
  element.id = "input-file";
  element.setAttribute("filename", data.filename);
  element.innerHTML = `
    <figure class="tb-file__fallback">
      <figcaption class="tb-file__caption">${data.filename}</figcaption>
      <pre class="tb-file__content"><code>${data.content}</code></pre>
    </figure>
    <script type="application/json" class="tb-file__config">${JSON.stringify(data)}</script>
  `;
  document.body.appendChild(element);
  return element;
}

describe("tb-file Web Component", () => {
  it("adds an accessible edit toggle for editable text files", () => {
    const element = appendTbFile();
    const button = element.querySelector("button.tb-file__button");
    const editor = element.querySelector("textarea.tb-file__editor");
    const label = element.querySelector("label.tb-file__editor-label");
    const fallback = element.querySelector(".tb-file__fallback");
    const sourceListing = element.querySelector(".tb-file__content");
    const editorSlot = element.querySelector(".tb-file__editor-slot");
    const caption = element.querySelector(".tb-file__caption");

    expect(customElements.get("tb-file")).toBeTypeOf("function");
    expect(button).not.toBeNull();
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(fallback.hidden).toBe(false);
    expect(caption.hidden).toBe(false);
    expect(sourceListing.hidden).toBe(false);
    expect(editorSlot.hidden).toBe(true);
    expect(editor.hidden).toBe(true);
    expect(label.hidden).toBe(true);

    button.click();
    expect(button.textContent).toBe("Hide editor");
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(fallback.hidden).toBe(false);
    expect(caption.hidden).toBe(false);
    expect(sourceListing.hidden).toBe(true);
    expect(editorSlot.hidden).toBe(false);
    expect(editor.hidden).toBe(false);
    expect(label.hidden).toBe(false);
  });

  it("replaces the fallback listing with an equally tall editor", () => {
    const element = appendTbFile();
    const button = element.querySelector("button.tb-file__button");
    const fallback = element.querySelector(".tb-file__fallback");
    const sourceListing = element.querySelector(".tb-file__content");
    const editorSlot = element.querySelector(".tb-file__editor-slot");
    const editor = element.querySelector("textarea.tb-file__editor");
    sourceListing.getBoundingClientRect = () => ({ height: 180 });

    button.click();
    expect(fallback.hidden).toBe(false);
    expect(sourceListing.hidden).toBe(true);
    expect(editorSlot.hidden).toBe(false);
    expect(editor.style.height).toBe("180px");
    expect(editor.style.minHeight).toBe("180px");

    button.click();
    expect(fallback.hidden).toBe(false);
    expect(sourceListing.hidden).toBe(false);
    expect(editorSlot.hidden).toBe(true);
    expect(editor.style.height).toBe("");
    expect(editor.style.minHeight).toBe("");
  });

  it("updates the fallback text as the file editor changes", () => {
    const element = appendTbFile();
    const button = element.querySelector("button.tb-file__button");
    const editor = element.querySelector("textarea.tb-file__editor");
    const code = element.querySelector(".tb-file__content code");

    button.click();
    editor.value = "Bob";
    editor.dispatchEvent(new Event("input", { bubbles: true }));

    expect(code.textContent).toBe("Bob");
  });

  it("provides its current content to attached code blocks", () => {
    const element = appendTbFile();
    const button = element.querySelector("button.tb-file__button");
    const editor = element.querySelector("textarea.tb-file__editor");

    expect(element.getFileContent()).toBe("Alice");
    button.click();
    editor.value = "Bob";
    editor.dispatchEvent(new Event("input", { bubbles: true }));

    expect(element.getFileContent()).toBe("Bob");
  });

  it("does not add editing controls for image files", () => {
    const element = appendTbFile({
      filename: "images/pic.svg",
      content: "",
      mimeType: "image/svg+xml",
      isText: false,
      editable: false,
    });

    expect(element.querySelector("button.tb-file__button")).toBeNull();
    expect(element.querySelector("textarea.tb-file__editor")).toBeNull();
  });
});
