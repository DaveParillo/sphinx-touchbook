class TbMicroParsons extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.source = this.querySelector(":scope .tb-micro-parsons__source");
    this.target = this.querySelector(":scope .tb-micro-parsons__target");
    this.checkButton = this.querySelector(":scope .tb-micro-parsons__check");
    this.status = this.querySelector(":scope .tb-micro-parsons__status");

    this.shuffle();
    this.addEventListener("click", (event) => {
      const button = event.target.closest(".tb-micro-parsons__token-button");
      if (button) {
        this.toggleToken(button.closest(".tb-micro-parsons__token"));
        return;
      }
      if (event.target.closest(".tb-micro-parsons__check")) {
        this.check();
      }
    });
    this.updateButtons();
    this.setStatus("");
  }

  tokens() {
    return Array.from(this.querySelectorAll(":scope .tb-micro-parsons__token"));
  }

  sourceTokens() {
    return Array.from(this.source?.querySelectorAll(":scope .tb-micro-parsons__token") || []);
  }

  targetTokens() {
    return Array.from(this.target?.querySelectorAll(":scope .tb-micro-parsons__token") || []);
  }

  requiredTokens() {
    return this.tokens()
      .filter((token) => token.dataset.distractor !== "true")
      .sort((left, right) => Number(left.dataset.order) - Number(right.dataset.order));
  }

  shuffle() {
    if (!this.source) {
      return;
    }
    const tokens = this.tokens();
    for (let index = tokens.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [tokens[index], tokens[swapIndex]] = [tokens[swapIndex], tokens[index]];
    }
    if (this.isSourceInitiallyCorrect(tokens) && tokens.length > 1) {
      [tokens[0], tokens[1]] = [tokens[1], tokens[0]];
    }
    tokens.forEach((token) => this.source.append(token));
  }

  isSourceInitiallyCorrect(tokens) {
    const required = tokens.filter((token) => token.dataset.distractor !== "true");
    return required.every((token, index) => Number(token.dataset.order) === index);
  }

  toggleToken(token) {
    if (!token || !this.source || !this.target) {
      return;
    }
    const destination = token.dataset.location === "target" ? this.source : this.target;
    token.dataset.location = destination === this.target ? "target" : "source";
    destination.append(token);
    this.clearFeedback();
    this.updateButtons();
    this.setStatus("");
    token.querySelector(".tb-micro-parsons__token-button")?.focus();
  }

  check() {
    const correct = this.isCorrect();
    this.markFeedback(correct);
    this.setStatus(correct ? "Correct." : "Not quite. Move the needed tokens into the answer row in order.");
  }

  isCorrect() {
    const answer = this.targetTokens();
    const required = this.requiredTokens();
    if (answer.length !== required.length) {
      return false;
    }
    if (answer.some((token) => token.dataset.distractor === "true")) {
      return false;
    }
    return answer.every((token, index) => Number(token.dataset.order) === Number(required[index]?.dataset.order));
  }

  markFeedback(correct) {
    const requiredOrder = this.requiredTokens().map((token) => Number(token.dataset.order));
    const answer = this.targetTokens();
    this.tokens().forEach((token) => {
      const inTarget = token.dataset.location === "target";
      const distractor = token.dataset.distractor === "true";
      const answerIndex = answer.indexOf(token);
      const tokenCorrect = correct
        || (!distractor && inTarget && Number(token.dataset.order) === requiredOrder[answerIndex])
        || (distractor && !inTarget);
      token.classList.toggle("tb-micro-parsons__token--correct", tokenCorrect);
      token.classList.toggle("tb-micro-parsons__token--incorrect", !tokenCorrect);
    });
  }

  clearFeedback() {
    this.tokens().forEach((token) => {
      token.classList.remove("tb-micro-parsons__token--correct", "tb-micro-parsons__token--incorrect");
    });
  }

  updateButtons() {
    this.tokens().forEach((token) => {
      const button = token.querySelector(".tb-micro-parsons__token-button");
      if (!button) {
        return;
      }
      const label = token.textContent.trim();
      const inTarget = token.dataset.location === "target";
      button.setAttribute("aria-label", inTarget ? `Move ${label} to tokens` : `Move ${label} to answer`);
      button.setAttribute("aria-pressed", inTarget ? "true" : "false");
    });
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-micro-parsons")) {
  customElements.define("tb-micro-parsons", TbMicroParsons);
}
