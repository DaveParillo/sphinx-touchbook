class TbMatch extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.selects = Array.from(this.querySelectorAll(":scope .tb-match__select"));
    this.checkButton = this.querySelector(":scope .tb-match__check");
    this.status = this.querySelector(":scope .tb-match__status");

    this.selects.forEach((select) => {
      select.addEventListener("change", () => {
        this.clearFeedback();
        this.updateState();
        this.setStatus("");
      });
    });
    if (this.checkButton) {
      this.checkButton.addEventListener("click", () => this.check());
    }
    this.updateState();
    this.setStatus("");
  }

  updateState() {
    if (this.checkButton) {
      this.checkButton.disabled = this.selects.length === 0;
    }
  }

  check() {
    let correctCount = 0;
    let incorrectCount = 0;
    let blankCount = 0;
    this.selects.forEach((select) => {
      const blank = select.value === "";
      const correct = !blank && select.value === select.dataset.answer;
      const incorrect = !blank && !correct;
      const choice = select.closest(".tb-match__choice");
      if (correct) {
        correctCount += 1;
      }
      if (incorrect) {
        incorrectCount += 1;
      }
      if (blank) {
        blankCount += 1;
      }
      select.classList.toggle("tb-match__select--correct", correct);
      select.classList.toggle("tb-match__select--incorrect", incorrect);
      if (choice) {
        choice.classList.toggle("tb-match__choice--correct", correct);
        choice.classList.toggle("tb-match__choice--incorrect", incorrect);
      }
    });
    if (correctCount === this.selects.length) {
      this.setStatus("Correct.");
      return;
    }
    this.setStatus(
      `Not quite: You got ${correctCount} correct and ${incorrectCount} incorrect out of ${this.selects.length}. ` +
        `You left ${blankCount} blank. Try again!`
    );
  }

  clearFeedback() {
    this.selects.forEach((select) => {
      const choice = select.closest(".tb-match__choice");
      select.classList.remove("tb-match__select--correct", "tb-match__select--incorrect");
      if (choice) {
        choice.classList.remove("tb-match__choice--correct", "tb-match__choice--incorrect");
      }
    });
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-match")) {
  customElements.define("tb-match", TbMatch);
}
