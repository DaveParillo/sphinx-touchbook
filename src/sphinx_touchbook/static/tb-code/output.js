import { renderText } from "./output-text.js";
import { renderSql } from "./output-sql.js";
import { renderHtml } from "./output-html.js";

/** All result data is inserted as text, except the explicitly sandboxed preview. */
export function renderOutput(container, result, context) {
  container.replaceChildren();
  switch (result.kind) {
    case "text": return renderText(container, result);
    case "sql": return renderSql(container, result);
    case "html": return renderHtml(container, result, context);
    default: throw new Error(`Unsupported result type: ${result.kind}.`);
  }
}
