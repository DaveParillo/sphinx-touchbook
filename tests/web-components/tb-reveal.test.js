import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-reveal.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendReveal({ modal = false } = {}) {
  const element = document.createElement("tb-reveal");
  element.id = modal ? "modal-reveal" : "inline-reveal";
  element.setAttribute("showlabel", "Open");
  element.setAttribute("hidelabel", "Close");
  if (modal) {
    element.setAttribute("modal", "");
    element.setAttribute("modal-titlebar", "Author message");
  }
  element.innerHTML = `
    <details class="tb-reveal__fallback"><summary>Open</summary></details>
    <div class="tb-reveal__content"><p>Hidden answer</p></div>
  `;
  document.body.appendChild(element);
  return element;
}

describe("tb-reveal Web Component", () => {
  it("enhances inline reveal content with an accessible toggle", () => {
    const element = appendReveal();

    const fallback = element.querySelector(".tb-reveal__fallback");
    const button = element.querySelector("button.tb-reveal__button");
    const panel = element.querySelector(".tb-reveal__panel");

    expect(customElements.get("tb-reveal")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(fallback.hidden).toBe(true);
    expect(button.textContent).toBe("Open");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(button.getAttribute("aria-controls")).toBe(panel.id);
    expect(panel.hidden).toBe(true);
    expect(panel.textContent).toContain("Hidden answer");

    click(button);
    expect(button.textContent).toBe("Close");
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(panel.hidden).toBe(false);

    click(button);
    expect(button.textContent).toBe("Open");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(panel.hidden).toBe(true);
  });

  it("enhances modal reveal content with dialog controls", () => {
    HTMLDialogElement.prototype.showModal = vi.fn(function showModal() {
      this.setAttribute("open", "");
    });
    HTMLDialogElement.prototype.close = vi.fn(function close() {
      this.removeAttribute("open");
    });

    const element = appendReveal({ modal: true });
    const fallback = element.querySelector(".tb-reveal__fallback");
    const openButton = element.querySelector("button.tb-reveal__button");
    const dialog = element.querySelector("dialog.tb-reveal__dialog");
    const closeButton = dialog.querySelector("button.tb-reveal__button");
    const label = dialog.querySelector(".tb-reveal__dialog-label");

    expect(fallback.hidden).toBe(true);
    expect(openButton.getAttribute("aria-haspopup")).toBe("dialog");
    expect(openButton.textContent).toBe("Open");
    expect(dialog.getAttribute("aria-labelledby")).toBe(label.id);
    expect(label.textContent).toBe("Author message");
    expect(dialog.textContent).toContain("Hidden answer");

    click(openButton);
    expect(dialog.hasAttribute("open")).toBe(true);
    expect(HTMLDialogElement.prototype.showModal).toHaveBeenCalledOnce();

    click(closeButton);
    expect(dialog.hasAttribute("open")).toBe(false);
    expect(HTMLDialogElement.prototype.close).toHaveBeenCalledOnce();
  });
});
