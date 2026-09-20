import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { change, click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-choice.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendChoice({ multiple = false, random = false } = {}) {
  const type = multiple ? "checkbox" : "radio";
  const element = document.createElement("tb-choice");
  element.id = "choice-example";
  element.setAttribute("mode", multiple ? "multiple" : "single");
  if (random) {
    element.setAttribute("random", "true");
  }
  element.innerHTML = `
    <div id="choice-example-prompt" class="tb-choice__prompt">
      <p>Select the correct answer.</p>
    </div>
    <div class="tb-choice__options" role="group" aria-labelledby="choice-example-prompt">
      <div class="tb-choice__option" data-correct="false">
        <div class="tb-choice__row">
          <input id="choice-option-0" class="tb-choice__input" type="${type}" name="choice-example-answer" value="0">
          <div class="tb-choice__answer"><p><label class="tb-choice__label" for="choice-option-0">A</label></p><div class="tb-choice__details"><pre>Example code</pre><p>More detail.</p></div></div>
        </div>
        <div class="tb-choice__feedback"><p>A is not correct.</p></div>
      </div>
      <div class="tb-choice__option" data-correct="true">
        <div class="tb-choice__row">
          <input id="choice-option-1" class="tb-choice__input" type="${type}" name="choice-example-answer" value="1">
          <div class="tb-choice__answer"><p><label class="tb-choice__label" for="choice-option-1">B</label></p><div class="tb-choice__details"><pre>Example code</pre><p>More detail.</p></div></div>
        </div>
        <div class="tb-choice__feedback"><p>B is correct.</p></div>
      </div>
      ${
        multiple
          ? `<div class="tb-choice__option" data-correct="true">
              <div class="tb-choice__row">
                <input id="choice-option-2" class="tb-choice__input" type="${type}" name="choice-example-answer" value="2">
                <div class="tb-choice__answer"><p><label class="tb-choice__label" for="choice-option-2">C</label></p><div class="tb-choice__details"><pre>Example code</pre><p>More detail.</p></div></div>
              </div>
              <div class="tb-choice__feedback"><p>C is also correct.</p></div>
            </div>`
          : ""
      }
    </div>
    <div class="tb-choice__actions">
      <button type="button" class="tb-choice__check">Check answer</button>
      <p class="tb-choice__status" role="status" aria-live="polite"></p>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

describe("tb-choice Web Component", () => {
  it.each([false, true])("selects only through the label or input (multiple=%s)", (multiple) => {
    const element = appendChoice({ multiple, random: true });
    const option = element.querySelector('.tb-choice__option[data-correct="false"]');
    const input = option.querySelector("input");
    option.querySelector("pre").click();
    option.querySelector(".tb-choice__details p").click();
    expect(input.checked).toBe(false);
    option.querySelector("label").click();
    expect(input.checked).toBe(true);
    expect(input.labels[0]).toBe(option.querySelector("label"));
    element.querySelector(".tb-choice__check").click();
    expect(element.querySelector(".tb-choice__status").textContent).toBe("Not quite.");
    const correct = element.querySelector('.tb-choice__option[data-correct="true"]');
    correct.querySelector("label").click();
    expect(element.querySelector(".tb-choice__status").textContent).toBe("");
    expect(option.querySelector(".tb-choice__feedback").hidden).toBe(true);
  });

  it("hides feedback on initialization", () => {
    const element = appendChoice();

    expect(customElements.get("tb-choice")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    element.querySelectorAll(".tb-choice__feedback").forEach((feedback) => {
      expect(feedback.hidden).toBe(true);
    });
  });

  it("checks a correct radio answer and shows selected feedback", () => {
    const element = appendChoice();
    const inputs = element.querySelectorAll(".tb-choice__input");
    inputs[1].checked = true;
    change(inputs[1]);

    click(element.querySelector(".tb-choice__check"));

    expect(element.querySelector(".tb-choice__status").textContent).toBe("Correct.");
    expect(element.querySelectorAll(".tb-choice__feedback")[0].hidden).toBe(true);
    expect(element.querySelectorAll(".tb-choice__feedback")[1].hidden).toBe(false);
    expect(element.querySelectorAll(".tb-choice__option")[1].classList.contains("tb-choice__option--correct")).toBe(true);
  });

  it("checks an incorrect radio answer and shows selected feedback", () => {
    const element = appendChoice();
    const inputs = element.querySelectorAll(".tb-choice__input");
    inputs[0].checked = true;
    change(inputs[0]);

    click(element.querySelector(".tb-choice__check"));

    expect(element.querySelector(".tb-choice__status").textContent).toBe("Not quite.");
    expect(element.querySelectorAll(".tb-choice__feedback")[0].hidden).toBe(false);
    expect(element.querySelectorAll(".tb-choice__feedback")[1].hidden).toBe(true);
    expect(element.querySelectorAll(".tb-choice__option")[0].classList.contains("tb-choice__option--incorrect")).toBe(true);
  });

  it("requires an exact checkbox selection for multiple answer choices", () => {
    const element = appendChoice({ multiple: true });
    const inputs = element.querySelectorAll(".tb-choice__input");
    inputs[1].checked = true;
    change(inputs[1]);

    click(element.querySelector(".tb-choice__check"));
    expect(element.querySelector(".tb-choice__status").textContent).toBe("Not quite.");

    inputs[2].checked = true;
    change(inputs[2]);
    click(element.querySelector(".tb-choice__check"));
    expect(element.querySelector(".tb-choice__status").textContent).toBe("Correct.");
    expect(element.querySelectorAll(".tb-choice__feedback")[1].hidden).toBe(false);
    expect(element.querySelectorAll(".tb-choice__feedback")[2].hidden).toBe(false);
  });

  it("randomizes answer order when requested", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendChoice({ multiple: true, random: true });
    const answers = Array.from(element.querySelectorAll(".tb-choice__label")).map((answer) =>
      answer.textContent.trim(),
    );

    expect(answers).toEqual(["B", "C", "A"]);
    randomMock.mockRestore();
  });

  it("reports an empty selection", () => {
    const element = appendChoice();

    click(element.querySelector(".tb-choice__check"));

    expect(element.querySelector(".tb-choice__status").textContent).toBe("Choose an answer before checking.");
  });
});
