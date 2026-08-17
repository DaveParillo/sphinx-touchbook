class TbGroup extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";

    const tabs = Array.from(this.querySelectorAll(":scope > .tb-group__fallback > tb-tab"));
    if (tabs.length === 0) {
      return;
    }

    const fallback = this.querySelector(":scope > .tb-group__fallback");
    fallback.hidden = true;

    const tablist = document.createElement("div");
    tablist.className = "tb-group__tablist";
    tablist.setAttribute("role", "tablist");

    const panels = document.createElement("div");
    panels.className = "tb-group__panels";

    tabs.forEach((tab, index) => {
      const label = tab.getAttribute("label") || `Tab ${index + 1}`;
      const tabId = `${this.safeId()}-tab-${index}`;
      const panelId = `${this.safeId()}-panel-${index}`;

      const button = document.createElement("button");
      button.type = "button";
      button.className = "tb-group__tab";
      button.id = tabId;
      button.textContent = label;
      button.setAttribute("role", "tab");
      button.setAttribute("aria-controls", panelId);
      button.setAttribute("aria-selected", index === 0 ? "true" : "false");
      button.tabIndex = index === 0 ? 0 : -1;

      const panel = document.createElement("section");
      panel.className = "tb-group__panel";
      panel.id = panelId;
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", tabId);
      panel.hidden = index !== 0;

      const content = tab.querySelector(".tb-tab__content");
      if (content) {
        while (content.firstChild) {
          panel.appendChild(content.firstChild);
        }
      }

      button.addEventListener("pointerdown", () => button.focus());
      button.addEventListener("mousedown", () => button.focus());
      button.addEventListener("click", () => this.selectTab(index));
      button.addEventListener("keydown", (event) => this.onKeydown(event, index));

      tablist.appendChild(button);
      panels.appendChild(panel);
    });

    this.append(tablist, panels);
    this.activateNestedGroups(panels[0]);
    TbGroup.installHashHandler();
    TbGroup.scheduleHashReveal();
  }

  selectTab(index, options = {}) {
    const tabs = this.ownTabs();
    const panels = this.ownPanels();

    tabs.forEach((tab, tabIndex) => {
      const selected = tabIndex === index;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });

    panels.forEach((panel, panelIndex) => {
      panel.hidden = panelIndex !== index;
    });

    this.activateNestedGroups(panels[index]);

    if (options.focus !== false) {
      tabs[index].focus();
    }
  }

  onKeydown(event, index) {
    const tabs = this.ownTabs();
    const last = tabs.length - 1;
    let next = null;

    if (event.key === "Tab" && !event.shiftKey) {
      if (this.focusFirstPanelControl(index)) {
        event.preventDefault();
      }
      return;
    }

    if (event.key === "ArrowRight") {
      next = index === last ? 0 : index + 1;
    } else if (event.key === "ArrowLeft") {
      next = index === 0 ? last : index - 1;
    } else if (event.key === "Home") {
      next = 0;
    } else if (event.key === "End") {
      next = last;
    }

    if (next !== null) {
      event.preventDefault();
      this.selectTab(next);
    }
  }

  focusFirstPanelControl(index) {
    const panel = this.ownPanels()[index];
    if (!panel || panel.hidden) {
      return false;
    }
    const controls = Array.from(panel.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), ' +
      'textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ));
    const control = controls.find((candidate) => !this.isHiddenControl(candidate));
    if (!control) {
      return false;
    }
    control.focus();
    return true;
  }

  isHiddenControl(control) {
    return (
      control.hidden ||
      control.closest("[hidden]") ||
      control.getAttribute("aria-hidden") === "true"
    );
  }

  ownTabs() {
    return Array.from(this.querySelectorAll(":scope > .tb-group__tablist > .tb-group__tab"));
  }

  ownPanels() {
    return Array.from(this.querySelectorAll(":scope > .tb-group__panels > .tb-group__panel"));
  }

  activateNestedGroups(panel) {
    if (!panel) {
      return;
    }

    panel.querySelectorAll("tb-group").forEach((group) => {
      if (group.dataset.enhanced !== "true") {
        return;
      }

      const tabs = group.ownTabs ? group.ownTabs() : [];
      const hasSelectedTab = tabs.some((tab) => tab.getAttribute("aria-selected") === "true");
      if (!hasSelectedTab && tabs.length > 0) {
        group.selectTab(0, { focus: false });
      }
    });
  }

  revealHashTarget(hash) {
    if (!hash || hash === "#") {
      return false;
    }

    const target = this.hashTarget(hash);
    if (!target) {
      return false;
    }

    const panels = this.ownPanels();
    const panelIndex = panels.findIndex((panel) => panel.contains(target));
    if (panelIndex === -1) {
      return false;
    }

    if (panels[panelIndex].hidden) {
      this.selectTab(panelIndex, { focus: false });
    }
    return true;
  }

  hashTarget(hash) {
    const id = TbGroup.decodeHashId(hash);
    if (!id) {
      return null;
    }
    return document.getElementById(id);
  }

  safeId() {
    if (!this.id) {
      this.id = `tb-group-${TbGroup.nextId++}`;
    }
    return this.id;
  }

  static installHashHandler() {
    if (TbGroup.hashHandlerInstalled) {
      return;
    }
    TbGroup.hashHandlerInstalled = true;
    window.addEventListener("hashchange", () => TbGroup.scheduleHashReveal());
    document.addEventListener("click", (event) => {
      const link = event.target.closest("a[href]");
      if (!link) {
        return;
      }
      const target = new URL(link.href, window.location.href);
      if (target.origin !== window.location.origin || target.pathname !== window.location.pathname || !target.hash) {
        return;
      }
      if (target.hash === window.location.hash) {
        TbGroup.scheduleHashReveal();
      }
    });
  }

  static scheduleHashReveal() {
    window.requestAnimationFrame(() => TbGroup.revealCurrentHash());
  }

  static revealCurrentHash() {
    const hash = window.location.hash;
    if (!hash || hash === "#") {
      return;
    }

    let revealed = false;
    document.querySelectorAll("tb-group").forEach((group) => {
      if (typeof group.revealHashTarget === "function") {
        revealed = group.revealHashTarget(hash) || revealed;
      }
    });

    if (!revealed) {
      return;
    }

    const id = TbGroup.decodeHashId(hash);
    const target = id ? document.getElementById(id) : null;
    if (!target) {
      return;
    }
    if (typeof target.scrollIntoView === "function") {
      target.scrollIntoView({ block: "start" });
    }
    if (typeof target.focus === "function" && TbGroup.isNaturallyFocusable(target)) {
      target.focus({ preventScroll: true });
    }
  }

  static isNaturallyFocusable(element) {
    return element.matches(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
      'textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
  }

  static decodeHashId(hash) {
    try {
      return decodeURIComponent(hash.slice(1));
    } catch (error) {
      return "";
    }
  }
}

TbGroup.nextId = 1;
TbGroup.hashHandlerInstalled = false;

customElements.define("tb-group", TbGroup);
