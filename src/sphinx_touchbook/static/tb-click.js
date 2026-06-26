class TbClick extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.targets = Array.from(this.querySelectorAll(":scope .tb-click__target"));
    this.feedback = Array.from(this.querySelectorAll(":scope .tb-click__feedback"));
    this.hintToggle = this.querySelector(":scope .tb-click__hint-toggle");
    this.status = this.querySelector(":scope .tb-click__status");

    this.feedback.forEach((item) => {
      item.hidden = true;
    });
    this.targets.forEach((target) => {
      target.addEventListener("click", () => this.selectTarget(target));
    });
    this.hintsVisible = this.getAttribute("hints") === "true";
    if (this.getAttribute("hints") === "never" && this.hintToggle) {
      this.hintToggle.hidden = true;
    } else if (this.hintToggle) {
      this.hintToggle.addEventListener("click", () => this.toggleHints());
    }
    this.updateHints();
    this.setStatus("");
  }

  toggleHints() {
    this.hintsVisible = !this.hintsVisible;
    this.updateHints();
  }

  updateHints() {
    this.dataset.hintsVisible = this.hintsVisible ? "true" : "false";
    if (this.hintToggle) {
      this.hintToggle.textContent = this.hintsVisible ? "Hide Hints" : "Show Hints";
      this.hintToggle.setAttribute("aria-pressed", this.hintsVisible ? "true" : "false");
    }
  }

  selectTarget(target) {
    this.targets.forEach((item) => {
      item.classList.remove("tb-click__target--correct", "tb-click__target--incorrect");
      item.setAttribute("aria-pressed", "false");
    });
    this.feedback.forEach((item) => {
      item.hidden = true;
    });

    const correct = target.dataset.correct === "true";
    target.classList.add(correct ? "tb-click__target--correct" : "tb-click__target--incorrect");
    target.setAttribute("aria-pressed", "true");

    const feedback = document.getElementById(target.dataset.feedbackId);
    if (feedback) {
      feedback.hidden = false;
    }
    this.setStatus(correct ? "Correct." : "Not quite.");
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-click")) {
  customElements.define("tb-click", TbClick);
}
