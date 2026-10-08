// Run after sphinx-accessibility has inserted its menu and restored preferences.
document.addEventListener("DOMContentLoaded", () => {
  const host = document.querySelector(".article-header-buttons");
  // The spelling of this ID comes from sphinx-accessibility 1.x.
  const menu = host?.querySelector("#AcccessibilityMenu");
  if (!menu) return;

  const toggle = menu.querySelector(".dropdown-toggle");
  toggle.id = "touchbook-accessibility-toggle";
  toggle.className = "nav-link d-flex py-2 px-0 px-xl-2 dropdown-toggle align-items-center";
  toggle.setAttribute("aria-label", host.dataset.accessibilityLabel);
  toggle.setAttribute("data-bs-display", "static");
  const label = document.createElement("span");
  label.className = "d-xl-none ms-2";
  label.textContent = host.dataset.accessibilityLabel;
  toggle.append(label);

  const panel = menu.querySelector(".dropdown-menu");
  panel.classList.add("dropdown-menu-end");
  panel.setAttribute("aria-labelledby", toggle.id);

  // Keep the extension's delegated actions while using native toggle buttons.
  for (const link of menu.querySelectorAll("a[data-action]")) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "dropdown-item d-flex align-items-center gap-2";
    button.dataset.action = link.dataset.action;
    button.setAttribute("aria-label", link.dataset.action === "toggleFont"
      ? host.dataset.fontLabel : host.dataset.contrastLabel);
    button.append(...link.childNodes);
    link.replaceWith(button);
  }
  for (const svg of menu.querySelectorAll("svg")) {
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("focusable", "false");
    svg.removeAttribute("id");
  }

  function syncState() {
    menu.querySelector('[data-action="toggleFont"]').setAttribute(
      "aria-pressed", String(document.body.classList.contains("dyslexic")));
    menu.querySelector('[data-action="toggleContrast"]').setAttribute(
      "aria-pressed", String(document.body.classList.contains("high-contrast")));
  }
  syncState();
  // The extension registered its click listener first, so state is now updated.
  menu.addEventListener("click", syncState);
});
