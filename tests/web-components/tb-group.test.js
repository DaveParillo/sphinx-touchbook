import { beforeAll, beforeEach, describe, expect, it } from "vitest";
import { click, keydown, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-group.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendGroup() {
  const element = document.createElement("tb-group");
  element.id = "example-tabs";
  element.innerHTML = `
    <div class="tb-group__fallback">
      <tb-tab label="First">
        <div class="tb-tab__content"><p>First content</p></div>
      </tb-tab>
      <tb-tab label="Second">
        <div class="tb-tab__content"><p>Second content</p></div>
      </tb-tab>
      <tb-tab label="Third">
        <div class="tb-tab__content"><p>Third content</p></div>
      </tb-tab>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

describe("tb-group Web Component", () => {
  it("creates an ARIA tab interface from fallback tab content", () => {
    const element = appendGroup();
    const fallback = element.querySelector(".tb-group__fallback");
    const tablist = element.querySelector(".tb-group__tablist");
    const tabs = Array.from(element.querySelectorAll(".tb-group__tab"));
    const panels = Array.from(element.querySelectorAll(".tb-group__panel"));

    expect(customElements.get("tb-group")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(fallback.hidden).toBe(true);
    expect(tablist.getAttribute("role")).toBe("tablist");
    expect(tabs).toHaveLength(3);
    expect(panels).toHaveLength(3);
    expect(tabs.map((tab) => tab.textContent)).toEqual(["First", "Second", "Third"]);

    expect(tabs[0].getAttribute("role")).toBe("tab");
    expect(tabs[0].getAttribute("aria-selected")).toBe("true");
    expect(tabs[0].getAttribute("aria-controls")).toBe(panels[0].id);
    expect(panels[0].getAttribute("role")).toBe("tabpanel");
    expect(panels[0].getAttribute("aria-labelledby")).toBe(tabs[0].id);
    expect(panels[0].hidden).toBe(false);
    expect(panels[1].hidden).toBe(true);
    expect(panels[0].textContent).toContain("First content");
  });

  it("selects tabs by click and arrow-key navigation", () => {
    const element = appendGroup();
    const tabs = Array.from(element.querySelectorAll(".tb-group__tab"));
    const panels = Array.from(element.querySelectorAll(".tb-group__panel"));

    click(tabs[1]);
    expect(tabs[0].getAttribute("aria-selected")).toBe("false");
    expect(tabs[1].getAttribute("aria-selected")).toBe("true");
    expect(tabs[1].tabIndex).toBe(0);
    expect(panels[0].hidden).toBe(true);
    expect(panels[1].hidden).toBe(false);
    expect(document.activeElement).toBe(tabs[1]);

    keydown(tabs[1], "ArrowRight");
    expect(tabs[2].getAttribute("aria-selected")).toBe("true");
    expect(panels[2].hidden).toBe(false);

    keydown(tabs[2], "ArrowRight");
    expect(tabs[0].getAttribute("aria-selected")).toBe("true");
    expect(panels[0].hidden).toBe(false);

    keydown(tabs[0], "End");
    expect(tabs[2].getAttribute("aria-selected")).toBe("true");

    keydown(tabs[2], "Home");
    expect(tabs[0].getAttribute("aria-selected")).toBe("true");
  });
});
