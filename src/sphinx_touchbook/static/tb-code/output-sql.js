export function renderSql(container, result) {
  for (const [index, data] of result.results.entries()) {
    const table = document.createElement("table");
    table.className = "tb-code__sql-table";
    const caption = table.createCaption();
    caption.textContent = `Result ${index + 1}: ${data.values.length} row${data.values.length === 1 ? "" : "s"}`;
    const headers = table.createTHead().insertRow();
    for (const name of data.columns) {
      const header = document.createElement("th");
      header.scope = "col";
      header.textContent = name;
      headers.append(header);
    }
    const body = table.createTBody();
    for (const values of data.values) {
      const row = body.insertRow();
      for (const value of values) {
        const cell = row.insertCell();
        cell.textContent = value === null ? "NULL" : String(value);
        if (value === null) {
          cell.className = "tb-code__sql-null";
          cell.title = "SQL NULL (missing value)";
        }
      }
    }
    if (!data.values.length) {
      const cell = body.insertRow().insertCell();
      cell.colSpan = data.columns.length;
      cell.textContent = "No rows returned.";
    }
    container.append(table);
  }
  for (const message of result.messages || []) {
    const paragraph = document.createElement("p");
    paragraph.textContent = message;
    container.append(paragraph);
  }
}
