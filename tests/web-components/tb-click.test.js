import { beforeAll, beforeEach, describe, expect, it } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-click.js");
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
    expect(incorrect.classList.contains("tb-click__target--incorrect")).toBe(true);
  });
});
