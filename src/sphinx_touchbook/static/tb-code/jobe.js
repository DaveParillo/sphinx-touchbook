import { fetchWithTimeout, withAbort } from "./transport.js";

/** JOBE protocol, file uploads, discovery caching, and response interpretation. */
export class JobeRunner {
  static languagesByEndpoint = new Map();
  static languagePreloadsByEndpoint = new Map();

  constructor(config) {
    this.config = config;
  }

  preload() {
    this.preloadSupportedLanguages();
  }

  async run(request, { signal, onStatus }) {
    if (!this.config.endpoint) throw new Error("No execution endpoint is configured.");
    const language = this.config.jobeLanguage || this.config.language || "python3";
    onStatus("Checking language support...");
    const supported = await withAbort(this.fetchSupportedLanguages(), signal);
    if (supported && !supported.has(language)) {
      throw new Error(`The execution service does not currently report support for ${language}.`);
    }
    onStatus("Running...");
    const runSpec = {
      language_id: language,
      sourcecode: request.source,
      parameters: request.parameters,
    };
    if (Object.hasOwn(request, "input")) runSpec.input = request.input;
    const files = await this.uploadRuntimeFiles(request.files, signal);
    if (files.length) runSpec.file_list = files;
    const result = await fetchWithTimeout(this.config.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8", "Accept": "application/json" },
      body: JSON.stringify({ run_spec: runSpec }),
    }, 30000, signal, async (response) => {
      if (!response.ok) throw new Error(`Execution service returned ${response.status}.`);
      return response.json();
    });
    return interpretJobeResult(result);
  }

  async uploadRuntimeFiles(files = [], signal) {
    if (!files.length) return [];
    const endpoint = this.config.filesEndpoint
      ? `${this.config.filesEndpoint.replace(/\/$/, "")}/`
      : (this.config.endpoint || "").replace(/runs\/?$/, "files/");
    if (!endpoint) throw new Error("No execution file endpoint is configured.");
    const result = [];
    for (const file of files) {
      const content = file.encoding === "base64"
        ? this.base64FromDataUrl(file.content) : file.content;
      const id = this.fileIdentifier(file.filename, content);
      const response = await fetchWithTimeout(`${endpoint}${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json; charset=utf-8", "Accept": "application/json" },
        body: JSON.stringify({ file_contents: file.encoding === "base64"
          ? content : this.base64EncodeText(content) }),
      }, 30000, signal);
      if (!response.ok) throw new Error(`Execution service could not upload ${file.filename}.`);
      result.push([id, file.filename]);
    }
    return result;
  }

  fetchWithTimeout(...args) {
    return fetchWithTimeout(...args);
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


  async fetchSupportedLanguages() {
    if (this.config.validateLanguage === false || !this.config.languagesEndpoint) {
      return null;
    }
    if (JobeRunner.languagesByEndpoint.has(this.config.languagesEndpoint)) {
      return JobeRunner.languagesByEndpoint.get(this.config.languagesEndpoint);
    }
    if (JobeRunner.languagePreloadsByEndpoint.has(this.config.languagesEndpoint)) {
      return JobeRunner.languagePreloadsByEndpoint.get(this.config.languagesEndpoint);
    }
    return this.loadSupportedLanguages(2500);
  }


  preloadSupportedLanguages() {
    if (this.config.validateLanguage === false || !this.config.languagesEndpoint) {
      return;
    }
    if (JobeRunner.languagesByEndpoint.has(this.config.languagesEndpoint)) {
      return;
    }
    if (JobeRunner.languagePreloadsByEndpoint.has(this.config.languagesEndpoint)) {
      return;
    }

    const preload = this.loadSupportedLanguages(15000).finally(() => {
      JobeRunner.languagePreloadsByEndpoint.delete(this.config.languagesEndpoint);
    });
    JobeRunner.languagePreloadsByEndpoint.set(this.config.languagesEndpoint, preload);
  }


  async loadSupportedLanguages(timeoutMs) {
    try {
      const payload = await this.fetchWithTimeout(
        this.config.languagesEndpoint,
        { headers: { "Accept": "application/json" } },
        timeoutMs,
        undefined,
        async (response) => response.ok ? response.json() : null,
      );
      if (payload === null) {
        return null;
      }
      const languageIds = Array.isArray(payload)
        ? payload.map((entry) => Array.isArray(entry) ? entry[0] : entry)
        : [];
      const languages = new Set(languageIds.filter(Boolean));
      JobeRunner.languagesByEndpoint.set(this.config.languagesEndpoint, languages);
      return languages;
    } catch (error) {
      return null;
    }
  }

}

export function interpretJobeResult(result) {
  return {
    kind: "text",
    text: [result.stdout, result.stderr, result.cmpinfo].filter(Boolean).join("\n") || "(no output)",
    status: result.outcome === 15 ? "Run complete." : `Run finished with outcome ${result.outcome}.`,
  };
}
