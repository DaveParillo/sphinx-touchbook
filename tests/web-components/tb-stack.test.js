import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { change, click, keydown, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-stack.js");
  await loadComponentScript("tb-group.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
  window.history.replaceState({}, "", window.location.pathname);
});

function createStack({ count = 3, id = "example", config = undefined, captions = [] } = {}) {
  const element = document.createElement("tb-stack");
  element.id = id;
  element.setAttribute("role", "group");
  element.setAttribute("aria-label", "Scene walkthrough");
  const scenes = Array.from({ length: count }, (_, index) => ({
    id: `${id}-scene-${index}`, caption: captions[index] ?? `Step ${index + 1}`, objects: []
  }));
  const controls = [["first", "First scene", "chevron-double-left"],
    ["previous", "Previous scene", "chevron-left"], ["next", "Next scene", "chevron-right"],
    ["last", "Last scene", "chevron-double-right"]];
  element.innerHTML = `<div class="tb-stack__controls" hidden>
    <p id="${id}-scene-caption" class="tb-stack__scene-caption" hidden></p>
    <div class="tb-stack__navigation">
    ${controls.map(([action, label, icon]) => `<button type="button" data-action="${action}"
      aria-label="${label}" title="${label}"><svg class="bi bi-${icon}" aria-hidden="true" focusable="false"></svg></button>`).join("")}
    <select class="tb-stack__selector" aria-label="Choose scene" hidden></select>
    <p class="tb-stack__status" role="status" aria-live="polite" aria-atomic="true"></p>
    </div>
  </div>
  <div class="tb-stack__scenes">${scenes.map((scene, index) =>
    `<tb-scene id="${scene.id}" role="group" aria-labelledby="${scene.id}-caption"><p id="${scene.id}-caption" class="tb-scene__caption"></p><tb-array id="${id}-array-${index}">
    <p>Complete array ${index}</p></tb-array><tb-pointer id="${id}-pointer-${index}">Pointer ${index}</tb-pointer></tb-scene>`
  ).join("")}</div>
  <script type="application/json">${config === undefined ? JSON.stringify({ version: 1, scenes }) : config}</script>`;
  element.querySelectorAll(".tb-scene__caption").forEach((heading, index) => {
    heading.textContent = `Scene ${index + 1}: ${scenes[index].caption}`;
  });
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
  it("provides a native scene selector with concise captions and full accessible names", () => {
    const captions = ["A".repeat(24), "B".repeat(25), "🦉".repeat(25),
      '<img src=x onerror="alert(1)">', "", "  Words\n   with   spacing  "];
    const element = appendStack({ count: captions.length, captions });
    const select = element.querySelector("select");
    expect(select.getAttribute("aria-label")).toBe("Choose scene");
    expect(select.hasAttribute("role")).toBe(false);
    expect(select.tabIndex).toBe(0);
    expect(select.hidden).toBe(false);
    expect(select.value).toBe("0");
    expect(select.options).toHaveLength(6);
    expect(select.options[0].textContent).toBe(`1 of 6: ${"A".repeat(24)}`);
    expect(select.options[1].textContent).toBe(`2 of 6: ${"B".repeat(23)}…`);
    expect(select.options[2].textContent).toBe(`3 of 6: ${"🦉".repeat(23)}…`);
    expect(select.options[3].getAttribute("aria-label")).toBe(`4 of 6: ${captions[3]}`);
    expect(select.options[3].childElementCount).toBe(0);
    expect(select.options[4].textContent).toBe("5 of 6");
    expect(select.options[5].textContent).toBe("6 of 6: Words with spacing");
    expect(select.options[1].getAttribute("aria-label")).toBe(`2 of 6: ${captions[1]}`);
    expect(select.options[1].title).toBe(`2 of 6: ${captions[1]}`);
    expect(select.title).toBe(`1 of 6: ${captions[0]}`);
  });

  it("jumps directly to any selected scene while keeping focus and avoiding duplicate announcements", () => {
    const element = appendStack({ count: 8 });
    const original = Array.from(element.querySelectorAll("tb-scene"));
    const select = element.querySelector("select");
    select.focus();
    select.value = "4";
    change(select);
    expect(visibleScenes(element)).toEqual([original[4]]);
    expect(element.dataset.scene).toBe("5");
    expect(element.querySelector(".tb-stack__scene-caption").textContent).toBe("Step 5");
    expect(button(element, "previous").disabled).toBe(false);
    expect(button(element, "next").disabled).toBe(false);
    expect(document.activeElement).toBe(select);
    expect(select.title).toBe("5 of 8: Step 5");
    expect(element.querySelector(".tb-stack__status").textContent).toBe("");
    select.value = "7";
    change(select);
    expect(visibleScenes(element)).toEqual([original[7]]);
    expect(button(element, "next").disabled).toBe(true);
    expect(button(element, "last").disabled).toBe(true);
    expect(document.activeElement).toBe(select);
    click(button(element, "first"));
    expect(select.value).toBe("0");
    expect(element.querySelector(".tb-stack__status").textContent).toBe("Scene 1 of 8: Step 1");
  });

  it("ignores a selector change with no selected option", () => {
    const element = appendStack();
    click(button(element, "next"));
    const select = element.querySelector("select");
    select.selectedIndex = -1;
    change(select);
    expect(element.dataset.scene).toBe("2");
  });

  it("names the carousel and its slides, following the visible caption on navigation", () => {
    const element = createStack();
    const heading = document.createElement("p");
    heading.id = "example-caption";
    heading.className = "tb-stack__caption";
    heading.textContent = 'Inspect <values> & "labels"';
    element.prepend(heading);
    element.setAttribute("aria-labelledby", heading.id);
    element.removeAttribute("aria-label");
    document.body.append(element);
    const scenes = Array.from(element.querySelectorAll("tb-scene"));
    const caption = element.querySelector(".tb-stack__scene-caption");
    const expectCurrentName = (index) => {
      expect(scenes[index].getAttribute("aria-labelledby")).toBe(caption.id);
      expect(document.getElementById(caption.id).textContent).toBe(`Step ${index + 1}`);
      expect(caption.hidden).toBe(false);
      expect(scenes[index].hasAttribute("aria-label")).toBe(false);
      scenes.forEach((scene, number) => {
        expect(scene.getAttribute("role")).toBe("group");
        expect(scene.getAttribute("aria-roledescription")).toBe("slide");
        if (number !== index) {
          expect(scene.hidden).toBe(true);
          expect(scene.hasAttribute("aria-labelledby")).toBe(false);
          expect(scene.getAttribute("aria-label")).toBe(`Step ${number + 1}`);
        }
      });
    };
    expect(element.getAttribute("role")).toBe("group");
    expect(element.getAttribute("aria-roledescription")).toBe("carousel");
    expect(document.getElementById(element.getAttribute("aria-labelledby"))).toBe(heading);
    expectCurrentName(0);
    click(button(element, "next"));
    expectCurrentName(1);
    click(button(element, "first"));
    expectCurrentName(0);
  });

  it("names uncaptioned slides by position and count without stale label references", () => {
    const element = createStack();
    const script = element.querySelector('script[type="application/json"]');
    const config = JSON.parse(script.textContent);
    config.scenes[0].caption = "";
    config.scenes[2].caption = "";
    script.textContent = JSON.stringify(config);
    document.body.append(element);
    const scenes = element.querySelectorAll("tb-scene");
    expect(element.getAttribute("aria-label")).toBe("Scene walkthrough");
    expect(scenes[0].getAttribute("aria-label")).toBe("1 of 3");
    expect(scenes[0].hasAttribute("aria-labelledby")).toBe(false);
    expect(scenes[2].getAttribute("aria-label")).toBe("3 of 3");
    click(button(element, "next"));
    expect(scenes[1].getAttribute("aria-labelledby")).toBe("example-scene-caption");
    click(button(element, "last"));
    expect(scenes[1].getAttribute("aria-label")).toBe("Step 2");
    expect(scenes[1].hasAttribute("aria-labelledby")).toBe(false);
    expect(scenes[2].getAttribute("aria-label")).toBe("3 of 3");
    expect(scenes[2].hasAttribute("aria-labelledby")).toBe(false);
    expect(element.querySelector(".tb-stack__scene-caption").hidden).toBe(true);
  });

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
    expect(controls.querySelector("select").value).toBe("1");
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
    const ids = Array.from(element.querySelectorAll("[id]")).map((item) => item.id);
    expect(new Set(ids).size).toBe(ids.length);
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
    expect(element.querySelector("select").hidden).toBe(true);
    element.querySelectorAll("button").forEach((control) => expect(control.disabled).toBe(true));
    expect(element.querySelector(".tb-stack__status").textContent).toBe("Scene 1 of 1: Step 1");
    expect(element.getAttribute("aria-roledescription")).toBe("carousel");
    expect(visibleScenes(element)[0].getAttribute("aria-roledescription")).toBe("slide");
  });

  it.each(["not JSON", "null", '{"version":2,"scenes":[]}', '{"version":1,"scenes":[]}'])(
    "retains all static scenes when configuration is invalid: %s", (config) => {
      const element = appendStack({ config });
      expect(visibleScenes(element)).toHaveLength(3);
      expect(element.dataset.enhanced).toBeUndefined();
      expect(element.hasAttribute("aria-roledescription")).toBe(false);
      element.querySelectorAll("tb-scene").forEach((scene) => {
        expect(scene.hasAttribute("aria-roledescription")).toBe(false);
        expect(document.getElementById(scene.getAttribute("aria-labelledby")).hidden).toBe(false);
      });
      expect(element.querySelector(".tb-stack__controls").hidden).toBe(true);
      expect(element.querySelector("select").hidden).toBe(true);
      expect(element.querySelector("select").options).toHaveLength(0);
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

  it("retains static scenes if the native selector is missing", () => {
    const element = createStack();
    element.querySelector("select").remove();
    document.body.append(element);
    expect(visibleScenes(element)).toHaveLength(3);
    expect(element.dataset.enhanced).toBeUndefined();
  });

  it("retains named static groups when the shared caption has no reference target", () => {
    const element = createStack();
    element.querySelector(".tb-stack__scene-caption").removeAttribute("id");
    document.body.append(element);
    expect(element.dataset.enhanced).toBeUndefined();
    expect(element.hasAttribute("aria-roledescription")).toBe(false);
    expect(visibleScenes(element)).toHaveLength(3);
    element.querySelectorAll("tb-scene").forEach((scene) => {
      expect(scene.hasAttribute("aria-roledescription")).toBe(false);
      expect(document.getElementById(scene.getAttribute("aria-labelledby")).hidden).toBe(false);
    });
  });

  it("keeps stacks independent even when semantic objects have the same names", () => {
    const first = appendStack();
    const second = appendStack({ id: "second" });
    click(button(first, "last"));
    expect(first.dataset.scene).toBe("3");
    expect(second.dataset.scene).toBe("1");
    expect(visibleScenes(first)[0].getAttribute("aria-labelledby")).toBe("example-scene-caption");
    expect(visibleScenes(second)[0].getAttribute("aria-labelledby")).toBe("second-scene-caption");
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
    expect(second.querySelector("select").value).toBe("2");
    expect(first.querySelector("select").value).toBe("0");
    expect(button(second, "next").disabled).toBe(true);
    expect(button(second, "previous").disabled).toBe(false);
  });

  it("initializes to the scene containing the current document target", () => {
    window.history.replaceState({}, "", "#example-pointer-2");
    const element = appendStack();
    expect(visibleScenes(element)[0].id).toBe("example-scene-2");
    expect(element.querySelector("select").value).toBe("2");
  });

  it("reveals inactive scene content on hash changes and repeated same-hash links", () => {
    const element = appendStack();
    window.history.replaceState({}, "", "#example-array-2");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    expect(element.dataset.scene).toBe("3");
    expect(element.querySelector("select").value).toBe("2");
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
    expect(element.getAttribute("aria-roledescription")).toBe("carousel");
    expect(visibleScenes(element)[0].getAttribute("aria-labelledby")).toBe("example-scene-caption");
    const select = element.querySelector("select");
    expect(element.querySelectorAll("select")).toHaveLength(1);
    expect(select.options).toHaveLength(3);
    select.value = "1";
    change(select);
    expect(show).toHaveBeenCalledTimes(2);
    expect(element.dataset.scene).toBe("2");
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
