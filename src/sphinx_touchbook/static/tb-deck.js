class TbDeck extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      this.attachNavigation();
      this.revealHashTarget();
      return;
    }
    const script = this.querySelector(':scope > script[type="application/json"]');
    const controls = this.querySelector(":scope > .tb-deck__controls");
    const cards = Array.from(this.querySelectorAll(":scope > .tb-deck__cards > tb-card"));
    let config;
    try {
      config = JSON.parse(script?.textContent || "");
    } catch {
      return;
    }
    if (!config || config.version !== 1 || !Array.isArray(config.cards) || !cards.length ||
        config.cards.length !== cards.length || !controls ||
        !config.cards.every((card, index) => card.id === cards[index].id)) return;
    const buttons = Array.from(controls.querySelectorAll("button[data-action]"));
    const actions = ["first", "previous", "next", "last"];
    this.status = controls.querySelector(".tb-deck__status");
    this.caption = controls.querySelector(".tb-deck__card-caption");
    this.selector = controls.querySelector("select.tb-deck__selector");
    if (!this.status || !this.caption?.id || !this.selector ||
        actions.some((action) => !buttons.some((button) => button.dataset.action === action))) return;

    this.cards = cards;
    this.config = config;
    this.buttons = buttons;
    this.index = 0;
    this.selector.replaceChildren(...config.cards.map((card, index) => {
      const option = document.createElement("option");
      const caption = card.caption.replace(/\s+/g, " ").trim();
      const characters = Array.from(caption);
      const shortCaption = characters.length > 24
        ? `${characters.slice(0, 23).join("")}…` : caption;
      const position = `${index + 1} of ${cards.length}`;
      option.value = String(index);
      option.textContent = position + (shortCaption ? `: ${shortCaption}` : "");
      option.setAttribute("aria-label", position + (caption ? `: ${caption}` : ""));
      option.title = option.getAttribute("aria-label");
      return option;
    }));
    this.selector.hidden = cards.length === 1;
    this.selector.addEventListener("change", () => {
      if (this.selector.selectedIndex >= 0) {
        // The native select announces the chosen option itself.
        this.showCard(this.selector.selectedIndex, { announce: false });
      }
    });
    this.setAttribute("aria-roledescription", "carousel");
    cards.forEach((card) => {
      card.setAttribute("aria-roledescription", "slide");
      const heading = card.querySelector(":scope > .tb-card__caption");
      if (heading) heading.hidden = true;
    });
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const destination = { first: 0, previous: this.index - 1,
          next: this.index + 1, last: cards.length - 1 }[button.dataset.action];
        this.showCard(destination);
      });
    });
    this.onHashChange = () => this.revealHashTarget();
    this.onDocumentClick = (event) => {
      const link = event.target.closest?.("a[href]");
      if (!link || event.defaultPrevented || event.button > 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const url = new URL(link.href, window.location.href);
      if (url.origin === window.location.origin && url.pathname === window.location.pathname &&
          url.search === window.location.search && url.hash) this.revealHashTarget(url.hash);
    };
    this.attachNavigation();
    this.dataset.enhanced = "true";
    this.showCard(0);
    this.revealHashTarget(window.location.hash, false);
    controls.hidden = false;
  }

  disconnectedCallback() {
    window.removeEventListener("hashchange", this.onHashChange);
    document.removeEventListener("click", this.onDocumentClick);
  }

  attachNavigation() {
    window.addEventListener("hashchange", this.onHashChange);
    document.addEventListener("click", this.onDocumentClick);
  }

  showCard(index, { announce = true } = {}) {
    if (!Number.isInteger(index)) return;
    this.index = Math.max(0, Math.min(index, this.cards.length - 1));
    this.selector.value = String(this.index);
    this.selector.title = this.selector.selectedOptions[0].title;
    this.cards.forEach((card, number) => { card.hidden = number !== this.index; });
    this.buttons.forEach((button) => {
      button.disabled = ["first", "previous"].includes(button.dataset.action)
        ? this.index === 0 : this.index === this.cards.length - 1;
    });
    if (this.buttons.includes(document.activeElement) && document.activeElement.disabled) {
      const action = this.index === 0 ? "next" : "previous";
      this.buttons.find((button) => button.dataset.action === action && !button.disabled)?.focus();
    }
    const caption = this.config.cards[this.index].caption;
    this.caption.textContent = caption;
    this.caption.hidden = !caption;
    this.cards.forEach((card, number) => {
      const cardCaption = this.config.cards[number].caption;
      if (number === this.index && cardCaption) {
        card.setAttribute("aria-labelledby", this.caption.id);
        card.removeAttribute("aria-label");
      } else {
        // Inactive cards keep their own names instead of following the
        // shared visible caption as navigation changes it.
        card.removeAttribute("aria-labelledby");
        card.setAttribute("aria-label", cardCaption || `${number + 1} of ${this.cards.length}`);
      }
    });
    this.status.textContent = announce ? `Card ${this.index + 1} of ${this.cards.length}` : "";
    if (caption && announce) {
      // Include the full caption in announcements without changing the
      // compact selector or single-card count.
      const description = document.createElement("span");
      description.className = "tb-deck__status-caption";
      description.textContent = `: ${caption}`;
      this.status.append(description);
    }
    this.dataset.card = String(this.index + 1);
  }

  revealHashTarget(hash = window.location.hash, scroll = true) {
    let id;
    try { id = decodeURIComponent(hash.replace(/^#/, "")); } catch { return; }
    if (!id) return;
    const target = document.getElementById(id);
    const card = target?.closest("tb-card");
    const index = this.cards.indexOf(card);
    if (index < 0) return;
    this.showCard(index);
    if (scroll) target.scrollIntoView?.({ block: "nearest" });
  }
}

if (!customElements.get("tb-deck")) customElements.define("tb-deck", TbDeck);
