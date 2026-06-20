class TbReveal extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.modal = this.hasAttribute("modal");
    this.showLabel = this.getAttribute("showlabel") || "Show";
    this.hideLabel = this.getAttribute("hidelabel") || "Hide";
    this.modalTitlebar = this.getAttribute("modal-titlebar") || "Message from the author";
    this.fallback = this.querySelector(".tb-reveal__fallback");
    if (!this.fallback) {
      return;
    }
    this.content = this.querySelector(".tb-reveal__content");
    if (!this.content) {
      return;
    }
    this.modal ? this.enhanceModal() : this.enhanceInline();
  }

  enhanceInline() {
    this.fallback.hidden = true;

    const button = document.createElement("button");
    const panelId = this.contentId();
    button.type = "button";
    button.className = "tb-reveal__button";
    button.textContent = this.showLabel;
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", panelId);

    const panel = document.createElement("div");
    panel.className = "tb-reveal__panel";
    panel.id = panelId;
    panel.hidden = true;
    while (this.content.firstChild) {
      panel.appendChild(this.content.firstChild);
    }

    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      button.textContent = expanded ? this.showLabel : this.hideLabel;
      panel.hidden = expanded;
    });

    this.append(button, panel);
  }

  enhanceModal() {
    this.fallback.hidden = true;

    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.className = "tb-reveal__button";
    openButton.textContent = this.showLabel;
    openButton.setAttribute("aria-haspopup", "dialog");

    const dialog = document.createElement("dialog");
    dialog.className = "tb-reveal__dialog";
    dialog.setAttribute("aria-labelledby", this.labelId());

    const header = document.createElement("div");
    header.className = "tb-reveal__dialog-header";

    const label = document.createElement("div");
    label.className = "tb-reveal__dialog-label";
    label.id = dialog.getAttribute("aria-labelledby");
    label.textContent = this.modalTitlebar;

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "tb-reveal__button";
    closeButton.textContent = this.hideLabel;

    const body = document.createElement("div");
    body.className = "tb-reveal__panel";
    while (this.content.firstChild) {
      body.appendChild(this.content.firstChild);
    }

    closeButton.addEventListener("click", () => {
      if (typeof dialog.close === "function") {
        dialog.close();
      } else {
        dialog.removeAttribute("open");
      }
    });
    openButton.addEventListener("click", () => {
      if (typeof dialog.showModal === "function") {
        dialog.showModal();
      } else {
        dialog.setAttribute("open", "");
      }
    });

    header.append(label, closeButton);
    dialog.append(header, body);
    this.append(openButton, dialog);
  }

  labelId() {
    if (!this.id) {
      this.id = `tb-reveal-${TbReveal.nextId++}`;
    }
    return `${this.id}-label`;
  }

  contentId() {
    if (!this.id) {
      this.id = `tb-reveal-${TbReveal.nextId++}`;
    }
    return `${this.id}-content`;
  }
}

TbReveal.nextId = 1;

customElements.define("tb-reveal", TbReveal);
