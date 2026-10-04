import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, keydown, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-animation.js");
  await loadComponentScript("tb-group.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
  window.history.replaceState({}, "", window.location.pathname);
});

function createAnimation({ count = 3, id = "example", config = undefined } = {}) {
  const element = document.createElement("tb-animation");
  element.id = id;
  const scenes = Array.from({ length: count }, (_, index) => ({
    id: `${id}-scene-${index}`, caption: `Step ${index + 1}`, objects: []
  }));
  element.innerHTML = `<div class="tb-animation__scenes">${scenes.map((scene, index) =>
    `<tb-scene id="${scene.id}"><p>${scene.caption}</p><tb-array id="${id}-array-${index}">
    <p>Complete array ${index}</p></tb-array><tb-pointer id="${id}-pointer-${index}">Pointer ${index}</tb-pointer></tb-scene>`
  ).join("")}</div>
  <script type="application/json">${config === undefined ? JSON.stringify({ version: 1, scenes }) : config}</script>
  <div class="tb-animation__controls" hidden>
    <button type="button" data-action="first" aria-label="First scene">&lt;&lt;</button>
    <button type="button" data-action="previous" aria-label="Previous scene">&lt;</button>
    <button type="button" data-action="next" aria-label="Next scene">&gt;</button>
    <button type="button" data-action="last" aria-label="Last scene">&gt;&gt;</button>
    <p class="tb-animation__status" role="status" aria-live="polite"></p>
  </div>`;
  return element;
}

function appendAnimation(options) {
  const element = createAnimation(options);
  document.body.append(element);
  return element;
}

function button(element, action) { return element.querySelector(`button[data-action="${action}"]`); }
function visibleScenes(element) { return Array.from(element.querySelectorAll("tb-scene")).filter((scene) => !scene.hidden); }


describe("tb-animation manual navigation", () => {
  it("shows the first complete scene and enables only forward navigation", () => {
    const element = appendAnimation();
    expect(customElements.get("tb-animation")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(visibleScenes(element).map((scene) => scene.id)).toEqual(["example-scene-0"]);
    expect(button(element, "first").disabled).toBe(true);
    expect(button(element, "previous").disabled).toBe(true);
    expect(button(element, "next").disabled).toBe(false);
    expect(button(element, "last").disabled).toBe(false);
    expect(element.querySelector(".tb-animation__controls").hidden).toBe(false);
    expect(element.querySelector(".tb-animation__status").textContent).toBe("Scene 1 of 3: Step 1");
  });

  it("implements all four navigation actions without replaying or cloning scenes", () => {
    const element = appendAnimation({ count: 4 });
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
    const element = appendAnimation();
    const last = button(element, "last");
    last.focus();
    click(last);
    expect(document.activeElement).toBe(button(element, "previous"));
    const first = button(element, "first");
    first.focus();
    click(first);
    expect(document.activeElement).toBe(button(element, "next"));
    expect(element.querySelector(".tb-animation__status").hasAttribute("tabindex")).toBe(false);
  });

  it("handles a single scene with all navigation disabled", () => {
    const element = appendAnimation({ count: 1 });
    expect(visibleScenes(element)).toHaveLength(1);
    element.querySelectorAll("button").forEach((control) => expect(control.disabled).toBe(true));
    expect(element.querySelector(".tb-animation__status").textContent).toBe("Scene 1 of 1: Step 1");
  });

  it.each(["not JSON", "null", '{"version":2,"scenes":[]}', '{"version":1,"scenes":[]}'])(
    "retains all static scenes when configuration is invalid: %s", (config) => {
      const element = appendAnimation({ config });
      expect(visibleScenes(element)).toHaveLength(3);
      expect(element.dataset.enhanced).toBeUndefined();
      expect(element.querySelector(".tb-animation__controls").hidden).toBe(true);
    });

  it("retains static scenes if scene identifiers do not match or controls are missing", () => {
    const element = createAnimation();
    element.querySelector("tb-scene").id = "different-id";
    document.body.append(element);
    expect(visibleScenes(element)).toHaveLength(3);
    const missing = createAnimation({ id: "missing" });
    missing.querySelector(".tb-animation__controls").remove();
    document.body.append(missing);
    expect(visibleScenes(missing)).toHaveLength(3);
  });

  it("keeps animations independent even when semantic objects have the same names", () => {
    const first = appendAnimation();
    const second = appendAnimation({ id: "second" });
    click(button(first, "last"));
    expect(first.dataset.scene).toBe("3");
    expect(second.dataset.scene).toBe("1");
  });
});


describe("tb-animation document targets and lifecycle", () => {
  it("initializes to the scene containing the current document target", () => {
    window.history.replaceState({}, "", "#example-pointer-2");
    const element = appendAnimation();
    expect(visibleScenes(element)[0].id).toBe("example-scene-2");
  });

  it("reveals inactive scene content on hash changes and repeated same-hash links", () => {
    const element = appendAnimation();
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
    const element = appendAnimation();
    element.revealHashTarget("#%invalid");
    element.revealHashTarget("#missing");
    expect(element.dataset.scene).toBe("1");
  });

  it("does not duplicate controls or listeners after reconnecting", () => {
    const element = appendAnimation();
    click(button(element, "next"));
    element.remove();
    document.body.append(element);
    const show = vi.spyOn(element, "showScene");
    click(button(element, "next"));
    expect(show).toHaveBeenCalledTimes(1);
    expect(element.dataset.scene).toBe("3");
    expect(element.querySelectorAll(".tb-animation__controls")).toHaveLength(1);
    window.history.replaceState({}, "", "#example-pointer-0");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    expect(element.dataset.scene).toBe("1");
  });

  it("preserves access to animation controls inside tb-group panels", () => {
    const group = document.createElement("tb-group");
    group.id = "tabs";
    group.innerHTML = `<div class="tb-group__fallback">
      <tb-tab label="Source"><div class="tb-tab__content">Source text</div></tb-tab>
      <tb-tab label="Rendered"><div class="tb-tab__content"></div></tb-tab>
      </div>`;
    group.querySelectorAll(".tb-tab__content")[1].append(createAnimation());
    document.body.append(group);
    const tabs = group.ownTabs();
    click(tabs[1]);
    keydown(tabs[1], "Tab");
    expect(document.activeElement.getAttribute("aria-label")).toBe("Next scene");
    click(document.activeElement);
    expect(group.querySelector("tb-animation").dataset.scene).toBe("2");
  });
});
