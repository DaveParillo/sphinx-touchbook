import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, input, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-formula.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
  vi.restoreAllMocks();
});

function appendFormula({
  language = "javascript",
  source = "4 * y + 3 * x",
  tolerance = 0,
  parameters = {},
} = {}) {
  const element = document.createElement("tb-formula");
  element.id = "formula-example";
  element.dataset.endpoint = "https://example.test/jobe/index.php/restapi/runs";
  element.innerHTML = `
    <div class="tb-formula__prompt">
      If a small glass holds <span class="tb-formula__variable" data-variable="x">{{x}}</span>
      and a large glass holds <span class="tb-formula__variable" data-variable="y">{{y}}</span>,
      what is the total?
    </div>
    <script type="application/json" class="tb-formula__config">
      ${JSON.stringify({
        variables: {
          x: { min: 80, max: 90, integer: true },
          y: { min: 10, max: 20, integer: true },
        },
        formula: { language, source, parameters },
        tolerance,
      })}
    </script>
    <div class="tb-formula__answer">
      <label class="tb-formula__label">Answer <input class="tb-formula__input" type="text" inputmode="decimal"></label>
    </div>
    <div class="tb-formula__actions">
      <button type="button" class="tb-formula__check">Check answer</button>
      <button type="button" class="tb-formula__new-values">New values</button>
      <p class="tb-formula__status" role="status" aria-live="polite"></p>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

describe("tb-formula Web Component", () => {
  it("generates variable values on initialization", () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendFormula();

    expect(customElements.get("tb-formula")).toBeTypeOf("function");
    expect(element.querySelector('[data-variable="x"]').textContent).toBe("80");
    expect(element.querySelector('[data-variable="y"]').textContent).toBe("10");
  });

  it("checks a JavaScript formula locally", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendFormula();
    const answer = element.querySelector(".tb-formula__input");
    answer.value = "280";
    input(answer);
    click(element.querySelector(".tb-formula__check"));
    await Promise.resolve();

    expect(element.querySelector(".tb-formula__status").textContent).toBe("Correct.");
    expect(answer.classList.contains("tb-formula__input--correct")).toBe(true);
  });

  it("rejects non-numeric input before checking the formula", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendFormula();
    const answer = element.querySelector(".tb-formula__input");
    answer.value = "not a number";
    click(element.querySelector(".tb-formula__check"));
    await Promise.resolve();

    expect(element.querySelector(".tb-formula__status").textContent).toBe("Enter a numeric answer.");
    expect(answer.classList.contains("tb-formula__input--incorrect")).toBe(true);
  });

  it("accepts tolerance for numeric JavaScript formulas", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendFormula({ tolerance: 0.5 });
    const answer = element.querySelector(".tb-formula__input");
    answer.value = "280.4";
    click(element.querySelector(".tb-formula__check"));
    await Promise.resolve();

    expect(element.querySelector(".tb-formula__status").textContent).toBe("Correct.");
  });

  it("can check against a formula range", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendFormula({ source: "[359, 361]" });
    const answer = element.querySelector(".tb-formula__input");
    answer.value = "360";
    click(element.querySelector(".tb-formula__check"));
    await Promise.resolve();

    expect(element.querySelector(".tb-formula__status").textContent).toBe("Correct.");
  });

  it("can check against an object range", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendFormula({ source: "({ min: 279, max: 281 })" });
    const answer = element.querySelector(".tb-formula__input");
    answer.value = "280";
    click(element.querySelector(".tb-formula__check"));
    await Promise.resolve();

    expect(element.querySelector(".tb-formula__status").textContent).toBe("Correct.");
  });

  it("requests new values and clears the answer", () => {
    const randomMock = vi.spyOn(Math, "random");
    randomMock.mockReturnValueOnce(0).mockReturnValueOnce(0).mockReturnValueOnce(0.999).mockReturnValueOnce(0.999);
    const element = appendFormula();
    const answer = element.querySelector(".tb-formula__input");
    answer.value = "360";
    click(element.querySelector(".tb-formula__new-values"));

    expect(element.querySelector('[data-variable="x"]').textContent).toBe("90");
    expect(element.querySelector('[data-variable="y"]').textContent).toBe("20");
    expect(answer.value).toBe("");
  });

  it("sends non-JavaScript formulas to the configured endpoint", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0);
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ stdout: "280" }),
    });
    globalThis.fetch = fetchMock;
    const element = appendFormula({
      language: "python3",
      source: "print(360)",
      parameters: { compileargs: [], linkargs: [], runargs: ["--check"], interpreterargs: [] },
    });
    const answer = element.querySelector(".tb-formula__input");
    answer.value = "280";
    click(element.querySelector(".tb-formula__check"));
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, request] = fetchMock.mock.calls[0];
    expect(url).toBe("https://example.test/jobe/index.php/restapi/runs");
    const payload = JSON.parse(request.body);
    expect(payload.run_spec.language_id).toBe("python3");
    expect(payload.run_spec.sourcecode).toBe("print(360)");
    expect(JSON.parse(payload.run_spec.input)).toEqual({ x: 80, y: 10 });
    expect(payload.run_spec.parameters).toEqual({ runargs: ["--check"] });
    expect(element.querySelector(".tb-formula__status").textContent).toBe("Correct.");
  });
});
