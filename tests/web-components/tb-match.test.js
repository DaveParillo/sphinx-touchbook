import { beforeAll, beforeEach, describe, expect, it } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-match.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendMatch() {
  const element = document.createElement("tb-match");
  element.id = "match-example";
  element.innerHTML = `
    <div class="tb-match__prompt"><p>Match each term.</p></div>
    <div class="tb-match__choices">
      <div class="tb-match__choice" data-answer="0">
        <label id="match-example-source-0" class="tb-match__source" for="match-example-select-0">compiler</label>
        <select id="match-example-select-0" class="tb-match__select" data-answer="0" aria-labelledby="match-example-source-0">
          <option value="">Choose a definition</option>
          <option value="0">Translates source.</option>
          <option value="1">Executes source.</option>
          <option value="2">Combines objects.</option>
        </select>
      </div>
      <div class="tb-match__choice" data-answer="1">
        <label id="match-example-source-1" class="tb-match__source" for="match-example-select-1">interpreter</label>
        <select id="match-example-select-1" class="tb-match__select" data-answer="1" aria-labelledby="match-example-source-1">
          <option value="">Choose a definition</option>
          <option value="0">Translates source.</option>
          <option value="1">Executes source.</option>
          <option value="2">Combines objects.</option>
        </select>
      </div>
      <div class="tb-match__choice" data-answer="2">
        <label id="match-example-source-2" class="tb-match__source" for="match-example-select-2">linker</label>
        <select id="match-example-select-2" class="tb-match__select" data-answer="2" aria-labelledby="match-example-source-2">
          <option value="">Choose a definition</option>
          <option value="0">Translates source.</option>
          <option value="1">Executes source.</option>
          <option value="2">Combines objects.</option>
        </select>
      </div>
    </div>
    <div class="tb-match__actions">
      <button type="button" class="tb-match__check" disabled>Check Me</button>
      <p class="tb-match__status" role="status" aria-live="polite"></p>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

function setSelect(select, value) {
  select.value = value;
  select.dispatchEvent(new Event("change", { bubbles: true }));
}

describe("tb-match Web Component", () => {
  it("enables checking when select controls are present", () => {
    const element = appendMatch();
    const selects = element.querySelectorAll(".tb-match__select");
    const check = element.querySelector(".tb-match__check");

    expect(customElements.get("tb-match")).toBeTypeOf("function");
    expect(check.disabled).toBe(false);

    setSelect(selects[0], "0");
    setSelect(selects[1], "1");
    expect(check.disabled).toBe(false);
  });

  it("reports correct matches", () => {
    const element = appendMatch();
    const selects = element.querySelectorAll(".tb-match__select");

    setSelect(selects[0], "0");
    setSelect(selects[1], "1");
    setSelect(selects[2], "2");
    click(element.querySelector(".tb-match__check"));

    expect(element.querySelector(".tb-match__status").textContent).toBe("Correct.");
    expect(selects[0].classList.contains("tb-match__select--correct")).toBe(true);
    expect(selects[0].closest(".tb-match__choice").classList.contains("tb-match__choice--correct")).toBe(true);
  });

  it("reports incorrect matches", () => {
    const element = appendMatch();
    const selects = element.querySelectorAll(".tb-match__select");

    setSelect(selects[0], "1");
    setSelect(selects[1], "0");
    setSelect(selects[2], "2");
    click(element.querySelector(".tb-match__check"));

    expect(element.querySelector(".tb-match__status").textContent).toBe(
      "Not quite: You got 1 correct and 2 incorrect out of 3. You left 0 blank. Try again!"
    );
    expect(selects[0].classList.contains("tb-match__select--incorrect")).toBe(true);
    expect(selects[0].closest(".tb-match__choice").classList.contains("tb-match__choice--incorrect")).toBe(true);
  });

  it("reports blank selections separately from incorrect selections", () => {
    const element = appendMatch();
    const selects = element.querySelectorAll(".tb-match__select");

    setSelect(selects[0], "0");
    setSelect(selects[1], "0");
    click(element.querySelector(".tb-match__check"));

    expect(element.querySelector(".tb-match__status").textContent).toBe(
      "Not quite: You got 1 correct and 1 incorrect out of 3. You left 1 blank. Try again!"
    );
    expect(selects[1].classList.contains("tb-match__select--incorrect")).toBe(true);
    expect(selects[2].classList.contains("tb-match__select--incorrect")).toBe(false);
  });

  it("clears feedback when a selection changes", () => {
    const element = appendMatch();
    const selects = element.querySelectorAll(".tb-match__select");

    setSelect(selects[0], "1");
    setSelect(selects[1], "0");
    setSelect(selects[2], "2");
    click(element.querySelector(".tb-match__check"));

    expect(selects[0].classList.contains("tb-match__select--incorrect")).toBe(true);

    setSelect(selects[0], "0");

    expect(element.querySelector(".tb-match__status").textContent).toBe("");
    expect(selects[0].classList.contains("tb-match__select--incorrect")).toBe(false);
  });
});
