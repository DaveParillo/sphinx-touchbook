/** Normalize execution arguments without depending on the component. */

export function cleanArgumentList(value) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map((item) => String(item)).filter((item) => item.length > 0);
}

export function cleanParameters(parameters) {
  const cleaned = {};
  for (const [key, value] of Object.entries(parameters)) {
    const cleanedValue = cleanArgumentList(value);
    if (cleanedValue.length > 0) {
      cleaned[key] = cleanedValue;
    }
  }
  return cleaned;
}

export function splitArguments(value) {
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
