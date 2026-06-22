class TbFile extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.config = this.readConfig();
    if (!this.config.isText || this.config.editable === false) {
      return;
    }
    this.editing = false;
    this.renderEditor();
  }

  readConfig() {
    const script = this.querySelector(":scope > script.tb-file__config");
    if (!script) {
      return {};
    }
    try {
      return JSON.parse(script.textContent);
    } catch (error) {
      return {};
    }
  }

  renderEditor() {
    const controls = document.createElement("div");
    controls.className = "tb-file__controls";

    this.editButton = document.createElement("button");
    this.editButton.type = "button";
    this.editButton.className = "tb-file__button";
    this.editButton.textContent = this.config.editLabel || "Edit";
    this.editButton.setAttribute("aria-expanded", "false");
    this.editButton.setAttribute("aria-controls", `${this.safeId()}-editor`);
    this.editButton.addEventListener("click", () => this.toggleEditor());
    controls.appendChild(this.editButton);

    const label = document.createElement("label");
    label.className = "tb-file__editor-label";
    label.htmlFor = `${this.safeId()}-editor`;
    label.textContent = `Editable file content for ${this.config.filename || "file"}`;
    label.hidden = true;

    this.editor = document.createElement("textarea");
    this.editor.id = label.htmlFor;
    this.editor.className = "tb-file__editor";
    this.editor.value = this.config.content || "";
    this.editor.hidden = true;
    this.editor.addEventListener("input", () => this.updateFallback());

    this.editorLabel = label;
    this.append(controls, label, this.editor);
  }

  toggleEditor() {
    if (this.editing) {
      this.hideEditor();
    } else {
      this.showEditor();
    }
  }

  showEditor() {
    this.editing = true;
    this.editor.hidden = false;
    this.editorLabel.hidden = false;
    this.editButton.textContent = this.config.hideEditLabel || "Hide editor";
    this.editButton.setAttribute("aria-expanded", "true");
    this.editor.focus();
  }

  hideEditor() {
    this.editing = false;
    this.editor.hidden = true;
    this.editorLabel.hidden = true;
    this.editButton.textContent = this.config.editLabel || "Edit";
    this.editButton.setAttribute("aria-expanded", "false");
  }

  updateFallback() {
    const code = this.querySelector(".tb-file__content code");
    if (code) {
      code.textContent = this.editor.value;
    }
  }

  safeId() {
    if (!this.id) {
      this.id = `tb-file-${TbFile.nextId++}`;
    }
    return this.id;
  }
}

TbFile.nextId = 1;

if (!customElements.get("tb-file")) {
  customElements.define("tb-file", TbFile);
}
