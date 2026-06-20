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

      button.addEventListener("click", () => this.selectTab(index));
      button.addEventListener("keydown", (event) => this.onKeydown(event, index));

      tablist.appendChild(button);
      panels.appendChild(panel);
    });

    this.append(tablist, panels);
  }

  selectTab(index) {
    const tabs = Array.from(this.querySelectorAll(".tb-group__tab"));
    const panels = Array.from(this.querySelectorAll(".tb-group__panel"));

    tabs.forEach((tab, tabIndex) => {
      const selected = tabIndex === index;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });

    panels.forEach((panel, panelIndex) => {
      panel.hidden = panelIndex !== index;
    });

    tabs[index].focus();
  }

  onKeydown(event, index) {
    const tabs = this.querySelectorAll(".tb-group__tab");
    const last = tabs.length - 1;
    let next = null;

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

  safeId() {
    if (!this.id) {
      this.id = `tb-group-${TbGroup.nextId++}`;
    }
    return this.id;
  }
}

TbGroup.nextId = 1;

customElements.define("tb-group", TbGroup);
