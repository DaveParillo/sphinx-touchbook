import { beforeAll, beforeEach, describe, expect, it } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-blank.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendBlank({ caseSensitive = false, trim = true, regex = false } = {}) {
  const element = document.createElement("tb-blank");
  element.id = "blank-example";
  element.setAttribute("case-sensitive", caseSensitive ? "true" : "false");
  element.setAttribute("trim", trim ? "true" : "false");
  element.innerHTML = `
    <div class="tb-blank__prompt">
      <p>The capital is <input class="tb-blank__input" type="text" data-blank-id="blank1"></p>
    </div>
    <script type="application/json" class="tb-blank__config">
      {
        "blanks": ["blank1"],
        "answers": {
          "blank1": {
            "matches": ${regex ? '["\\\\d+"]' : '["Paris", "City of Paris"]'},
            "hints": [{"value": "London", "feedback": "London is the capital of the United Kingdom."}],
            "feedback": "Correct.",
            "incorrect": "Try again.",
            "regex": ${regex ? "true" : "false"}
          }
        }
      }
    </script>
    <div class="tb-blank__actions">
      <button type="button" class="tb-blank__check">Check answer</button>
      <p class="tb-blank__status" role="status" aria-live="polite"></p>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

describe("tb-blank Web Component", () => {
  it("accepts case-insensitive trimmed matches by default", () => {
    const element = appendBlank();
    const input = element.querySelector(".tb-blank__input");
    input.value = " paris ";
    click(element.querySelector(".tb-blank__check"));

    expect(customElements.get("tb-blank")).toBeTypeOf("function");
    expect(element.querySelector(".tb-blank__status").textContent).toBe("Correct.");
    expect(input.classList.contains("tb-blank__input--correct")).toBe(true);
  });

  it("can require case-sensitive matching", () => {
    const element = appendBlank({ caseSensitive: true });
    const input = element.querySelector(".tb-blank__input");
    input.value = "paris";
    click(element.querySelector(".tb-blank__check"));

    expect(element.querySelector(".tb-blank__status").textContent).toBe("Try again.");
    expect(input.classList.contains("tb-blank__input--incorrect")).toBe(true);
  });

  it("uses targeted hints for known wrong answers", () => {
    const element = appendBlank();
    const input = element.querySelector(".tb-blank__input");
    input.value = "London";
    click(element.querySelector(".tb-blank__check"));

    expect(element.querySelector(".tb-blank__status").textContent).toBe(
      "London is the capital of the United Kingdom.",
    );
  });

  it("uses regex matches when configured", () => {
    const element = appendBlank({ regex: true });
    const input = element.querySelector(".tb-blank__input");
    input.value = "187";
    click(element.querySelector(".tb-blank__check"));

    expect(element.querySelector(".tb-blank__status").textContent).toBe("Correct.");
  });

  it("clears feedback when the input changes", () => {
    const element = appendBlank();
    const input = element.querySelector(".tb-blank__input");
    input.value = "London";
    click(element.querySelector(".tb-blank__check"));

    expect(input.classList.contains("tb-blank__input--incorrect")).toBe(true);
    input.value = "Paris";
    input.dispatchEvent(new Event("input", { bubbles: true }));

    expect(element.querySelector(".tb-blank__status").textContent).toBe("");
    expect(input.classList.contains("tb-blank__input--incorrect")).toBe(false);
  });
});
