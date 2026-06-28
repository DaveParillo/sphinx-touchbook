class TbOrder extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.list = this.querySelector(":scope .tb-order__list");
    this.checkButton = this.querySelector(":scope .tb-order__check");
    this.status = this.querySelector(":scope .tb-order__status");

    this.shuffle();
    this.addEventListener("click", (event) => {
      const button = event.target.closest("button");
      if (!button) {
        return;
      }
      if (button.classList.contains("tb-order__move-up")) {
        this.move(button.closest(".tb-order__item"), -1);
      } else if (button.classList.contains("tb-order__move-down")) {
        this.move(button.closest(".tb-order__item"), 1);
      } else if (button.classList.contains("tb-order__check")) {
        this.check();
      }
    });
    this.updateControls();
    this.setStatus("");
  }

  items() {
    return Array.from(this.querySelectorAll(":scope .tb-order__item"));
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
    if (this.isCorrectOrder(items) && items.length > 1) {
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
      item.querySelector(".tb-order__move-up")?.focus();
    } else if (direction > 0 && item.nextElementSibling) {
      this.list.insertBefore(item.nextElementSibling, item);
      item.querySelector(".tb-order__move-down")?.focus();
    }
    this.clearFeedback();
    this.updateControls();
    this.setStatus("");
  }

  check() {
    const items = this.items();
    const correct = this.isCorrectOrder(items);
    items.forEach((item, index) => {
      const itemCorrect = Number(item.dataset.order) === index;
      item.classList.toggle("tb-order__item--correct", correct || itemCorrect);
      item.classList.toggle("tb-order__item--incorrect", !correct && !itemCorrect);
    });
    this.setStatus(correct ? "Correct." : "Not quite. Try again!");
  }

  isCorrectOrder(items) {
    return items.every((item, index) => Number(item.dataset.order) === index);
  }

  clearFeedback() {
    this.items().forEach((item) => {
      item.classList.remove("tb-order__item--correct", "tb-order__item--incorrect");
    });
  }

  updateControls() {
    const items = this.items();
    items.forEach((item, index) => {
      const up = item.querySelector(".tb-order__move-up");
      const down = item.querySelector(".tb-order__move-down");
      if (up) {
        up.disabled = index === 0;
      }
      if (down) {
        down.disabled = index === items.length - 1;
      }
    });
  }

  setStatus(text) {
    if (this.status) {
      this.status.textContent = text;
    }
  }
}

if (!customElements.get("tb-order")) {
  customElements.define("tb-order", TbOrder);
}
