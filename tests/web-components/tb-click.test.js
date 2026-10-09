import { beforeAll, beforeEach, describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-click.js");
  const style = document.createElement("style");
  style.textContent = readFileSync(resolve("src/sphinx_touchbook/static/tb-click.css"), "utf8");
  document.head.append(style);
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendClick({ hints = "false", includeHintButton = true } = {}) {
  const element = document.createElement("tb-click");
  element.id = "click-example";
  element.setAttribute("hints", hints);
  element.innerHTML = `
    <div class="tb-click__prompt">
      <p>Click the comparison operator.</p>
    </div>
    <div class="highlight-none notranslate tb-click__source">
      <div class="highlight"><pre>WHERE age <button type="button" class="tb-click__target" data-correct="true" data-feedback-id="click-example-feedback-0" aria-describedby="click-example-feedback-0">&gt;=</button> 18;</pre></div>
    </div>
    <div id="click-example-feedback-0" class="tb-click__feedback" data-correct="true" hidden>
      <p>Correct.</p>
    </div>
    <div id="click-example-feedback-1" class="tb-click__feedback" data-correct="false" hidden>
      <p>Not this one.</p>
    </div>
    <button type="button" class="tb-click__target" data-correct="false" data-feedback-id="click-example-feedback-1" aria-describedby="click-example-feedback-1">WHERE</button>
    ${includeHintButton ? '<button type="button" class="tb-click__hint-toggle">Show Hints</button>' : ""}
    <p class="tb-click__status" role="status" aria-live="polite"></p>
  `;
  document.body.appendChild(element);
  return element;
}

describe("tb-click Web Component", () => {
  it("hides feedback on initialization", () => {
    const element = appendClick();

    expect(customElements.get("tb-click")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(element.dataset.hintsVisible).toBe("false");
    expect(element.querySelector(".tb-click__hint-toggle").textContent).toBe("Show Hints");
    element.querySelectorAll(".tb-click__feedback").forEach((feedback) => {
      expect(feedback.hidden).toBe(true);
    });
    element.querySelectorAll(".tb-click__target").forEach((target) => {
      expect(target.hasAttribute("aria-describedby")).toBe(false);
    });
  });

  it("toggles hints with show and hide labels", () => {
    const element = appendClick();
    const toggle = element.querySelector(".tb-click__hint-toggle");

    click(toggle);
    expect(element.dataset.hintsVisible).toBe("true");
    expect(toggle.textContent).toBe("Hide Hints");
    expect(toggle.getAttribute("aria-pressed")).toBe("true");

    click(toggle);
    expect(element.dataset.hintsVisible).toBe("false");
    expect(toggle.textContent).toBe("Show Hints");
    expect(toggle.getAttribute("aria-pressed")).toBe("false");
  });

  it("initializes with hints shown when requested", () => {
    const element = appendClick({ hints: "true" });
    const toggle = element.querySelector(".tb-click__hint-toggle");

    expect(element.dataset.hintsVisible).toBe("true");
    expect(toggle.textContent).toBe("Hide Hints");
  });

  it("hides the hint button when hints are never available", () => {
    const element = appendClick({ hints: "never" });

    expect(element.dataset.hintsVisible).toBe("false");
    expect(element.querySelector(".tb-click__hint-toggle").hidden).toBe(true);
  });

  it("shows correct feedback for a correct target", () => {
    const element = appendClick();
    const target = element.querySelector('.tb-click__target[data-correct="true"]');

    click(target);

    expect(element.querySelector(".tb-click__status").textContent).toBe("Correct.");
    expect(element.querySelector("#click-example-feedback-0").hidden).toBe(false);
    expect(target.getAttribute("aria-pressed")).toBe("true");
    expect(target.getAttribute("aria-describedby")).toBe("click-example-feedback-0");
    expect(target.classList.contains("tb-click__target--correct")).toBe(true);
  });

  it("shows incorrect feedback and clears the previous selection", () => {
    const element = appendClick();
    const correct = element.querySelector('.tb-click__target[data-correct="true"]');
    const incorrect = element.querySelector('.tb-click__target[data-correct="false"]');

    click(correct);
    click(incorrect);

    expect(element.querySelector(".tb-click__status").textContent).toBe("Not quite.");
    expect(element.querySelector("#click-example-feedback-0").hidden).toBe(true);
    expect(element.querySelector("#click-example-feedback-1").hidden).toBe(false);
    expect(correct.classList.contains("tb-click__target--correct")).toBe(false);
    expect(correct.hasAttribute("aria-describedby")).toBe(false);
    expect(incorrect.classList.contains("tb-click__target--incorrect")).toBe(true);
  });
});

function appendKeyedClick(kind, { hints = "false", shape = "ellipse" } = {}) {
  const element = document.createElement("tb-click");
  element.setAttribute("hints", hints);
  const shapes = {
    ellipse: '<ellipse rx="20" ry="10" fill="#add8e6"/>',
    polygon: '<polygon points="0,0 40,0 40,20 0,20" fill="#add8e6"/>',
    path: '<path d="M0,0 H40 V20 H0 Z" fill="#add8e6"/>',
  };
  element.innerHTML = `
    <div class="tb-click__source">
      ${kind === "array" ? `<tb-array><table><tbody><tr><td>
        <button type="button" class="tb-click__target" data-key="a" data-correct="false" data-feedback-id="keyed-feedback-a" aria-label="a: same">same</button>
        </td><td><button type="button" class="tb-click__target" data-key="b" data-correct="true" data-feedback-id="keyed-feedback-b" aria-label="b: same">same</button>
        </td></tr></tbody></table></tb-array>` : `<tb-graph><svg class="tb-click__diagram" role="group" aria-label="Graph diagram">
        <g role="button" tabindex="0" class="tb-click__target" data-key="a" data-correct="false" data-feedback-id="keyed-feedback-a" aria-label="a: same">${shapes[shape]}<text>same</text></g>
        <g role="button" tabindex="0" class="tb-click__target" data-key="b" data-correct="true" data-feedback-id="keyed-feedback-b" aria-label="b: same">${shapes[shape]}<text>same</text></g>
        <g class="node">${shapes[shape]}<text>Unselectable</text></g>
        <path class="relationship" d="M0,0 L20,20"/>
        </svg></tb-graph>`}
    </div>
    <div id="keyed-feedback-a" class="tb-click__feedback" hidden>Wrong key.</div>
    <div id="keyed-feedback-b" class="tb-click__feedback" hidden>Correct key.</div>
    <button type="button" class="tb-click__hint-toggle">Show Hints</button>
    <p class="tb-click__status" role="status"></p>`;
  document.body.append(element);
  return element;
}

describe("tb-click keyed sources", () => {
  it.each(["ellipse", "polygon", "path"])("toggles visible graph hints on %s shapes", (shape) => {
    const question = appendKeyedClick("graph", { shape });
    const targets = Array.from(question.querySelectorAll(`.tb-click__target ${shape}`));
    const toggle = question.querySelector(".tb-click__hint-toggle");
    const dash = (element) => getComputedStyle(element).getPropertyValue("stroke-dasharray");
    const original = targets.map(dash);

    click(toggle);
    expect(targets.map(dash)).toEqual(["4 3", "4 3"]);
    expect(targets.map((element) => getComputedStyle(element).strokeWidth)).toEqual(["2px", "2px"]);
    expect(targets.map((element) => element.getAttribute("fill"))).toEqual(["#add8e6", "#add8e6"]);
    expect(dash(question.querySelector(`.node ${shape}`))).not.toBe("4 3");
    expect(dash(question.querySelector(".relationship"))).not.toBe("4 3");
    expect(question.querySelectorAll('.tb-click__target[aria-pressed="true"]')).toHaveLength(0);
    expect(Array.from(question.querySelectorAll(".tb-click__feedback")).every((item) => item.hidden)).toBe(true);

    click(toggle);
    expect(targets.map(dash)).toEqual(original);
  });

  it.each(["true", "never"])("honors initial graph hints=%s", (hints) => {
    const question = appendKeyedClick("graph", { hints });
    const shape = question.querySelector(".tb-click__target ellipse");
    const visible = getComputedStyle(shape).getPropertyValue("stroke-dasharray") === "4 3";
    expect(visible).toBe(hints === "true");
    if (hints === "never") {
      expect(question.querySelector(".tb-click__hint-toggle").hidden).toBe(true);
    }
  });

  it.each(["a", "b"])("preserves graph feedback for %s while toggling hints", (key) => {
    const question = appendKeyedClick("graph");
    const target = question.querySelector(`[data-key="${key}"]`);
    const shape = target.querySelector("ellipse");
    const toggle = question.querySelector(".tb-click__hint-toggle");
    click(target);
    const feedbackStroke = getComputedStyle(shape).stroke;
    const feedbackFill = getComputedStyle(shape).fill;
    expect(feedbackStroke).toBe(key === "b" ? "rgb(46, 125, 50)" : "rgb(176, 0, 32)");
    for (let count = 0; count < 2; count += 1) {
      click(toggle);
      expect(getComputedStyle(shape).stroke).toBe(feedbackStroke);
      expect(getComputedStyle(shape).fill).toBe(feedbackFill);
      expect(target.getAttribute("aria-pressed")).toBe("true");
      expect(question.querySelector(`#keyed-feedback-${key}`).hidden).toBe(false);
    }
  });

  it.each(["array", "graph"])("grades %s keys independently of duplicate values", (kind) => {
    const question = appendKeyedClick(kind);
    const a = question.querySelector('[data-key="a"]');
    const b = question.querySelector('[data-key="b"]');
    expect(a.textContent).toBe(b.textContent);
    click(b.querySelector("text") || b);
    expect(question.querySelector(".tb-click__status").textContent).toBe("Correct.");
    expect(b.getAttribute("aria-pressed")).toBe("true");
    expect(question.querySelector("#keyed-feedback-b").hidden).toBe(false);
    expect(b.getAttribute("aria-describedby")).toBe("keyed-feedback-b");
    click(a);
    expect(question.querySelector(".tb-click__status").textContent).toBe("Not quite.");
    expect(b.getAttribute("aria-pressed")).toBe("false");
    expect(question.querySelector("#keyed-feedback-b").hidden).toBe(true);
    expect(question.querySelector("#keyed-feedback-a").hidden).toBe(false);
    expect(b.hasAttribute("aria-describedby")).toBe(false);
  });

  it.each(["Enter", " "])("activates a graph node with %j", (key) => {
    const question = appendKeyedClick("graph");
    const target = question.querySelector('[data-key="b"]');
    const event = new KeyboardEvent("keydown", { key, bubbles: true, cancelable: true });
    target.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(true);
    expect(question.querySelector(".tb-click__status").textContent).toBe("Correct.");
    expect(target.getAttribute("aria-pressed")).toBe("true");
  });

  it("keeps graph keyboard activation idempotent on reconnect", () => {
    const question = appendKeyedClick("graph");
    question.remove();
    document.body.append(question);
    let selections = 0;
    const select = question.selectTarget.bind(question);
    question.selectTarget = (target) => { selections += 1; select(target); };
    question.querySelector('[data-key="b"]').dispatchEvent(new KeyboardEvent("keydown", { key: "Enter" }));
    expect(selections).toBe(1);
  });
});
