import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-parsons.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendParsons({ noIndent = false } = {}) {
  const element = document.createElement("tb-parsons");
  element.id = "parsons-example";
  element.dataset.noIndent = noIndent ? "true" : "false";
  element.innerHTML = `
    <ol class="tb-parsons__list" aria-label="Code fragments">
      <li class="tb-parsons__item" data-order="0" data-indent="0" data-current-indent="0" data-distractor="false">
        <pre class="tb-parsons__code"><code>def findmax(alist):</code></pre>
        ${controls()}
      </li>
      <li class="tb-parsons__item" data-order="1" data-indent="4" data-current-indent="0" data-distractor="false">
        <pre class="tb-parsons__code"><code>if len(alist) == 0:
    return None</code></pre>
        ${controls()}
      </li>
      <li class="tb-parsons__item" data-order="2" data-indent="4" data-current-indent="0" data-distractor="false">
        <pre class="tb-parsons__code"><code>return curmax</code></pre>
        ${controls()}
      </li>
      <li class="tb-parsons__item" data-order="3" data-indent="4" data-current-indent="0" data-distractor="true">
        <pre class="tb-parsons__code"><code>return item</code></pre>
        ${controls()}
      </li>
    </ol>
    <div class="tb-parsons__actions">
      <button type="button" class="tb-parsons__check">Check answer</button>
      <p class="tb-parsons__status" role="status" aria-live="polite"></p>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

function controls() {
  return `
    <div class="tb-parsons__controls" aria-label="Arrange fragment">
      <button type="button" class="tb-parsons__move tb-parsons__move-up">↑</button>
      <button type="button" class="tb-parsons__move tb-parsons__move-down">↓</button>
      <button type="button" class="tb-parsons__indent tb-parsons__outdent">←</button>
      <button type="button" class="tb-parsons__indent tb-parsons__indent-in">→</button>
      <button type="button" class="tb-parsons__toggle" aria-pressed="true" aria-label="Included in solution">
        <span class="tb-parsons__toggle-icon" aria-hidden="true">✓</span>
        <span class="tb-parsons__toggle-label">Use</span>
      </button>
    </div>
  `;
}

function orderValues(element) {
  return Array.from(element.querySelectorAll(".tb-parsons__item")).map((item) => item.dataset.order);
}

function itemForOrder(element, order) {
  return Array.from(element.querySelectorAll(".tb-parsons__item")).find((item) => item.dataset.order === order);
}

function setOrder(element, orders) {
  const list = element.querySelector(".tb-parsons__list");
  orders.forEach((order) => list.append(itemForOrder(element, order)));
}

describe("tb-parsons Web Component", () => {
  it("shuffles fragments on initialization", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendParsons();

    expect(customElements.get("tb-parsons")).toBeTypeOf("function");
    expect(orderValues(element)).not.toEqual(["0", "1", "2", "3"]);
    randomMock.mockRestore();
  });

  it("moves fragments with native buttons", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendParsons();
    randomMock.mockRestore();

    setOrder(element, ["1", "0", "2", "3"]);
    click(itemForOrder(element, "0").querySelector(".tb-parsons__move-up"));

    expect(orderValues(element).slice(0, 3)).toEqual(["0", "1", "2"]);
    expect(element.querySelector(".tb-parsons__item .tb-parsons__move-up").disabled).toBe(true);
  });

  it("changes indentation with indent controls", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendParsons();
    randomMock.mockRestore();

    const item = itemForOrder(element, "1");
    click(item.querySelector(".tb-parsons__indent-in"));
    expect(item.dataset.currentIndent).toBe("4");
    expect(item.style.getPropertyValue("--tb-parsons-indent")).toBe("4");
    click(item.querySelector(".tb-parsons__outdent"));
    expect(item.dataset.currentIndent).toBe("0");
  });

  it("toggles a fragment between use and skip states", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendParsons();
    randomMock.mockRestore();

    const item = itemForOrder(element, "3");
    const toggle = item.querySelector(".tb-parsons__toggle");
    click(toggle);

    expect(toggle.getAttribute("aria-pressed")).toBe("false");
    expect(toggle.getAttribute("aria-label")).toBe("Not included in solution");
    expect(item.classList.contains("tb-parsons__item--excluded")).toBe(true);
    expect(item.querySelector(".tb-parsons__toggle-label").textContent).toBe("Skip");
  });

  it("reports correct order, indentation, and skipped distractors", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendParsons();
    randomMock.mockRestore();

    setOrder(element, ["0", "1", "2", "3"]);
    click(itemForOrder(element, "1").querySelector(".tb-parsons__indent-in"));
    click(itemForOrder(element, "2").querySelector(".tb-parsons__indent-in"));
    click(itemForOrder(element, "3").querySelector(".tb-parsons__toggle"));
    click(element.querySelector(".tb-parsons__check"));

    expect(element.querySelector(".tb-parsons__status").textContent).toBe("Correct.");
    expect(itemForOrder(element, "0").classList.contains("tb-parsons__item--correct")).toBe(true);
  });

  it("reports incorrect answers when a distractor is included", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendParsons();
    randomMock.mockRestore();

    setOrder(element, ["0", "1", "2", "3"]);
    click(itemForOrder(element, "1").querySelector(".tb-parsons__indent-in"));
    click(itemForOrder(element, "2").querySelector(".tb-parsons__indent-in"));
    click(element.querySelector(".tb-parsons__check"));

    expect(element.querySelector(".tb-parsons__status").textContent).toBe(
      "Not quite. Check the order, indentation, and skipped fragments."
    );
    expect(itemForOrder(element, "3").classList.contains("tb-parsons__item--incorrect")).toBe(true);
  });

  it("ignores indentation when no-indent is set", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendParsons({ noIndent: true });
    randomMock.mockRestore();

    setOrder(element, ["0", "1", "2", "3"]);
    click(itemForOrder(element, "3").querySelector(".tb-parsons__toggle"));
    click(element.querySelector(".tb-parsons__check"));

    expect(element.querySelector(".tb-parsons__status").textContent).toBe("Correct.");
  });
});
