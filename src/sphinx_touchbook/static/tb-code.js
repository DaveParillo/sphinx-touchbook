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
    this.sourceDisplay = this.querySelector(":scope > .tb-code__fallback code")
      || this.querySelector(":scope > .tb-code__fallback pre");
    this.editing = false;
    this.revisions = [this.source];
    this.revisionIndex = 0;
    this.editorDirty = false;
    this.fileEditors = new Map();
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

    this.tutorButton = document.createElement("button");
    this.tutorButton.type = "button";
    this.tutorButton.className = "tb-code__button";
    this.tutorButton.textContent = `Show in ${this.tutorLanguageLabel()} Tutor`;
    this.tutorButton.hidden = !this.canShowTutor();
    this.tutorButton.addEventListener("click", () => this.openTutor());

    this.editButton = document.createElement("button");
    this.editButton.type = "button";
    this.editButton.className = "tb-code__button";
    this.editButton.textContent = this.config.editLabel || "Edit";
    this.editButton.hidden = this.config.editable === false;
    this.editButton.setAttribute("aria-expanded", "false");
    this.editButton.setAttribute("aria-controls", `${this.safeId()}-editor`);
    this.editButton.addEventListener("click", () => this.toggleEditor());

    controls.append(this.runButton, this.editButton, this.tutorButton);

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

    this.attachedFiles = document.createElement("div");
    this.attachedFiles.className = "tb-code__attached-files";
    this.attachedFiles.hidden = !this.hasAttachedFiles();
    if (this.hasAttachedFiles()) {
      this.renderAttachedFiles();
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
      this.attachedFiles,
      this.status,
      outputLabel,
      this.output,
    );
  }

  hasRuntimeInputs() {
    return Boolean(this.config.stdin) || this.cleanArgumentList(this.config.parameters?.runargs || []).length > 0;
  }

  hasAttachedFiles() {
    return this.attachedFileConfigs().length > 0;
  }

  attachedFileConfigs() {
    return Array.isArray(this.config.files) ? this.config.files : [];
  }

  renderAttachedFiles() {
    const heading = document.createElement("div");
    heading.className = "tb-code__attached-files-label";
    heading.textContent = "Attached files";
    this.attachedFiles.appendChild(heading);

    for (const file of this.attachedFileConfigs()) {
      const wrapper = document.createElement("div");
      wrapper.className = "tb-code__attached-file";

      const label = document.createElement("label");
      label.className = "tb-code__attached-file-label";
      label.textContent = file.filename;

      if (file.is_text) {
        const editor = document.createElement("textarea");
        editor.className = "tb-code__attached-file-editor";
        editor.value = file.content || "";
        editor.readOnly = file.editable === false;
        editor.id = `${this.safeId()}-file-${this.fileEditors.size + 1}`;
        label.htmlFor = editor.id;
        this.fileEditors.set(file.filename, editor);
        wrapper.append(label, editor);
      } else {
        const note = document.createElement("div");
        note.className = "tb-code__attached-file-note";
        note.textContent = `${file.mime_type || "application/octet-stream"} file`;
        wrapper.append(label, note);
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
    this.editor.hidden = true;
    this.editorLabel.hidden = true;
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
    this.updateSourceDisplay(source);
    this.updateRevisionControl();
  }

  loadRevision(index) {
    if (index < 0 || index >= this.revisions.length) {
      return;
    }
    this.revisionIndex = index;
    this.editor.value = this.revisions[index];
    this.editorDirty = false;
    this.updateSourceDisplay(this.revisions[index]);
    this.updateRevisionControl();
    this.status.textContent = `Loaded source version ${index + 1}.`;
  }

  updateSourceDisplay(source) {
    if (!this.sourceDisplay) {
      return;
    }
    this.sourceDisplay.replaceChildren(...this.highlightSource(source));
  }

  highlightSource(source) {
    const fragment = document.createDocumentFragment();
    const lines = source.split("\n");
    lines.forEach((line, lineIndex) => {
      this.appendHighlightedLine(fragment, line);
      if (lineIndex < lines.length - 1) {
        fragment.appendChild(document.createTextNode("\n"));
      }
    });
    return Array.from(fragment.childNodes);
  }

  appendHighlightedLine(parent, line) {
    const language = (this.config.language || "").toLowerCase();
    const tokens = this.tokenizeSourceLine(line, language);
    tokens.forEach((token) => {
      if (!token.className) {
        parent.appendChild(document.createTextNode(token.text));
        return;
      }
      const span = document.createElement("span");
      span.className = token.className;
      span.textContent = token.text;
      parent.appendChild(span);
    });
  }

  tokenizeSourceLine(line, language) {
    const tokens = [];
    const keywordClasses = this.keywordClasses(language);
    let index = 0;

    while (index < line.length) {
      const rest = line.slice(index);
      const whitespace = rest.match(/^\s+/);
      if (whitespace) {
        tokens.push({ text: whitespace[0] });
        index += whitespace[0].length;
        continue;
      }

      const comment = this.commentMatch(rest, language);
      if (comment) {
        tokens.push({ text: comment, className: "c1" });
        break;
      }

      const string = rest.match(/^([rubf]*("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'))/i);
      if (string) {
        tokens.push({ text: string[0], className: "s2" });
        index += string[0].length;
        continue;
      }

      const number = rest.match(/^\b\d+(?:\.\d+)?\b/);
      if (number) {
        tokens.push({ text: number[0], className: "mi" });
        index += number[0].length;
        continue;
      }

      const name = rest.match(/^[A-Za-z_][A-Za-z0-9_]*/);
      if (name) {
        const word = name[0];
        tokens.push({ text: word, className: keywordClasses.get(word) || "n" });
        index += word.length;
        continue;
      }

      const operator = rest.match(/^(==|!=|<=|>=|&&|\|\||::|->|\+\+|--|[-+*/%=<>!&|^~]+)/);
      if (operator) {
        tokens.push({ text: operator[0], className: "o" });
        index += operator[0].length;
        continue;
      }

      tokens.push({ text: line[index], className: "p" });
      index += 1;
    }

    return tokens;
  }

  keywordClasses(language) {
    const keywords = new Map();
    const add = (words, className) => words.forEach((word) => keywords.set(word, className));
    if (["python", "py", "python3"].includes(language)) {
      add(["False", "None", "True"], "kc");
      add(["and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"], "k");
      add(["print", "len", "range", "str", "int", "float", "list", "dict", "set", "tuple"], "nb");
      return keywords;
    }
    if (["cpp", "c++", "c", "java", "js", "javascript", "nodejs"].includes(language)) {
      add(["auto", "bool", "break", "case", "catch", "char", "class", "const", "continue", "default", "do", "double", "else", "enum", "false", "float", "for", "if", "int", "long", "new", "private", "protected", "public", "return", "short", "static", "struct", "switch", "this", "throw", "true", "try", "void", "while"], "k");
      add(["include", "import", "package"], "kn");
      add(["std", "System", "String", "Scanner"], "nc");
      return keywords;
    }
    if (language === "octave") {
      add(["break", "case", "catch", "continue", "else", "elseif", "end", "for", "function", "if", "otherwise", "return", "switch", "try", "while"], "k");
    }
    return keywords;
  }

  commentMatch(rest, language) {
    if (["python", "py", "python3", "octave"].includes(language) && rest.startsWith("#")) {
      return rest;
    }
    if (rest.startsWith("//")) {
      return rest;
    }
    return "";
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
    const endpoint = this.config.endpoint;
    if (!endpoint) {
      this.showError("No execution endpoint is configured.");
      return;
    }

    const source = this.currentSource();
    const executionSource = this.executionSource(source);
    const languageId = this.config.jobeLanguage || this.config.language || "python3";
    const payload = {
      run_spec: {
        language_id: languageId,
        sourcecode: executionSource,
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
      const fileList = await this.uploadRuntimeFiles();
      if (fileList.length > 0) {
        payload.run_spec.file_list = fileList;
      }
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

  canShowTutor() {
    return Boolean(this.config.showTutor) && Boolean(this.tutorLanguage());
  }

  tutorLanguage() {
    const candidates = [this.config.jobeLanguage, this.config.language]
      .filter(Boolean)
      .map((language) => String(language).toLowerCase());
    for (const language of candidates) {
      if (["python", "python3", "py"].includes(language)) {
        return "3";
      }
      if (["cpp", "c++"].includes(language)) {
        return "cpp";
      }
      if (language === "c") {
        return "c";
      }
      if (language === "java") {
        return "java";
      }
      if (["javascript", "js", "node", "nodejs"].includes(language)) {
        return "js";
      }
    }
    return "";
  }

  tutorLanguageLabel() {
    const tutorLanguage = this.tutorLanguage();
    const labels = {
      "3": "Python",
      "c": "C",
      "cpp": "C++",
      "java": "Java",
      "js": "JavaScript",
    };
    return labels[tutorLanguage] || "Python";
  }

  openTutor() {
    const tutorLanguage = this.tutorLanguage();
    if (!tutorLanguage) {
      return;
    }
    const source = this.executionSource(this.currentSource());
    const url = `https://pythontutor.com/visualize.html#code=${encodeURIComponent(source)}&curInstr=0&mode=display&py=${encodeURIComponent(tutorLanguage)}`;
    window.open(url, "_blank", "noopener");
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

  runtimeFiles() {
    return this.attachedFileConfigs().map((file) => {
      const content = file.is_text
        ? this.textFileContent(file)
        : this.base64FromDataUrl(file.data_url || "");
      const runtimeFile = {
        id: this.fileIdentifier(file.filename, content),
        filename: file.filename,
        mime_type: file.mime_type || "text/plain",
      };
      if (file.is_text) {
        runtimeFile.encoding = "text";
        runtimeFile.content = content;
      } else {
        runtimeFile.encoding = "base64";
        runtimeFile.content = content;
      }
      return runtimeFile;
    });
  }

  textFileContent(file) {
    const editor = this.fileEditors.get(file.filename);
    return editor ? editor.value : file.content || "";
  }

  async uploadRuntimeFiles() {
    const files = this.runtimeFiles();
    if (files.length === 0) {
      return [];
    }
    const endpoint = this.fileUploadEndpoint();
    if (!endpoint) {
      throw new Error("No execution file endpoint is configured.");
    }
    const fileList = [];
    for (const file of files) {
      await this.uploadRuntimeFile(endpoint, file);
      fileList.push([file.id, file.filename]);
    }
    return fileList;
  }

  async uploadRuntimeFile(endpoint, file) {
    const base64Content = file.encoding === "base64" ? file.content : this.base64EncodeText(file.content);
    const response = await fetch(`${endpoint}${file.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
      },
      body: JSON.stringify({ file_contents: base64Content }),
    });
    if (!response.ok) {
      throw new Error(`Execution service could not upload ${file.filename}.`);
    }
  }

  fileUploadEndpoint() {
    if (this.config.filesEndpoint) {
      return this.config.filesEndpoint.endsWith("/") ? this.config.filesEndpoint : `${this.config.filesEndpoint}/`;
    }
    if (!this.config.endpoint) {
      return "";
    }
    return this.config.endpoint.replace(/runs\/?$/, "files/");
  }

  fileIdentifier(filename, content) {
    const hashInput = `${filename}\u0000${content}`;
    let hash = 2166136261;
    for (let index = 0; index < hashInput.length; index += 1) {
      hash ^= hashInput.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return `tbfile${(hash >>> 0).toString(36)}${content.length.toString(36)}`;
  }

  base64EncodeText(value) {
    const bytes = new TextEncoder().encode(value);
    let binary = "";
    for (const byte of bytes) {
      binary += String.fromCharCode(byte);
    }
    return btoa(binary);
  }

  base64FromDataUrl(value) {
    const marker = ";base64,";
    const index = value.indexOf(marker);
    if (index === -1) {
      return value;
    }
    return value.slice(index + marker.length);
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
