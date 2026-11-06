import { createRunner } from "./tb-code/runners.js";
import { cleanArgumentList, cleanParameters, splitArguments } from "./tb-code/arguments.js";
import { tutorLanguage, tutorLanguageLabel, tutorUrl, compilerExplorerUrl } from "./tb-code/tools.js";
import { renderOutput } from "./tb-code/output.js";

class TbCode extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.config = this.readConfig();
    this.source = this.config.source || "";
    this.sourceDisplay = this.querySelector(":scope > .tb-code__fallback code")
      || this.querySelector(":scope > .tb-code__fallback pre");
    this.fallback = this.querySelector(":scope > .tb-code__fallback");
    this.sourceListing = this.fallback?.querySelector(":scope > .highlight, :scope > pre");
    this.editorSlot = document.createElement("div");
    this.editorSlot.className = "tb-code__editor-slot";
    this.editorSlot.hidden = true;
    if (this.sourceListing) {
      this.sourceListing.before(this.editorSlot);
    } else if (this.fallback) {
      this.fallback.append(this.editorSlot);
    } else {
      this.prepend(this.editorSlot);
    }
    this.editing = false;
    this.revisions = [this.source];
    this.revisionIndex = 0;
    this.renderControls();
    try {
      this.runner = createRunner(this.config);
      this.runner.preload?.();
    } catch (error) {
      this.showError(error.message);
    }
  }

  disconnectedCallback() {
    this.controller?.abort();
    this.cleanupOutput?.();
    this.cleanupOutput = null;
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

    this.tutorButton = document.createElement("button");
    this.tutorButton.type = "button";
    this.tutorButton.className = "tb-code__button tb-code__external-button tb-code__tutor-button";
    this.configureExternalButton(this.tutorButton, `Show in ${tutorLanguageLabel(this.config)} Tutor`);
    // Bootstrap Icons mortarboard-fill (MIT); license in bootstrap-icons-LICENSE.txt.
    const tutorIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    tutorIcon.setAttribute("viewBox", "0 0 16 16");
    tutorIcon.setAttribute("aria-hidden", "true");
    tutorIcon.innerHTML = '<path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.5 3.5a.5.5 0 0 0 .025.917l7.5 3a.5.5 0 0 0 .372 0L14 7.14V13a1 1 0 0 0-1 1v2h3v-2a1 1 0 0 0-1-1V6.739l.686-.275a.5.5 0 0 0 .025-.917z"/><path d="M4.176 9.032a.5.5 0 0 0-.656.327l-.5 1.7a.5.5 0 0 0 .294.605l4.5 1.8a.5.5 0 0 0 .372 0l4.5-1.8a.5.5 0 0 0 .294-.605l-.5-1.7a.5.5 0 0 0-.656-.327L8 10.466z"/>';
    this.tutorButton.append(tutorIcon);
    this.tutorButton.hidden = !(this.config.showTutor && tutorLanguage(this.config));
    this.tutorButton.addEventListener("click", () => this.openExternal(tutorUrl(this.config, this.executionSource(this.currentSource()))));

    this.compilerExplorerButton = document.createElement("button");
    this.compilerExplorerButton.type = "button";
    this.compilerExplorerButton.className = "tb-code__button tb-code__external-button tb-code__compiler-explorer-button";
    this.configureExternalButton(this.compilerExplorerButton, "Show in Compiler Explorer");
    // Compiler Explorer mark (BSD 2-Clause); license in compiler-explorer-LICENSE.txt.
    const compilerExplorerIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    compilerExplorerIcon.setAttribute("viewBox", "0 0 270 270");
    compilerExplorerIcon.setAttribute("aria-hidden", "true");
    for (const pathData of [
      "M228.18 192.43c-1.1-2.1-1.1-4.6 0-6.6 1.4-2.5 2.6-5 3.8-7.6.8-1.9-.5-4-2.6-4h-22.5c-2.3 0-4.5 1.2-5.7 3.1-2.9 4.4-6.3 8.7-10.1 12.5-14.5 14.5-33.7 22.4-54.1 22.4-20.5 0-39.7-8-54.1-22.4-14.6-14.4-22.5-33.6-22.5-54.1s8-39.7 22.4-54.1c14.5-14.5 33.7-22.4 54.1-22.4 20.5 0 39.7 8 54.1 22.4 3.9 3.9 7.2 8.1 10.1 12.5 1.3 1.9 3.4 3.1 5.7 3.1h22.6c2.1 0 3.4-2.1 2.6-4-1.2-2.6-2.4-5.1-3.8-7.6-1.1-2.1-1.1-4.6 0-6.6l7.6-13.8c1.5-2.7 1-6-1.2-8.2l-19.1-19.1c-2.2-2.2-5.5-2.6-8.2-1.2l-13.9 7.7c-2.1 1.1-4.6 1.1-6.6 0-6.6-3.6-13.6-6.5-20.8-8.6-2.3-.7-4.1-2.4-4.7-4.7l-4.4-15.2c-.9-2.9-3.5-5-6.6-5h-27c-3.1 0-5.8 2-6.6 5l-4.4 15.2c-.7 2.3-2.4 4-4.7 4.7-7.2 2.1-14.2 5-20.8 8.6-2.1 1.1-4.6 1.2-6.6 0l-13.9-7.7c-2.7-1.5-6-1-8.2 1.2l-19.1 19.1c-2.2 2.2-2.6 5.5-1.2 8.2l7.7 13.9c1.1 2.1 1.1 4.6 0 6.6-3.6 6.6-6.5 13.6-8.6 20.8-.7 2.3-2.4 4.1-4.7 4.7l-15.2 4.4c-2.9.9-5 3.5-5 6.6v27c0 3.1 2 5.8 5 6.6l15.2 4.4c2.3.7 4 2.4 4.7 4.7 2.1 7.2 5 14.2 8.6 20.8 1.1 2.1 1.2 4.6 0 6.6l-7.7 13.9c-1.5 2.7-1 6 1.2 8.2l19.1 19.1c2.2 2.2 5.5 2.6 8.2 1.2l13.9-7.7c2.1-1.1 4.6-1.1 6.6 0 6.6 3.6 13.6 6.5 20.8 8.6 2.3.7 4.1 2.4 4.7 4.7l4.4 15.2c.9 2.9 3.5 5 6.6 5h27c3.1 0 5.8-2 6.6-5l4.4-15.2c.7-2.3 2.4-4 4.7-4.7 7.2-2.1 14.2-5 20.8-8.6 2.1-1.1 4.6-1.2 6.6 0l13.9 7.7c2.7 1.5 6 1 8.2-1.2l19.1-19.1c2.2-2.2 2.6-5.5 1.2-8.2z",
      "M91.08 96.83h92.7v17.2h-92.7zm0 30.6h76.4v17.2h-76.4zm0 30.6h92.7v17.2h-92.7z",
    ]) {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", pathData);
      compilerExplorerIcon.append(path);
    }
    this.compilerExplorerButton.append(compilerExplorerIcon);
    this.compilerExplorerButton.hidden = !this.config.compilerExplorer;
    this.compilerExplorerButton.addEventListener("click", () => this.openExternal(compilerExplorerUrl(this.config, this.executionSource(this.currentSource()))));

    this.editButton = document.createElement("button");
    this.editButton.type = "button";
    this.editButton.className = "tb-code__button";
    this.editButton.textContent = this.config.editLabel || "Edit";
    this.editButton.hidden = this.config.readonly === true;
    this.editButton.setAttribute("aria-expanded", "false");
    this.editButton.setAttribute("aria-controls", `${this.safeId()}-editor`);
    this.editButton.addEventListener("click", () => this.toggleEditor());

    this.stopButton = document.createElement("button");
    this.stopButton.type = "button";
    this.stopButton.className = "tb-code__button";
    this.stopButton.textContent = "Stop";
    this.stopButton.hidden = true;
    this.stopButton.addEventListener("click", () => this.controller?.abort());
    controls.append(this.runButton, this.stopButton, this.editButton, this.tutorButton, this.compilerExplorerButton);

    const editorLabel = document.createElement("label");
    editorLabel.className = "tb-code__editor-label tb-code__visually-hidden";
    editorLabel.htmlFor = `${this.safeId()}-editor`;
    editorLabel.textContent = "Editable source code";
    this.editor = document.createElement("textarea");
    this.editor.id = editorLabel.htmlFor;
    this.editor.className = "tb-code__editor";
    this.editor.value = this.source;
    this.editor.hidden = true;
    this.editor.addEventListener("change", () => this.captureCurrentRevision());
    editorLabel.hidden = true;
    this.editorLabel = editorLabel;
    this.editorSlot.append(editorLabel, this.editor);

    this.revisionControl = document.createElement("div");
    this.revisionControl.className = "tb-code__revision-control";
    this.revisionControl.hidden = true;

    this.revisionLabel = document.createElement("label");
    this.revisionLabel.className = "tb-code__revision-label";
    this.revisionLabel.htmlFor = `${this.safeId()}-revision`;
    this.revisionLabel.textContent = this.config.revisionLabel || "Source version";

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

    if (this.hasConfiguredStdin()) {
      const stdinField = this.createRuntimeInput(
        "stdin",
        "Standard input",
        this.config.stdin,
      );
      this.stdinInput = stdinField.input;
      this.runtimeInputs.appendChild(stdinField.wrapper);
    }

    const runargs = cleanArgumentList(this.config.parameters?.runargs || []);
    if (runargs.length > 0) {
      const runargsField = this.createRuntimeInput(
        "runargs",
        "Run arguments",
        runargs.join(" "),
      );
      this.runargsInput = runargsField.input;
      this.runtimeInputs.appendChild(runargsField.wrapper);
    }

    this.attachedFiles = document.createElement("div");
    this.attachedFiles.className = "tb-code__attached-files";
    this.renderAttachedFiles();

    this.status = document.createElement("div");
    this.status.className = "tb-code__status";
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.status.setAttribute("aria-atomic", "true");

    const outputLabel = document.createElement("div");
    outputLabel.className = "tb-code__output-label";
    outputLabel.id = `${this.safeId()}-output-label`;
    outputLabel.textContent = "Program output";

    this.output = document.createElement("div");
    this.output.className = "tb-code__output";
    this.output.tabIndex = 0;
    this.output.setAttribute("role", "group");
    this.output.setAttribute("aria-label", "Execution results");
    this.output.setAttribute("aria-describedby", outputLabel.id);

    this.append(
      controls,
      this.revisionControl,
      this.runtimeInputs,
      this.attachedFiles,
      this.status,
      outputLabel,
      this.output,
    );
  }

  configureExternalButton(button, label) {
    button.setAttribute("aria-label", label);
    button.dataset.tooltip = label;
    button.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        button.dataset.tooltipDismissed = "true";
      }
    });
    button.addEventListener("blur", () => {
      delete button.dataset.tooltipDismissed;
    });
    button.addEventListener("mouseleave", () => {
      delete button.dataset.tooltipDismissed;
    });
  }

  hasRuntimeInputs() {
    return this.hasConfiguredStdin() || cleanArgumentList(this.config.parameters?.runargs || []).length > 0;
  }

  hasConfiguredStdin() {
    return Object.hasOwn(this.config, "stdin");
  }

  attachedFileConfigs() {
    return Array.isArray(this.config.files) ? this.config.files : [];
  }

  renderAttachedFiles() {
    const files = this.attachedFileConfigs().filter((file) => !file.hidden);
    this.attachedFiles.hidden = files.length === 0;
    if (!files.length) return;

    const heading = document.createElement("div");
    heading.className = "tb-code__attached-files-label";
    heading.textContent = "Attached files";
    this.attachedFiles.appendChild(heading);

    for (const file of files) {
      const wrapper = document.createElement("div");
      wrapper.className = "tb-code__attached-file";

      if (file.href) {
        const link = document.createElement("a");
        link.className = "tb-code__attached-file-link";
        link.href = file.href;
        link.textContent = file.filename;
        wrapper.append(link);
      } else {
        const note = document.createElement("div");
        note.className = "tb-code__attached-file-note";
        note.textContent = `${file.filename} (${file.mime_type || "application/octet-stream"} file)`;
        wrapper.append(note);
      }

      this.attachedFiles.appendChild(wrapper);
    }
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
    const fallbackHeight = this.sourceListing?.getBoundingClientRect().height;
    if (fallbackHeight) {
      const height = `${Math.ceil(fallbackHeight)}px`;
      this.editor.style.height = height;
      this.editor.style.minHeight = height;
    }
    if (this.sourceListing) {
      this.sourceListing.hidden = true;
    }
    this.editorSlot.hidden = false;
    this.editor.hidden = false;
    this.editorLabel.hidden = false;
    this.updateRevisionControl();
    this.editButton.textContent = this.config.hideEditLabel || "Hide editor";
    this.editButton.setAttribute("aria-expanded", "true");
    this.editor.focus();
  }

  hideEditor() {
    this.captureCurrentRevision();
    this.editing = false;
    this.editorSlot.hidden = true;
    if (this.sourceListing) {
      this.sourceListing.hidden = false;
    }
    this.editor.hidden = true;
    this.editorLabel.hidden = true;
    this.editor.style.height = "";
    this.editor.style.minHeight = "";
    this.editButton.textContent = this.config.editLabel || "Edit";
    this.editButton.setAttribute("aria-expanded", "false");
  }

  captureCurrentRevision() {
    const source = this.editor.value;
    if (source === this.revisions[this.revisionIndex]) {
      return;
    }
    const retained = this.revisions.slice(0, this.revisionIndex + 1);
    retained.push(source);
    this.revisions = retained;
    this.revisionIndex = this.revisions.length - 1;
    this.updateSourceDisplay(source);
    this.updateRevisionControl();
  }

  loadRevision(index) {
    if (index < 0 || index >= this.revisions.length) {
      return;
    }
    this.revisionIndex = index;
    this.editor.value = this.revisions[index];
    this.updateSourceDisplay(this.revisions[index]);
    this.updateRevisionControl();
    this.status.textContent = `Loaded source version ${index + 1}.`;
  }

  updateSourceDisplay(source) {
    if (!this.sourceDisplay) {
      return;
    }
    const fragment = document.createDocumentFragment();
    const emphasized = new Set(this.config.emphasizeLines || []);
    const lineNumberStart = Number.isInteger(this.config.lineNumberStart)
      ? this.config.lineNumberStart
      : 1;
    const lines = source.split("\n");
    const lineNumberWidth = String(lineNumberStart + lines.length - 1).length;

    lines.forEach((line, index) => {
      const lineContent = document.createDocumentFragment();
      if (this.config.lineNumbers === true) {
        const number = document.createElement("span");
        number.className = "linenos";
        number.textContent = String(lineNumberStart + index).padStart(lineNumberWidth);
        lineContent.appendChild(number);
      }
      lineContent.appendChild(document.createTextNode(line));

      if (emphasized.has(index + 1)) {
        const highlight = document.createElement("span");
        highlight.className = "hll";
        highlight.appendChild(lineContent);
        fragment.appendChild(highlight);
      } else {
        fragment.appendChild(lineContent);
      }
      if (index < lines.length - 1) {
        fragment.appendChild(document.createTextNode("\n"));
      }
    });
    this.sourceDisplay.replaceChildren(fragment);
  }

  updateRevisionControl() {
    if (!this.revisionSlider || !this.revisionOutput) {
      return;
    }
    this.revisionSlider.max = String(this.revisions.length);
    this.revisionSlider.value = String(this.revisionIndex + 1);
    this.revisionOutput.value = `${this.revisionIndex + 1} of ${this.revisions.length}`;
    this.revisionControl.hidden = this.revisions.length <= 1;
  }

  async runCode() {
    if (this.controller) return;
    const controller = new AbortController();
    this.controller = controller;
    this.setBusy(true, "Running...");
    this.cleanupOutput?.();
    this.cleanupOutput = null;
    try {
      this.runner ||= createRunner(this.config);
      const request = {
        source: this.executionSource(this.currentSource()),
        parameters: this.runtimeParameters(),
        files: this.runtimeFiles(),
      };
      if (this.hasConfiguredStdin()) request.input = this.stdinInput?.value ?? this.config.stdin;
      const onStatus = (message) => { this.status.textContent = message; };
      const result = await this.runner.run(request, { signal: controller.signal, onStatus });
      if (controller.signal.aborted || !this.isConnected) return;
      this.cleanupOutput = renderOutput(this.output, result, { onStatus });
      this.status.textContent = result.status;
    } catch (error) {
      if (this.isConnected) {
        this.showError(error.name === "AbortError" ? "Run cancelled." : error.message || "Unable to run the program.");
        if (error.name === "AbortError") this.status.textContent = "Run cancelled.";
      }
    } finally {
      this.controller = null;
      this.setBusy(false);
    }
  }

  openExternal(url) {
    if (url) window.open(url, "_blank", "noopener");
  }

  currentSource() {
    if (!this.editor.hidden) {
      this.captureCurrentRevision();
    }
    return this.editor.hidden ? this.revisions[this.revisionIndex] : this.editor.value;
  }

  executionSource(source) {
    const parts = [
      ...this.sourceFragments(this.config.runBefore),
      source,
      ...this.sourceFragments(this.config.runAfter),
    ].filter((part) => part.length > 0);
    return parts.join("\n");
  }

  sourceFragments(value) {
    if (!Array.isArray(value)) {
      return [];
    }
    return value.map((fragment) => String(fragment));
  }

  runtimeParameters() {
    const parameters = cleanParameters(this.config.parameters || {});
    if (this.runargsInput) {
      const runargs = splitArguments(this.runargsInput.value);
      if (runargs.length > 0) {
        parameters.runargs = runargs;
      } else {
        delete parameters.runargs;
      }
    }
    return parameters;
  }

  runtimeFiles() {
    return this.attachedFileConfigs().map((file) => ({
      filename: file.filename,
      mime_type: file.mime_type || "application/octet-stream",
      encoding: file.is_text ? "text" : "base64",
      content: file.is_text ? this.sourceFileContent(file) : file.data_url || "",
    }));
  }

  sourceFileContent(file) {
    const source = file.source_id ? document.getElementById(file.source_id) : null;
    if (typeof source?.getFileContent === "function") {
      return source.getFileContent();
    }
    return file.content || "";
  }

  showError(message) {
    this.cleanupOutput?.();
    this.cleanupOutput = renderOutput(this.output, { kind: "text", text: message });
    this.status.textContent = "Run failed.";
  }

  setBusy(isBusy, message) {
    const stopFocused = document.activeElement === this.stopButton;
    this.runButton.disabled = isBusy;
    this.stopButton.hidden = !isBusy;
    this.runButton.setAttribute("aria-busy", String(isBusy));
    this.status.textContent = isBusy ? (message || "Running...") : this.status.textContent;
    if (!isBusy && stopFocused && this.isConnected) this.runButton.focus();
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
