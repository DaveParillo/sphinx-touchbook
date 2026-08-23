import { beforeAll, beforeEach, describe, expect, it } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-reveal.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendReveal() {
  const element = document.createElement("tb-reveal");
  element.id = "inline-reveal";
  element.setAttribute("label", "Hint");
  element.innerHTML = `
    <details class="tb-reveal__fallback"><summary>Hint</summary></details>
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
    const chevron = button.querySelector("svg.tb-reveal__chevron");
    const panel = element.querySelector(".tb-reveal__panel");

    expect(customElements.get("tb-reveal")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(fallback.hidden).toBe(true);
    expect(button.textContent).toBe("Hint");
    expect(chevron.getAttribute("aria-hidden")).toBe("true");
    expect(chevron.getAttribute("focusable")).toBe("false");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(button.getAttribute("aria-controls")).toBe(panel.id);
    expect(panel.hidden).toBe(true);
    expect(panel.textContent).toContain("Hidden answer");

    click(button);
    expect(button.textContent).toBe("Hint");
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(panel.hidden).toBe(false);

    click(button);
    expect(button.textContent).toBe("Hint");
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(panel.hidden).toBe(true);
  });

});
