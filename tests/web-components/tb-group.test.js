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

function ownTabs(element) {
  return Array.from(element.querySelectorAll(":scope > .tb-group__tablist > .tb-group__tab"));
}

function ownPanels(element) {
  return Array.from(element.querySelectorAll(":scope > .tb-group__panels > .tb-group__panel"));
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

  it("keeps a nested group selected when its enclosing tab is selected", () => {
    const outer = document.createElement("tb-group");
    outer.id = "outer-tabs";
    outer.innerHTML = `
      <div class="tb-group__fallback">
        <tb-tab label="Source">
          <div class="tb-tab__content"><p>Source content</p></div>
        </tb-tab>
        <tb-tab label="Rendered">
          <div class="tb-tab__content">
            <tb-group id="inner-tabs">
              <div class="tb-group__fallback">
                <tb-tab label="First inner">
                  <div class="tb-tab__content"><p>First inner content</p></div>
                </tb-tab>
                <tb-tab label="Second inner">
                  <div class="tb-tab__content"><p>Second inner content</p></div>
                </tb-tab>
              </div>
            </tb-group>
          </div>
        </tb-tab>
      </div>
    `;

    document.body.appendChild(outer);

    const outerTabs = ownTabs(outer);
    const outerPanels = ownPanels(outer);
    const inner = outer.querySelector("#inner-tabs");
    const innerTabs = ownTabs(inner);
    const innerPanels = ownPanels(inner);

    expect(outerTabs[0].getAttribute("aria-selected")).toBe("true");
    expect(outerPanels[1].hidden).toBe(true);
    expect(innerTabs[0].getAttribute("aria-selected")).toBe("true");
    expect(innerPanels[0].hidden).toBe(false);

    click(outerTabs[1]);

    expect(outerTabs[1].getAttribute("aria-selected")).toBe("true");
    expect(outerPanels[1].hidden).toBe(false);
    expect(innerTabs[0].getAttribute("aria-selected")).toBe("true");
    expect(innerTabs[1].getAttribute("aria-selected")).toBe("false");
    expect(innerPanels[0].hidden).toBe(false);
    expect(innerPanels[1].hidden).toBe(true);
    expect(innerPanels[0].textContent).toContain("First inner content");
  });
});
