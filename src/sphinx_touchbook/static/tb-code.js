class TbCode extends HTMLElement {
  static languagesByEndpoint = new Map();
  static languagePreloadsByEndpoint = new Map();

  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.config = this.readConfig();
    this.source = this.config.source || "";
    this.editing = false;
    this.revisions = [this.source];
    this.revisionIndex = 0;
    this.editorDirty = false;
    this.renderControls();
    this.preloadSupportedLanguages();
  }

  readConfig() {
    const script = this.querySelector(":scope > script.tb-code__config");
    if (!script) {
      return {};
    }
    try {
      return JSON.parse(script.textContent);
    } catch (error) {
      return {};
    }
  }

  renderControls() {
    const controls = document.createElement("div");
    controls.className = "tb-code__controls";

    this.runButton = document.createElement("button");
    this.runButton.type = "button";
    this.runButton.className = "tb-code__button";
    this.runButton.textContent = this.config.runLabel || "Run";
    this.runButton.addEventListener("click", () => this.runCode());

    this.editButton = document.createElement("button");
    this.editButton.type = "button";
    this.editButton.className = "tb-code__button";
    this.editButton.textContent = this.config.editLabel || "Edit";
    this.editButton.hidden = this.config.editable === false;
    this.editButton.setAttribute("aria-expanded", "false");
    this.editButton.setAttribute("aria-controls", `${this.safeId()}-editor`);
    this.editButton.addEventListener("click", () => this.toggleEditor());

    controls.append(this.runButton, this.editButton);

    const editorLabel = document.createElement("label");
    editorLabel.className = "tb-code__editor-label";
    editorLabel.htmlFor = `${this.safeId()}-editor`;
    editorLabel.textContent = "Editable source code";
    this.editor = document.createElement("textarea");
    this.editor.id = editorLabel.htmlFor;
    this.editor.className = "tb-code__editor";
    this.editor.value = this.source;
    this.editor.hidden = true;
    this.editor.addEventListener("input", () => {
      this.editorDirty = true;
    });
    this.editor.addEventListener("change", () => this.captureCurrentRevision());
    editorLabel.hidden = true;
    this.editorLabel = editorLabel;

    this.revisionControl = document.createElement("div");
    this.revisionControl.className = "tb-code__revision-control";
    this.revisionControl.hidden = true;

    this.revisionLabel = document.createElement("label");
    this.revisionLabel.className = "tb-code__revision-label";
    this.revisionLabel.htmlFor = `${this.safeId()}-revision`;
    this.revisionLabel.textContent = this.config.revisionLabel || "Editor revision";

    this.revisionSlider = document.createElement("input");
    this.revisionSlider.id = this.revisionLabel.htmlFor;
    this.revisionSlider.className = "tb-code__revision-slider";
    this.revisionSlider.type = "range";
    this.revisionSlider.min = "1";
    this.revisionSlider.max = "1";
    this.revisionSlider.step = "1";
    this.revisionSlider.value = "1";
    this.revisionSlider.addEventListener("input", () => this.loadRevision(Number(this.revisionSlider.value) - 1));

    this.revisionOutput = document.createElement("output");
    this.revisionOutput.className = "tb-code__revision-output";
    this.revisionOutput.setAttribute("for", this.revisionSlider.id);
    this.revisionControl.append(this.revisionLabel, this.revisionSlider, this.revisionOutput);
    this.updateRevisionControl();

    this.runtimeInputs = document.createElement("div");
    this.runtimeInputs.className = "tb-code__runtime-inputs";
    this.runtimeInputs.hidden = !this.hasRuntimeInputs();

    if (this.config.stdin) {
      const stdinField = this.createRuntimeInput(
        "stdin",
        "Standard input",
        this.config.stdin,
      );
      this.stdinInput = stdinField.input;
      this.runtimeInputs.appendChild(stdinField.wrapper);
    }

    const runargs = this.cleanArgumentList(this.config.parameters?.runargs || []);
    if (runargs.length > 0) {
      const runargsField = this.createRuntimeInput(
        "runargs",
        "Run arguments",
        runargs.join(" "),
      );
      this.runargsInput = runargsField.input;
      this.runtimeInputs.appendChild(runargsField.wrapper);
    }

    this.status = document.createElement("div");
    this.status.className = "tb-code__status";
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");

    const outputLabel = document.createElement("div");
    outputLabel.className = "tb-code__output-label";
    outputLabel.id = `${this.safeId()}-output-label`;
    outputLabel.textContent = "Program output";

    this.output = document.createElement("pre");
    this.output.className = "tb-code__output";
    this.output.tabIndex = 0;
    this.output.setAttribute("aria-labelledby", outputLabel.id);

    this.append(
      controls,
      editorLabel,
      this.editor,
      this.revisionControl,
      this.runtimeInputs,
      this.status,
      outputLabel,
      this.output,
    );
  }

  hasRuntimeInputs() {
    return Boolean(this.config.stdin) || this.cleanArgumentList(this.config.parameters?.runargs || []).length > 0;
  }

  createRuntimeInput(name, labelText, value) {
    const wrapper = document.createElement("div");
    wrapper.className = "tb-code__runtime-field";

    const label = document.createElement("label");
    label.className = "tb-code__runtime-label";
    label.htmlFor = `${this.safeId()}-${name}`;
    label.textContent = labelText;

    const input = document.createElement("input");
    input.id = label.htmlFor;
    input.className = "tb-code__runtime-input";
    input.type = "text";
    input.value = value;

    wrapper.append(label, input);
    return { wrapper, input };
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
    this.revisionControl.hidden = false;
    this.editButton.textContent = this.config.hideEditLabel || "Hide editor";
    this.editButton.setAttribute("aria-expanded", "true");
    this.editor.focus();
  }

  hideEditor() {
    this.captureCurrentRevision();
    this.editing = false;
    this.editor.hidden = true;
    this.editorLabel.hidden = true;
    this.revisionControl.hidden = true;
    this.editButton.textContent = this.config.editLabel || "Edit";
    this.editButton.setAttribute("aria-expanded", "false");
  }

  captureCurrentRevision() {
    const source = this.editor.value;
    if (source === this.revisions[this.revisionIndex]) {
      this.editorDirty = false;
      return;
    }
    const retained = this.revisions.slice(0, this.revisionIndex + 1);
    retained.push(source);
    this.revisions = retained;
    this.revisionIndex = this.revisions.length - 1;
    this.editorDirty = false;
    this.updateRevisionControl();
  }

  loadRevision(index) {
    if (index < 0 || index >= this.revisions.length) {
      return;
    }
    this.revisionIndex = index;
    this.editor.value = this.revisions[index];
    this.editorDirty = false;
    this.updateRevisionControl();
    this.status.textContent = `Loaded editor revision ${index + 1}.`;
  }

  updateRevisionControl() {
    if (!this.revisionSlider || !this.revisionOutput) {
      return;
    }
    this.revisionSlider.max = String(this.revisions.length);
    this.revisionSlider.value = String(this.revisionIndex + 1);
    this.revisionOutput.value = `${this.revisionIndex + 1} of ${this.revisions.length}`;
  }

  async runCode() {
    const endpoint = this.config.endpoint;
    if (!endpoint) {
      this.showError("No execution endpoint is configured.");
      return;
    }

    if (!this.editor.hidden) {
      this.captureCurrentRevision();
    }
    const source = this.editor.hidden ? this.revisions[this.revisionIndex] : this.editor.value;
    const languageId = this.config.jobeLanguage || this.config.language || "python3";
    const payload = {
      run_spec: {
        language_id: languageId,
        sourcecode: source,
        parameters: this.runtimeParameters(),
      },
    };
    if (this.stdinInput) {
      payload.run_spec.input = this.stdinInput.value;
    } else if (this.config.stdin) {
      payload.run_spec.input = this.config.stdin;
    }

    this.setBusy(true, "Checking language support...");
    try {
      const supportedLanguages = await this.fetchSupportedLanguages();
      if (supportedLanguages && !supportedLanguages.has(languageId)) {
        this.showError(`The execution service does not currently report support for ${languageId}.`);
        return;
      }

      this.status.textContent = "Running...";
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Accept": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`Execution service returned ${response.status}.`);
      }
      const result = await response.json();
      this.renderResult(result);
    } catch (error) {
      this.showError(error.message || "Unable to run the program.");
    } finally {
      this.setBusy(false);
    }
  }

  cleanParameters(parameters) {
    const cleaned = {};
    for (const [key, value] of Object.entries(parameters)) {
      const cleanedValue = this.cleanArgumentList(value);
      if (cleanedValue.length > 0) {
        cleaned[key] = cleanedValue;
      }
    }
    return cleaned;
  }

  runtimeParameters() {
    const parameters = this.cleanParameters(this.config.parameters || {});
    if (this.runargsInput) {
      const runargs = this.splitArguments(this.runargsInput.value);
      if (runargs.length > 0) {
        parameters.runargs = runargs;
      } else {
        delete parameters.runargs;
      }
    }
    return parameters;
  }

  cleanArgumentList(value) {
    if (!Array.isArray(value)) {
      return [];
    }
    return value.map((item) => String(item)).filter((item) => item.length > 0);
  }

  splitArguments(value) {
    const args = [];
    let current = "";
    let quote = null;
    let escaped = false;

    for (const character of value.trim()) {
      if (escaped) {
        current += character;
        escaped = false;
      } else if (character === "\\") {
        escaped = true;
      } else if (quote) {
        if (character === quote) {
          quote = null;
        } else {
          current += character;
        }
      } else if (character === '"' || character === "'") {
        quote = character;
      } else if (/\s/.test(character)) {
        if (current) {
          args.push(current);
          current = "";
        }
      } else {
        current += character;
      }
    }

    if (escaped) {
      current += "\\";
    }
    if (current) {
      args.push(current);
    }
    return args;
  }

  async fetchSupportedLanguages() {
    if (this.config.validateLanguage === false || !this.config.languagesEndpoint) {
      return null;
    }
    if (TbCode.languagesByEndpoint.has(this.config.languagesEndpoint)) {
      return TbCode.languagesByEndpoint.get(this.config.languagesEndpoint);
    }
    return this.loadSupportedLanguages(2500);
  }

  preloadSupportedLanguages() {
    if (this.config.validateLanguage === false || !this.config.languagesEndpoint) {
      return;
    }
    if (TbCode.languagesByEndpoint.has(this.config.languagesEndpoint)) {
      return;
    }
    if (TbCode.languagePreloadsByEndpoint.has(this.config.languagesEndpoint)) {
      return;
    }

    const preload = this.loadSupportedLanguages(15000).finally(() => {
      TbCode.languagePreloadsByEndpoint.delete(this.config.languagesEndpoint);
    });
    TbCode.languagePreloadsByEndpoint.set(this.config.languagesEndpoint, preload);
  }

  async loadSupportedLanguages(timeoutMs) {
    try {
      const response = await this.fetchWithTimeout(
        this.config.languagesEndpoint,
        { headers: { "Accept": "application/json" } },
        timeoutMs,
      );
      if (!response.ok) {
        return null;
      }
      const payload = await response.json();
      const languageIds = Array.isArray(payload)
        ? payload.map((entry) => Array.isArray(entry) ? entry[0] : entry)
        : [];
      const languages = new Set(languageIds.filter(Boolean));
      TbCode.languagesByEndpoint.set(this.config.languagesEndpoint, languages);
      return languages;
    } catch (error) {
      return null;
    }
  }

  async fetchWithTimeout(url, options, timeoutMs) {
    if (typeof AbortController === "undefined") {
      return fetch(url, options);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timeoutId);
    }
  }

  renderResult(result) {
    const stdout = result.stdout || "";
    const stderr = result.stderr || "";
    const cmpinfo = result.cmpinfo || "";
    const output = [stdout, stderr, cmpinfo].filter(Boolean).join("\n");
    this.output.textContent = output || "(no output)";
    this.status.textContent = result.outcome === 15 ? "Run complete." : `Run finished with outcome ${result.outcome}.`;
  }

  showError(message) {
    this.output.textContent = message;
    this.status.textContent = "Run failed.";
  }

  setBusy(isBusy, message) {
    this.runButton.disabled = isBusy;
    this.runButton.setAttribute("aria-busy", String(isBusy));
    this.status.textContent = isBusy ? (message || "Running...") : this.status.textContent;
  }

  safeId() {
    if (!this.id) {
      this.id = `tb-code-${TbCode.nextId++}`;
    }
    return this.id;
  }
}

TbCode.nextId = 1;

customElements.define("tb-code", TbCode);
