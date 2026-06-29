import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-micro-parsons.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendMicroParsons({ distractors = true } = {}) {
  const element = document.createElement("tb-micro-parsons");
  element.id = "micro-parsons-example";
  element.dataset.hasDistractors = distractors ? "true" : "false";
  element.innerHTML = `
    <div class="tb-micro-parsons__workspace">
      <div class="tb-micro-parsons__row">
        <p class="tb-micro-parsons__row-label">Tokens</p>
        <ol class="tb-micro-parsons__tokens tb-micro-parsons__source" aria-label="Available tokens">
          ${token("0", "false", "int")}
          ${token("1", "false", "x")}
          ${token("2", "false", "=")}
          ${token("3", "false", "42")}
          ${token("4", "false", ";")}
          ${distractors ? token("5", "true", "float") : ""}
        </ol>
      </div>
      <div class="tb-micro-parsons__row">
        <p class="tb-micro-parsons__row-label">Answer</p>
        <ol class="tb-micro-parsons__tokens tb-micro-parsons__target" aria-label="Answer tokens"></ol>
      </div>
    </div>
    <div class="tb-micro-parsons__actions">
      <button type="button" class="tb-micro-parsons__check">Check answer</button>
      <p class="tb-micro-parsons__status" role="status" aria-live="polite"></p>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

function token(order, distractor, label) {
  return `
    <li class="tb-micro-parsons__token" data-order="${order}" data-distractor="${distractor}" data-location="source">
      <button type="button" class="tb-micro-parsons__token-button" aria-label="Move ${label} to answer">
        <code class="tb-micro-parsons__content">${label}</code>
      </button>
    </li>
  `;
}

function sourceValues(element) {
  return Array.from(element.querySelectorAll(".tb-micro-parsons__source .tb-micro-parsons__token"))
    .map((item) => item.dataset.order);
}

function targetValues(element) {
  return Array.from(element.querySelectorAll(".tb-micro-parsons__target .tb-micro-parsons__token"))
    .map((item) => item.dataset.order);
}

function tokenForOrder(element, order) {
  return Array.from(element.querySelectorAll(".tb-micro-parsons__token")).find((item) => item.dataset.order === order);
}

function clickToken(element, order) {
  click(tokenForOrder(element, order).querySelector(".tb-micro-parsons__token-button"));
}

describe("tb-micro-parsons Web Component", () => {
  it("shuffles source tokens on initialization", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendMicroParsons();

    expect(customElements.get("tb-micro-parsons")).toBeTypeOf("function");
    expect(sourceValues(element)).not.toEqual(["0", "1", "2", "3", "4", "5"]);
    expect(targetValues(element)).toEqual([]);
    randomMock.mockRestore();
  });

  it("moves a token from source to target and back with one button", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendMicroParsons({ distractors: false });
    randomMock.mockRestore();

    clickToken(element, "0");

    expect(targetValues(element)).toEqual(["0"]);
    expect(tokenForOrder(element, "0").dataset.location).toBe("target");
    expect(tokenForOrder(element, "0").querySelector("button").getAttribute("aria-pressed")).toBe("true");
    expect(tokenForOrder(element, "0").querySelector("button").getAttribute("aria-label")).toBe("Move int to tokens");

    clickToken(element, "0");

    expect(targetValues(element)).toEqual([]);
    expect(sourceValues(element)).toContain("0");
    expect(tokenForOrder(element, "0").dataset.location).toBe("source");
  });

  it("reports correct order when distractors remain in source", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendMicroParsons();
    randomMock.mockRestore();

    ["0", "1", "2", "3", "4"].forEach((order) => clickToken(element, order));
    click(element.querySelector(".tb-micro-parsons__check"));

    expect(element.querySelector(".tb-micro-parsons__status").textContent).toBe("Correct.");
    expect(tokenForOrder(element, "0").classList.contains("tb-micro-parsons__token--correct")).toBe(true);
    expect(tokenForOrder(element, "5").dataset.location).toBe("source");
  });

  it("reports incorrect order when a distractor is moved to target", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendMicroParsons();
    randomMock.mockRestore();

    ["0", "1", "2", "3", "4", "5"].forEach((order) => clickToken(element, order));
    click(element.querySelector(".tb-micro-parsons__check"));

    expect(element.querySelector(".tb-micro-parsons__status").textContent).toBe(
      "Not quite. Move the needed tokens into the answer row in order."
    );
    expect(tokenForOrder(element, "5").classList.contains("tb-micro-parsons__token--incorrect")).toBe(true);
  });
});
