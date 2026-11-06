/* The library and WASM are loaded only when a SQL example is run. */
importScripts("vendor/sql-wasm.js");
self.onmessage = async ({ data }) => {
  try {
    const [SQL, { executeSql }] = await Promise.all([
      initSqlJs({ locateFile: (name) => new URL(`vendor/${name}`, self.location.href).href }),
      import("./sqlite-engine.js"),
    ]);
    self.postMessage({ result: executeSql(SQL, data) });
  } catch (error) {
    self.postMessage({ error: String(error.message || error) });
  } finally {
    self.close();
  }
};
