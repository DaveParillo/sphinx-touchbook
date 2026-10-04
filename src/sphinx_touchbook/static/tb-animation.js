class TbAnimation extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      this.attachNavigation();
      this.revealHashTarget();
      return;
    }
    const script = this.querySelector(':scope > script[type="application/json"]');
    const controls = this.querySelector(":scope > .tb-animation__controls");
    const scenes = Array.from(this.querySelectorAll(":scope > .tb-animation__scenes > tb-scene"));
    let config;
    try {
      config = JSON.parse(script?.textContent || "");
    } catch {
      return;
    }
    if (!config || config.version !== 1 || !Array.isArray(config.scenes) || !scenes.length ||
        config.scenes.length !== scenes.length || !controls ||
        !config.scenes.every((scene, index) => scene.id === scenes[index].id)) return;
    const buttons = Array.from(controls.querySelectorAll("button[data-action]"));
    const actions = ["first", "previous", "next", "last"];
    this.status = controls.querySelector(".tb-animation__status");
    if (!this.status || actions.some((action) => !buttons.some((button) => button.dataset.action === action))) return;

    this.scenes = scenes;
    this.config = config;
    this.buttons = buttons;
    this.index = 0;
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const destination = { first: 0, previous: this.index - 1,
          next: this.index + 1, last: scenes.length - 1 }[button.dataset.action];
        this.showScene(destination);
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
    this.showScene(0);
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

  showScene(index) {
    if (!Number.isInteger(index)) return;
    this.index = Math.max(0, Math.min(index, this.scenes.length - 1));
    this.scenes.forEach((scene, number) => { scene.hidden = number !== this.index; });
    this.buttons.forEach((button) => {
      button.disabled = ["first", "previous"].includes(button.dataset.action)
        ? this.index === 0 : this.index === this.scenes.length - 1;
    });
    if (this.buttons.includes(document.activeElement) && document.activeElement.disabled) {
      const action = this.index === 0 ? "next" : "previous";
      this.buttons.find((button) => button.dataset.action === action && !button.disabled)?.focus();
    }
    const caption = this.config.scenes[this.index].caption;
    this.status.textContent = `Scene ${this.index + 1} of ${this.scenes.length}${caption ? `: ${caption}` : ""}`;
    this.dataset.scene = String(this.index + 1);
  }

  revealHashTarget(hash = window.location.hash, scroll = true) {
    let id;
    try { id = decodeURIComponent(hash.replace(/^#/, "")); } catch { return; }
    if (!id) return;
    const target = document.getElementById(id);
    const scene = target?.closest("tb-scene");
    const index = this.scenes.indexOf(scene);
    if (index < 0) return;
    this.showScene(index);
    if (scroll) target.scrollIntoView?.({ block: "nearest" });
  }
}

if (!customElements.get("tb-animation")) customElements.define("tb-animation", TbAnimation);
