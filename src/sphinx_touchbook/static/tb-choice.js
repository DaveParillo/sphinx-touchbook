class TbChoice extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.optionContainer = this.querySelector(":scope .tb-choice__options");
    if (this.shouldRandomize()) {
      this.randomizeOptions();
    }
    this.options = Array.from(this.querySelectorAll(":scope .tb-choice__option"));
    this.inputs = this.options
      .map((option) => option.querySelector(".tb-choice__input"))
      .filter(Boolean);
    this.feedback = Array.from(this.querySelectorAll(":scope .tb-choice__feedback"));
    this.checkButton = this.querySelector(":scope .tb-choice__check");
    this.status = this.querySelector(":scope .tb-choice__status");

    this.feedback.forEach((item) => {
      item.hidden = true;
    });
    if (this.status) {
      this.status.textContent = "";
    }
    if (this.checkButton) {
      this.checkButton.addEventListener("click", () => this.check());
    }
    this.inputs.forEach((input) => {
      input.addEventListener("change", () => this.clearResult());
    });
  }

  shouldRandomize() {
    return this.getAttribute("random") === "true";
  }

  randomizeOptions() {
    if (!this.optionContainer) {
      return;
    }
    const options = Array.from(this.optionContainer.querySelectorAll(":scope > .tb-choice__option"));
    for (let index = options.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [options[index], options[swapIndex]] = [options[swapIndex], options[index]];
    }
    options.forEach((option) => this.optionContainer.append(option));
  }

  check() {
    const selected = this.options.filter((option) => {
      const input = option.querySelector(".tb-choice__input");
      return input && input.checked;
    });
    this.feedback.forEach((item) => {
      item.hidden = true;
    });
    this.options.forEach((option) => {
      option.classList.remove("tb-choice__option--selected", "tb-choice__option--correct", "tb-choice__option--incorrect");
    });

    if (selected.length === 0) {
      this.setStatus("Choose an answer before checking.");
      return;
    }

    selected.forEach((option) => {
      const feedback = option.querySelector(".tb-choice__feedback");
      option.classList.add("tb-choice__option--selected");
      option.classList.add(this.isCorrectOption(option) ? "tb-choice__option--correct" : "tb-choice__option--incorrect");
      if (feedback) {
        feedback.hidden = false;
      }
    });

    this.setStatus(this.isCorrectSelection() ? "Correct." : "Not quite.");
  }

  clearResult() {
    this.setStatus("");
    this.options.forEach((option) => {
      option.classList.remove("tb-choice__option--selected", "tb-choice__option--correct", "tb-choice__option--incorrect");
    });
    this.feedback.forEach((item) => {
      item.hidden = true;
    });
  }

  isCorrectSelection() {
    return this.options.every((option) => {
      const input = option.querySelector(".tb-choice__input");
      if (!input) {
        return true;
      }
      return input.checked === this.isCorrectOption(option);
    });
  }

  isCorrectOption(option) {
    return option.dataset.correct === "true";
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-choice")) {
  customElements.define("tb-choice", TbChoice);
}
