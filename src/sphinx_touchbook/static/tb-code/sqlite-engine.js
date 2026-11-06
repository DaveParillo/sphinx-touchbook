import {
  MAX_DATABASE_BYTES, MAX_OUTPUT_BYTES, MAX_STATEMENTS, MAX_ROWS, MAX_SQLITE_HEAP_BYTES,
} from "./limits.js";

function seedDatabase(files) {
  if (!files?.length) return undefined;
  const content = files[0].content;
  const base64 = content.includes(";base64,") ? content.split(";base64,")[1] : content;
  if (base64.length > Math.ceil(MAX_DATABASE_BYTES / 3) * 4) {
    throw new Error("The SQLite seed database exceeds 16 MiB.");
  }
  const bytes = Uint8Array.from(atob(base64), (character) => character.charCodeAt(0));
  const signature = new TextDecoder().decode(bytes.subarray(0, 16));
  if (signature !== "SQLite format 3\u0000") {
    throw new Error("The attached file is not an SQLite database.");
  }
  return bytes;
}

function cellValue(value) {
  if (typeof value === "bigint") {
    return value >= BigInt(Number.MIN_SAFE_INTEGER) && value <= BigInt(Number.MAX_SAFE_INTEGER)
      ? Number(value) : String(value);
  }
  if (value instanceof Uint8Array) {
    return `BLOB (${value.length} bytes)`;
  }
  return value;
}

/** Execute through SQLite's statement iterator, never by splitting on ';'. */
export function executeSql(SQL, request) {
  const db = new SQL.Database(seedDatabase(request.files));
  const results = [];
  let rowCount = 0;
  let byteCount = 0;
  let statements = 0;
  let truncated = false;
  let error;
  const encoder = new TextEncoder();
  try {
    // Each run has its own worker/library instance. SQLite's hard heap limit
    // bounds engine allocations and cannot be raised through the SQL pragma.
    db.run(`PRAGMA hard_heap_limit=${MAX_SQLITE_HEAP_BYTES}`);
    for (const statement of db.iterateStatements(request.source)) {
      if (statements >= MAX_STATEMENTS) {
        truncated = true;
        break;
      }
      statements += 1;
      const columns = statement.getColumnNames();
      const values = [];
      byteCount += encoder.encode(JSON.stringify(columns)).length;
      if (byteCount > MAX_OUTPUT_BYTES) {
        truncated = true;
        break;
      }
      while (statement.step()) {
        if (rowCount >= MAX_ROWS) {
          truncated = true;
          break;
        }
        const row = statement.get(null, { useBigInt: true }).map(cellValue);
        byteCount += encoder.encode(JSON.stringify(row)).length;
        if (byteCount > MAX_OUTPUT_BYTES) {
          truncated = true;
          break;
        }
        values.push(row);
        rowCount += 1;
      }
      if (columns.length) results.push({ columns, values });
      if (truncated) break;
    }
  } catch (caught) {
    error = String(caught.message || caught);
  } finally {
    db.close();
  }
  const messages = [];
  if (!results.length && !error) messages.push("SQL statements completed. No result rows.");
  if (truncated) messages.push("Output truncated; remaining statements were not executed.");
  if (error) messages.push(error);
  return { kind: "sql", results, messages,
    status: error ? "Run failed." : (truncated ? "Run complete; output truncated." : "Run complete."),
  };
}
