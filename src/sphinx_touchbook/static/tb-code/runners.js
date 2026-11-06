import { JobeRunner } from "./jobe.js";
import { BrowserRunner } from "./browser.js";
import { SqliteRunner } from "./sqlite.js";

export function createRunner(config) {
  if (!config.runner || config.runner === "jobe") return new JobeRunner(config);
  if (config.runner !== "browser") throw new Error(`Unknown execution runner: ${config.runner}.`);
  if (["sql", "sqlite", "sqlite3"].includes(String(config.language).toLowerCase())) {
    return new SqliteRunner();
  }
  return new BrowserRunner(config);
}
