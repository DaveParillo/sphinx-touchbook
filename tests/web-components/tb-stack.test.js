import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, keydown, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-stack.js");
  await loadComponentScript("tb-group.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
  window.history.replaceState({}, "", window.location.pathname);
});

function createStack({ count = 3, id = "example", config = undefined } = {}) {
  const element = document.createElement("tb-stack");
  element.id = id;
  const scenes = Array.from({ length: count }, (_, index) => ({
    id: `${id}-scene-${index}`, caption: `Step ${index + 1}`, objects: []
  }));
  const controls = [["first", "First scene", "chevron-double-left"],
    ["previous", "Previous scene", "chevron-left"], ["next", "Next scene", "chevron-right"],
    ["last", "Last scene", "chevron-double-right"]];
  element.innerHTML = `<div class="tb-stack__controls" hidden>
    <p class="tb-stack__scene-caption" hidden></p>
    <div class="tb-stack__navigation">
    ${controls.map(([action, label, icon]) => `<button type="button" data-action="${action}"
      aria-label="${label}" title="${label}"><svg class="bi bi-${icon}" aria-hidden="true" focusable="false"></svg></button>`).join("")}
    <p class="tb-stack__status" role="status" aria-live="polite" aria-atomic="true"></p>
    </div>
  </div>
  <div class="tb-stack__scenes">${scenes.map((scene, index) =>
    `<tb-scene id="${scene.id}"><p class="tb-scene__caption">Scene ${index + 1}: ${scene.caption}</p><tb-array id="${id}-array-${index}">
    <p>Complete array ${index}</p></tb-array><tb-pointer id="${id}-pointer-${index}">Pointer ${index}</tb-pointer></tb-scene>`
  ).join("")}</div>
  <script type="application/json">${config === undefined ? JSON.stringify({ version: 1, scenes }) : config}</script>`;
  return element;
}

function appendStack(options) {
  const element = createStack(options);
  document.body.append(element);
  return element;
}

function button(element, action) { return element.querySelector(`button[data-action="${action}"]`); }
function visibleScenes(element) { return Array.from(element.querySelectorAll("tb-scene")).filter((scene) => !scene.hidden); }


