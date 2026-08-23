class TbReveal extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.revealTitle = this.getAttribute("label") || "Details";
    this.fallback = this.querySelector(".tb-reveal__fallback");
    if (!this.fallback) {
      return;
    }
    this.content = this.querySelector(".tb-reveal__content");
    if (!this.content) {
      return;
    }
    this.enhanceInline();
  }

  enhanceInline() {
    this.fallback.hidden = true;

    const button = document.createElement("button");
    const panelId = this.contentId();
    button.type = "button";
    button.className = "tb-reveal__button";
    button.append(this.chevron(), document.createTextNode(this.revealTitle));
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
      panel.hidden = expanded;
    });

    this.append(button, panel);
  }

  contentId() {
    if (!this.id) {
      this.id = `tb-reveal-${TbReveal.nextId++}`;
    }
    return `${this.id}-content`;
  }

  chevron() {
    const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    icon.classList.add("tb-reveal__chevron");
    icon.setAttribute("aria-hidden", "true");
    icon.setAttribute("focusable", "false");
    icon.setAttribute("viewBox", "0 0 24 24");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "m9 18 6-6-6-6");
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "currentcolor");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("stroke-linejoin", "round");
    path.setAttribute("stroke-width", "2");
    icon.appendChild(path);
    return icon;
  }
}

TbReveal.nextId = 1;

customElements.define("tb-reveal", TbReveal);
