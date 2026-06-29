class TbFormula extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.config = this.readConfig();
    this.input = this.querySelector(":scope .tb-formula__input");
    this.checkButton = this.querySelector(":scope .tb-formula__check");
    this.newValuesButton = this.querySelector(":scope .tb-formula__new-values");
    this.status = this.querySelector(":scope .tb-formula__status");
    this.endpoint = this.dataset.endpoint || "";
    this.values = {};
    this.expected = null;

    this.generateValues();
    this.checkButton?.addEventListener("click", () => this.check());
    this.newValuesButton?.addEventListener("click", () => this.newValues());
    this.input?.addEventListener("input", () => {
      this.input.classList.remove("tb-formula__input--correct", "tb-formula__input--incorrect");
      this.setStatus("");
    });
  }

  readConfig() {
    const script = this.querySelector(':scope script[type="application/json"].tb-formula__config');
    if (!script) {
      return { variables: {}, formula: { language: "javascript", source: "" }, tolerance: 0 };
    }
    try {
      return JSON.parse(script.textContent || "{}");
    } catch {
      return { variables: {}, formula: { language: "javascript", source: "" }, tolerance: 0 };
    }
  }

  generateValues() {
    this.values = {};
    Object.entries(this.config.variables || {}).forEach(([name, range]) => {
      this.values[name] = this.randomValue(range);
    });
    this.querySelectorAll(":scope .tb-formula__variable").forEach((element) => {
      const name = element.dataset.variable;
      element.textContent = this.formatValue(this.values[name]);
    });
    this.expected = null;
    this.setStatus("");
  }

  randomValue(range) {
    const min = Number(range.min);
    const max = Number(range.max);
    if (range.integer) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    return Math.random() * (max - min) + min;
  }

  formatValue(value) {
    if (Number.isInteger(value)) {
      return String(value);
    }
    return String(Number(value.toFixed(4)));
  }

  newValues() {
    this.generateValues();
    if (this.input) {
      this.input.value = "";
      this.input.classList.remove("tb-formula__input--correct", "tb-formula__input--incorrect");
      this.input.focus();
    }
  }

  async check() {
    const submitted = Number(this.input?.value);
    if (!Number.isFinite(submitted)) {
      this.mark(false);
      this.setStatus("Enter a numeric answer.");
      return;
    }

    this.setStatus("Checking...");
    try {
      const expected = await this.expectedValue();
      const correct = this.inRange(submitted, expected);
      this.mark(correct);
      this.setStatus(correct ? "Correct." : "Not quite. Try again!");
    } catch (error) {
      this.mark(false);
      this.setStatus(error.message || "Unable to check this answer.");
    }
  }

  async expectedValue() {
    if (this.expected !== null) {
      return this.expected;
    }
    const formula = this.config.formula || {};
    const language = String(formula.language || "javascript").toLocaleLowerCase();
    if (language === "javascript" || language === "js") {
      this.expected = this.evaluateJavaScript(formula.source || "");
      return this.expected;
    }
    this.expected = await this.evaluateRemote(formula);
    return this.expected;
  }

  evaluateJavaScript(source) {
    const names = Object.keys(this.values);
    const args = names.map((name) => this.values[name]);
    const evaluator = new Function(...names, `"use strict"; return (${source});`);
    return this.normalizeExpected(evaluator(...args));
  }

  async evaluateRemote(formula) {
    if (!this.endpoint) {
      throw new Error("No formula execution endpoint is configured.");
    }
    const response = await fetch(this.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        run_spec: {
          language_id: formula.language,
          sourcecode: formula.source,
          input: JSON.stringify(this.values),
          parameters: this.cleanParameters(formula.parameters || {}),
        },
      }),
    });
    if (!response.ok) {
      throw new Error("Unable to check this answer.");
    }
    const result = await response.json();
    if (result.stderr || result.cmpinfo) {
      throw new Error(result.stderr || result.cmpinfo);
    }
    return this.normalizeExpected(this.parseExpected(result.stdout));
  }

  cleanParameters(parameters) {
    const cleaned = {};
    Object.entries(parameters).forEach(([key, value]) => {
      if (Array.isArray(value) && value.length > 0) {
        cleaned[key] = value.map((item) => String(item));
      }
    });
    return cleaned;
  }

  parseExpected(text) {
    const trimmed = String(text || "").trim();
    try {
      return JSON.parse(trimmed);
    } catch {
      return Number(trimmed);
    }
  }

  normalizeExpected(value) {
    if (Array.isArray(value) && value.length === 2) {
      return { min: Number(value[0]), max: Number(value[1]) };
    }
    if (value && typeof value === "object" && "min" in value && "max" in value) {
      return { min: Number(value.min), max: Number(value.max) };
    }
    const numberValue = Number(value);
    if (!Number.isFinite(numberValue)) {
      throw new Error("The answer formula did not produce a numeric value.");
    }
    return numberValue;
  }

  inRange(submitted, expected) {
    if (typeof expected === "number") {
      const tolerance = Number(this.config.tolerance || 0);
      return Math.abs(submitted - expected) <= tolerance;
    }
    return submitted >= expected.min && submitted <= expected.max;
  }

  mark(correct) {
    if (!this.input) {
      return;
    }
    this.input.classList.toggle("tb-formula__input--correct", correct);
    this.input.classList.toggle("tb-formula__input--incorrect", !correct);
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-formula")) {
  customElements.define("tb-formula", TbFormula);
}
