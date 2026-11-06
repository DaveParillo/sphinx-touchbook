import { cleanArgumentList } from "./arguments.js";

/** Pure link construction for tools opened outside the textbook. */
export function tutorLanguage(config) {
  const aliases = {
    python: "3", python3: "3", py: "3", cpp: "cpp", "c++": "cpp", c: "c",
    java: "java", javascript: "js", js: "js", node: "js", nodejs: "js",
  };
  for (const name of [config.jobeLanguage, config.language]) {
    const language = aliases[String(name || "").toLowerCase()];
    if (language) return language;
  }
  return "";
}

export function tutorLanguageLabel(config) {
  return { "3": "Python", cpp: "C++", c: "C", java: "Java", js: "JavaScript" }[
    tutorLanguage(config)
  ] || "Python";
}

export function tutorUrl(config, source) {
  const language = tutorLanguage(config);
  if (!language) return null;
  return `https://pythontutor.com/visualize.html#code=${encodeURIComponent(source)}&curInstr=0&mode=display&py=${encodeURIComponent(language)}`;
}

export function compilerExplorerUrl(config, source) {
  const profile = config.compilerExplorer;
  if (!profile) return null;
  // CE's single Java source file is example.java. Preserve the source in the
  // textbook; only remove public from top-level types in the transferred copy.
  if (profile.language === "java") {
    source = source.replace(
      /^public[ \t]+(?=(?:(?:abstract|final|sealed|non-sealed|strictfp)[ \t]+)*(?:class|interface|enum|record|@interface)[ \t]+)/gm,
      "",
    );
  }
  const state = { sessions: [{
    id: 1, language: profile.language, source,
    compilers: [{ id: profile.compiler,
      options: profile.options ?? cleanArgumentList(config.parameters?.compileargs).join(" ") }],
  }] };
  const json = JSON.stringify(state).replace(/[\u007f-\uffff]/g, (character) =>
    `\\u${character.charCodeAt(0).toString(16).padStart(4, "0")}`);
  return `https://godbolt.org/clientstate/${encodeURIComponent(btoa(json))}`;
}