describe("tb-stack manual navigation", () => {
  it("shows the first complete scene and enables only forward navigation", () => {
    const element = appendStack();
    expect(customElements.get("tb-stack")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(visibleScenes(element).map((scene) => scene.id)).toEqual(["example-scene-0"]);
    expect(button(element, "first").disabled).toBe(true);
    expect(button(element, "previous").disabled).toBe(true);
    expect(button(element, "next").disabled).toBe(false);
    expect(button(element, "last").disabled).toBe(false);
    expect(element.querySelector(".tb-stack__controls").hidden).toBe(false);
    expect(element.querySelector(".tb-stack__status").textContent).toBe("Scene 1 of 3: Step 1");
    expect(Array.from(element.querySelectorAll(".tb-scene__caption")).every((heading) => heading.hidden)).toBe(true);
  });

  it("keeps controls above changing scene content with one current scene caption", () => {
    const element = appendStack();
    const controls = element.querySelector(".tb-stack__controls");
    const scenes = element.querySelector(".tb-stack__scenes");
    const content = element.querySelectorAll("tb-array")[1];
    content.append(document.createElement("pre"));
    content.lastElementChild.textContent = "A larger scene\n".repeat(30);
    click(button(element, "next").querySelector("svg"));
    expect(controls.nextElementSibling).toBe(scenes);
    expect(controls.querySelector(".tb-stack__status").textContent).toBe("Scene 2 of 3: Step 2");
    const caption = controls.querySelector(".tb-stack__scene-caption");
    const navigation = controls.querySelector(".tb-stack__navigation");
    expect(caption.textContent).toBe("Step 2");
    expect(caption.hidden).toBe(false);
    expect(caption.nextElementSibling).toBe(navigation);
    expect(navigation.lastElementChild.firstChild.textContent).toBe("Scene 2 of 3");
    expect(navigation.lastElementChild.querySelector(".tb-stack__status-caption").textContent).toBe(": Step 2");
    expect(visibleScenes(element)[0].querySelector(".tb-scene__caption").hidden).toBe(true);
    expect(content.querySelector("p").hidden).toBe(false);
  });

  it("clears the separate caption when the next scene has no caption", () => {
    const element = createStack();
    const config = element.querySelector('script[type="application/json"]');
    const data = JSON.parse(config.textContent);
    data.scenes[1].caption = "";
    config.textContent = JSON.stringify(data);
    document.body.append(element);
    click(button(element, "next"));
    const caption = element.querySelector(".tb-stack__scene-caption");
    expect(caption.hidden).toBe(true);
    expect(caption.textContent).toBe("");
    expect(element.querySelector(".tb-stack__status").textContent).toBe("Scene 2 of 3");
  });

  it("implements all four navigation actions without replaying or cloning scenes", () => {
    const element = appendStack({ count: 4 });
    const original = Array.from(element.querySelectorAll("tb-scene"));
    click(button(element, "next"));
    expect(visibleScenes(element)).toEqual([original[1]]);
    click(button(element, "last"));
    expect(visibleScenes(element)).toEqual([original[3]]);
    expect(button(element, "next").disabled).toBe(true);
    expect(button(element, "last").disabled).toBe(true);
    click(button(element, "previous"));
    expect(visibleScenes(element)).toEqual([original[2]]);
    click(button(element, "first"));
    expect(visibleScenes(element)).toEqual([original[0]]);
    expect(element.querySelectorAll("tb-array")).toHaveLength(4);
    expect(new Set(Array.from(element.querySelectorAll("[id]")).map((item) => item.id)).size).toBe(12);
  });

  it("keeps keyboard focus on an available control at an endpoint", () => {
    const element = appendStack();
    const last = button(element, "last");
    last.focus();
    click(last);
    expect(document.activeElement).toBe(button(element, "previous"));
    const first = button(element, "first");
    first.focus();
    click(first);
    expect(document.activeElement).toBe(button(element, "next"));
    expect(element.querySelector(".tb-stack__status").hasAttribute("tabindex")).toBe(false);
  });

  it("handles a single scene with all navigation disabled", () => {
    const element = appendStack({ count: 1 });
    expect(visibleScenes(element)).toHaveLength(1);
    element.querySelectorAll("button").forEach((control) => expect(control.disabled).toBe(true));
    expect(element.querySelector(".tb-stack__status").textContent).toBe("Scene 1 of 1: Step 1");
  });

  it.each(["not JSON", "null", '{"version":2,"scenes":[]}', '{"version":1,"scenes":[]}'])(
    "retains all static scenes when configuration is invalid: %s", (config) => {
      const element = appendStack({ config });
      expect(visibleScenes(element)).toHaveLength(3);
      expect(element.dataset.enhanced).toBeUndefined();
      expect(element.querySelector(".tb-stack__controls").hidden).toBe(true);
      expect(Array.from(element.querySelectorAll(".tb-scene__caption")).every((heading) => !heading.hidden)).toBe(true);
    });

  it("retains static scenes if scene identifiers do not match or controls are missing", () => {
    const element = createStack();
    element.querySelector("tb-scene").id = "different-id";
    document.body.append(element);
    expect(visibleScenes(element)).toHaveLength(3);
    const missing = createStack({ id: "missing" });
    missing.querySelector(".tb-stack__controls").remove();
    document.body.append(missing);
    expect(visibleScenes(missing)).toHaveLength(3);
  });

  it("keeps stacks independent even when semantic objects have the same names", () => {
    const first = appendStack();
    const second = appendStack({ id: "second" });
    click(button(first, "last"));
    expect(first.dataset.scene).toBe("3");
    expect(second.dataset.scene).toBe("1");
  });
});


describe("tb-stack document targets and lifecycle", () => {
  it("follows links to scenes in another stack while preserving the departure scene", () => {
    const first = appendStack();
    const second = appendStack({ id: "second" });
    const link = document.createElement("a");
    link.href = "#second-scene-2";
    first.querySelector("tb-scene").append(link);

    click(link);

    expect(visibleScenes(first)[0].id).toBe("example-scene-0");
    expect(visibleScenes(second)[0].id).toBe("second-scene-2");
    expect(second.querySelector(".tb-stack__status").textContent).toBe("Scene 3 of 3: Step 3");
    expect(button(second, "next").disabled).toBe(true);
    expect(button(second, "previous").disabled).toBe(false);
  });

  it("initializes to the scene containing the current document target", () => {
    window.history.replaceState({}, "", "#example-pointer-2");
    const element = appendStack();
    expect(visibleScenes(element)[0].id).toBe("example-scene-2");
  });

  it("reveals inactive scene content on hash changes and repeated same-hash links", () => {
    const element = appendStack();
    window.history.replaceState({}, "", "#example-array-2");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    expect(element.dataset.scene).toBe("3");
    click(button(element, "first"));
    const link = document.createElement("a");
    link.href = "#example-array-2";
    document.body.append(link);
    click(link);
    expect(element.dataset.scene).toBe("3");
  });

  it("ignores malformed and unrelated document targets", () => {
    const element = appendStack();
    element.revealHashTarget("#%invalid");
    element.revealHashTarget("#missing");
    expect(element.dataset.scene).toBe("1");
  });

  it("does not duplicate controls or listeners after reconnecting", () => {
    const element = appendStack();
    click(button(element, "next"));
    element.remove();
    document.body.append(element);
    const show = vi.spyOn(element, "showScene");
    click(button(element, "next"));
    expect(show).toHaveBeenCalledTimes(1);
    expect(element.dataset.scene).toBe("3");
    expect(element.querySelectorAll(".tb-stack__controls")).toHaveLength(1);
    window.history.replaceState({}, "", "#example-pointer-0");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    expect(element.dataset.scene).toBe("1");
  });

  it("preserves access to stack controls inside tb-group panels", () => {
    const group = document.createElement("tb-group");
    group.id = "tabs";
    group.innerHTML = `<div class="tb-group__fallback">
      <tb-tab label="Source"><div class="tb-tab__content">Source text</div></tb-tab>
      <tb-tab label="Rendered"><div class="tb-tab__content"></div></tb-tab>
      </div>`;
    group.querySelectorAll(".tb-tab__content")[1].append(createStack());
    document.body.append(group);
    const tabs = group.ownTabs();
    click(tabs[1]);
    keydown(tabs[1], "Tab");
    expect(document.activeElement.getAttribute("aria-label")).toBe("Next scene");
    click(document.activeElement);
    expect(group.querySelector("tb-stack").dataset.scene).toBe("2");
  });
});
