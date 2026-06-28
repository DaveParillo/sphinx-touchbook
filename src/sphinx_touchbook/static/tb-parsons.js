class TbParsons extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.list = this.querySelector(":scope .tb-parsons__list");
    this.checkButton = this.querySelector(":scope .tb-parsons__check");
    this.status = this.querySelector(":scope .tb-parsons__status");
    this.noIndent = this.dataset.noIndent === "true";

    this.shuffle();
    this.addEventListener("click", (event) => {
      const button = event.target.closest("button");
      if (!button) {
        return;
      }
      const item = button.closest(".tb-parsons__item");
      if (button.classList.contains("tb-parsons__move-up")) {
        this.move(item, -1);
      } else if (button.classList.contains("tb-parsons__move-down")) {
        this.move(item, 1);
      } else if (button.classList.contains("tb-parsons__outdent")) {
        this.changeIndent(item, -4);
      } else if (button.classList.contains("tb-parsons__indent-in")) {
        this.changeIndent(item, 4);
      } else if (button.classList.contains("tb-parsons__toggle")) {
        this.toggleUse(item);
      } else if (button.classList.contains("tb-parsons__check")) {
        this.check();
      }
    });
    this.items().forEach((item) => this.setCurrentIndent(item, 0));
    this.updateControls();
    this.setStatus("");
  }

  items() {
    return Array.from(this.querySelectorAll(":scope .tb-parsons__item"));
  }

  requiredItems() {
    return this.items()
      .filter((item) => item.dataset.distractor !== "true")
      .sort((left, right) => Number(left.dataset.order) - Number(right.dataset.order));
  }

  includedItems() {
    return this.items().filter((item) => this.isIncluded(item));
  }

  isIncluded(item) {
    return item?.querySelector(".tb-parsons__toggle")?.getAttribute("aria-pressed") === "true";
  }

  shuffle() {
    if (!this.list) {
      return;
    }
    const items = this.items();
    for (let index = items.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [items[index], items[swapIndex]] = [items[swapIndex], items[index]];
    }
    if (this.isCorrect(items) && items.length > 1) {
      [items[0], items[1]] = [items[1], items[0]];
    }
    items.forEach((item) => this.list.append(item));
  }

  move(item, direction) {
    if (!item || !this.list) {
      return;
    }
    if (direction < 0 && item.previousElementSibling) {
      this.list.insertBefore(item, item.previousElementSibling);
      item.querySelector(".tb-parsons__move-up")?.focus();
    } else if (direction > 0 && item.nextElementSibling) {
      this.list.insertBefore(item.nextElementSibling, item);
      item.querySelector(".tb-parsons__move-down")?.focus();
    }
    this.clearFeedback();
    this.updateControls();
    this.setStatus("");
  }

  changeIndent(item, delta) {
    if (!item) {
      return;
    }
    const current = Number(item.dataset.currentIndent || 0);
    this.setCurrentIndent(item, Math.max(0, current + delta));
    this.clearFeedback();
    this.updateControls();
    this.setStatus("");
  }

  setCurrentIndent(item, indent) {
    item.dataset.currentIndent = String(indent);
    item.style.setProperty("--tb-parsons-indent", String(indent));
  }

  toggleUse(item) {
    if (!item) {
      return;
    }
    const toggle = item.querySelector(".tb-parsons__toggle");
    const icon = item.querySelector(".tb-parsons__toggle-icon");
    const label = item.querySelector(".tb-parsons__toggle-label");
    const included = !this.isIncluded(item);
    toggle.setAttribute("aria-pressed", included ? "true" : "false");
    toggle.setAttribute("aria-label", included ? "Included in solution" : "Not included in solution");
    if (icon) {
      icon.textContent = included ? "✓" : "×";
    }
    if (label) {
      label.textContent = included ? "Use" : "Skip";
    }
    item.classList.toggle("tb-parsons__item--excluded", !included);
    this.clearFeedback();
    this.setStatus("");
  }

  check() {
    const correct = this.isCorrect();
    this.markFeedback(correct);
    this.setStatus(correct ? "Correct." : this.incorrectMessage());
  }

  isCorrect(items = this.items()) {
    const required = this.requiredItems();
    const included = items.filter((item) => this.isIncluded(item));
    const hasOnlyRequired = included.length === required.length
      && included.every((item) => item.dataset.distractor !== "true");
    const orderCorrect = included.every(
      (item, index) => Number(item.dataset.order) === Number(required[index]?.dataset.order)
    );
    const indentCorrect = this.noIndent || included.every(
      (item) => Number(item.dataset.currentIndent || 0) === Number(item.dataset.indent || 0)
    );
    return hasOnlyRequired && orderCorrect && indentCorrect;
  }

  markFeedback(correct) {
    const requiredOrder = this.requiredItems().map((item) => Number(item.dataset.order));
    this.items().forEach((item) => {
      const included = this.isIncluded(item);
      const distractor = item.dataset.distractor === "true";
      const includedIndex = this.includedItems().indexOf(item);
      const orderCorrect = Number(item.dataset.order) === requiredOrder[includedIndex];
      const indentCorrect = this.noIndent
        || Number(item.dataset.currentIndent || 0) === Number(item.dataset.indent || 0);
      const itemCorrect = correct
        || (!distractor && included && orderCorrect && indentCorrect)
        || (distractor && !included);
      item.classList.toggle("tb-parsons__item--correct", itemCorrect);
      item.classList.toggle("tb-parsons__item--incorrect", !itemCorrect);
    });
  }

  incorrectMessage() {
    if (this.noIndent) {
      return "Not quite. Check the order and skipped fragments.";
    }
    return "Not quite. Check the order, indentation, and skipped fragments.";
  }

  clearFeedback() {
    this.items().forEach((item) => {
      item.classList.remove("tb-parsons__item--correct", "tb-parsons__item--incorrect");
    });
  }

  updateControls() {
    const items = this.items();
    items.forEach((item, index) => {
      const up = item.querySelector(".tb-parsons__move-up");
      const down = item.querySelector(".tb-parsons__move-down");
      const outdent = item.querySelector(".tb-parsons__outdent");
      if (up) {
        up.disabled = index === 0;
      }
      if (down) {
        down.disabled = index === items.length - 1;
      }
      if (outdent) {
        outdent.disabled = Number(item.dataset.currentIndent || 0) === 0;
      }
    });
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-parsons")) {
  customElements.define("tb-parsons", TbParsons);
}
