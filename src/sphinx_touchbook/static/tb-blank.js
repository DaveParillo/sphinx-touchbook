class TbBlank extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.inputs = Array.from(this.querySelectorAll(":scope .tb-blank__input"));
    this.checkButton = this.querySelector(":scope .tb-blank__check");
    this.status = this.querySelector(":scope .tb-blank__status");
    this.config = this.readConfig();
    this.caseSensitive = this.getAttribute("case-sensitive") === "true";
    this.trim = this.getAttribute("trim") !== "false";

    this.inputs.forEach((input) => {
      input.addEventListener("input", () => {
        input.classList.remove("tb-blank__input--correct", "tb-blank__input--incorrect");
        this.setStatus("");
      });
    });
    if (this.checkButton) {
      this.checkButton.addEventListener("click", () => this.check());
    }
  }

  readConfig() {
    const script = this.querySelector(':scope script[type="application/json"].tb-blank__config');
    if (!script) {
      return { answers: {} };
    }
    try {
      return JSON.parse(script.textContent || "{}");
    } catch {
      return { answers: {} };
    }
  }

  check() {
    let correctCount = 0;
    const messages = [];
    this.inputs.forEach((input) => {
      const blankId = input.dataset.blankId;
      const answer = this.config.answers?.[blankId] || {};
      const result = this.evaluate(input.value, answer);
      if (result.correct) {
        correctCount += 1;
      }
      input.classList.toggle("tb-blank__input--correct", result.correct);
      input.classList.toggle("tb-blank__input--incorrect", !result.correct);
      if (result.message) {
        messages.push(result.message);
      }
    });

    if (correctCount === this.inputs.length) {
      this.setStatus(messages[0] || "Correct.");
      return;
    }
    this.setStatus(messages.join(" ") || `Not quite: You got ${correctCount} correct out of ${this.inputs.length}.`);
  }

  evaluate(rawValue, answer) {
    const value = this.normalize(rawValue);
    const matches = answer.matches || [];
    const hints = answer.hints || [];
    const useRegex = Boolean(answer.regex);

    if (matches.some((expected) => this.matches(value, expected, useRegex))) {
      return { correct: true, message: answer.feedback || "Correct." };
    }

    const hint = hints.find((item) => this.matches(value, item.value, false));
    if (hint) {
      return { correct: false, message: hint.feedback };
    }

    return { correct: false, message: answer.incorrect || "Not quite. Try again!" };
  }

  matches(value, expected, useRegex) {
    if (!useRegex) {
      const normalizedExpected = this.normalize(expected);
      return value === normalizedExpected;
    }
    try {
      const flags = this.caseSensitive ? "" : "i";
      const pattern = this.trim ? String(expected).trim() : String(expected);
      return new RegExp(pattern, flags).test(value);
    } catch {
      return false;
    }
  }

  normalize(value) {
    const stringValue = this.trim ? String(value).trim() : String(value);
    return this.caseSensitive ? stringValue : stringValue.toLocaleLowerCase();
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-blank")) {
  customElements.define("tb-blank", TbBlank);
}
