const MATH_CONSTANTS = Object.freeze({
  E: Math.E,
  PI: Math.PI,
});

const MATH_FUNCTIONS = Object.freeze({
  abs: Math.abs,
  acos: Math.acos,
  acosh: Math.acosh,
  asin: Math.asin,
  asinh: Math.asinh,
  atan: Math.atan,
  atan2: Math.atan2,
  atanh: Math.atanh,
  cbrt: Math.cbrt,
  ceil: Math.ceil,
  cos: Math.cos,
  cosh: Math.cosh,
  exp: Math.exp,
  expm1: Math.expm1,
  floor: Math.floor,
  hypot: Math.hypot,
  log: Math.log,
  log10: Math.log10,
  log1p: Math.log1p,
  log2: Math.log2,
  max: Math.max,
  min: Math.min,
  pow: Math.pow,
  round: Math.round,
  sign: Math.sign,
  sin: Math.sin,
  sinh: Math.sinh,
  sqrt: Math.sqrt,
  tan: Math.tan,
  tanh: Math.tanh,
  trunc: Math.trunc,
});

class FormulaExpressionParser {
  constructor(source, values) {
    this.source = String(source);
    this.values = values;
    this.position = 0;
    this.token = null;
    this.nextToken();
  }

  parse() {
    const value = this.parseExpression();
    if (this.token.type !== "end") {
      throw new Error(`Unexpected token ${this.token.value}.`);
    }
    return value;
  }

  nextToken() {
    while (/\s/.test(this.source[this.position] || "")) {
      this.position += 1;
    }
    if (this.position >= this.source.length) {
      this.token = { type: "end", value: "" };
      return;
    }

    const remainder = this.source.slice(this.position);
    const number = remainder.match(/^(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/);
    if (number) {
      this.position += number[0].length;
      this.token = { type: "number", value: number[0] };
      return;
    }
    const identifier = remainder.match(/^[A-Za-z_][A-Za-z0-9_]*/);
    if (identifier) {
      this.position += identifier[0].length;
      this.token = { type: "identifier", value: identifier[0] };
      return;
    }
    if (remainder.startsWith("**")) {
      this.position += 2;
      this.token = { type: "operator", value: "**" };
      return;
    }
    const symbol = remainder[0];
    if ("+-*/()[]{}.,:".includes(symbol)) {
      this.position += 1;
      this.token = { type: "symbol", value: symbol };
      return;
    }
    throw new Error(`Unsupported character ${symbol}.`);
  }

  accept(value) {
    if (this.token.value !== value) {
      return false;
    }
    this.nextToken();
    return true;
  }

  expect(value) {
    if (!this.accept(value)) {
      throw new Error(`Expected ${value}.`);
    }
  }

  parseExpression(minimumPrecedence = 0) {
    let value = this.parseUnary();
    const precedence = { "+": 1, "-": 1, "*": 2, "/": 2, "**": 3 };
    while (Object.hasOwn(precedence, this.token.value) && precedence[this.token.value] >= minimumPrecedence) {
      const operator = this.token.value;
      const operatorPrecedence = precedence[operator];
      this.nextToken();
      const nextPrecedence = operator === "**" ? operatorPrecedence : operatorPrecedence + 1;
      const right = this.parseExpression(nextPrecedence);
      if (operator === "+") value += right;
      if (operator === "-") value -= right;
      if (operator === "*") value *= right;
      if (operator === "/") value /= right;
      if (operator === "**") value **= right;
    }
    return value;
  }

  parseUnary() {
    if (this.accept("+")) return this.parseUnary();
    if (this.accept("-")) return -this.parseUnary();
    return this.parsePrimary();
  }

  parsePrimary() {
    if (this.token.type === "number") {
      const value = Number(this.token.value);
      this.nextToken();
      return value;
    }
    if (this.accept("(")) {
      const value = this.parseExpression();
      this.expect(")");
      return value;
    }
    if (this.accept("[")) return this.parseArray();
    if (this.accept("{")) return this.parseRange();
    if (this.token.type === "identifier") return this.parseIdentifier();
    throw new Error(`Expected a number, variable, or expression; found ${this.token.value || "end of formula"}.`);
  }

  parseArray() {
    const values = [];
    if (this.accept("]")) return values;
    do {
      values.push(this.parseExpression());
    } while (this.accept(","));
    this.expect("]");
    return values;
  }

  parseRange() {
    const result = {};
    if (this.accept("}")) return result;
    do {
      if (this.token.type !== "identifier" || !["min", "max"].includes(this.token.value)) {
        throw new Error("Range objects may contain only min and max keys.");
      }
      const key = this.token.value;
      this.nextToken();
      this.expect(":");
      result[key] = this.parseExpression();
    } while (this.accept(","));
    this.expect("}");
    return result;
  }

  parseIdentifier() {
    const name = this.token.value;
    this.nextToken();
    if (Object.hasOwn(this.values, name)) return this.values[name];
    if (name !== "Math") {
      throw new Error(`Unknown variable ${name}.`);
    }

    this.expect(".");
    if (this.token.type !== "identifier") {
      throw new Error("Expected a Math constant or function name.");
    }
    const member = this.token.value;
    this.nextToken();
    if (Object.hasOwn(MATH_CONSTANTS, member)) return MATH_CONSTANTS[member];
    if (!Object.hasOwn(MATH_FUNCTIONS, member)) {
      throw new Error(`Unsupported Math function Math.${member}.`);
    }
    this.expect("(");
    const args = this.parseArrayContents();
    return MATH_FUNCTIONS[member](...args);
  }

  parseArrayContents() {
    const values = [];
    if (this.accept(")")) return values;
    do {
      values.push(this.parseExpression());
    } while (this.accept(","));
    this.expect(")");
    return values;
  }
}

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
      this.values[name] = this.displayedValue(this.randomValue(range), range);
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

  displayedValue(value, range) {
    return range.integer ? value : Number(value.toFixed(4));
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
    const answer = this.input?.value.trim() || "";
    if (!answer) {
      this.mark(false);
      this.setStatus("Enter a numeric answer.");
      return;
    }
    const submitted = Number(answer);
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
      this.expected = this.evaluateFormulaExpression(formula.source || "");
      return this.expected;
    }
    this.expected = await this.evaluateRemote(formula);
    return this.expected;
  }

  evaluateFormulaExpression(source) {
    const value = new FormulaExpressionParser(source, this.values).parse();
    return this.normalizeExpected(value);
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
      return this.normalizeRange(value[0], value[1]);
    }
    if (value && typeof value === "object" && "min" in value && "max" in value) {
      return this.normalizeRange(value.min, value.max);
    }
    const numberValue = Number(value);
    if (!Number.isFinite(numberValue)) {
      throw new Error("The answer formula did not produce a numeric value.");
    }
    return numberValue;
  }

  normalizeRange(minimum, maximum) {
    const min = Number(minimum);
    const max = Number(maximum);
    if (!Number.isFinite(min) || !Number.isFinite(max) || min > max) {
      throw new Error("The answer formula did not produce a valid numeric range.");
    }
    return { min, max };
  }

  inRange(submitted, expected) {
    if (typeof expected === "number") {
      const configuredTolerance = Number(this.config.tolerance || 0);
      const floatingPointTolerance = Number.EPSILON * 8 * Math.max(1, Math.abs(submitted), Math.abs(expected));
      return Math.abs(submitted - expected) <= Math.max(configuredTolerance, floatingPointTolerance);
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
