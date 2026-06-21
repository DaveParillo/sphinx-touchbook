import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

export async function loadComponentScript(scriptName) {
  const source = await readFile(resolve("src/sphinx_touchbook/static", scriptName), "utf8");
  window.eval(source);
}

export function click(element) {
  element.dispatchEvent(new MouseEvent("click", { bubbles: true }));
}

export function keydown(element, key) {
  element.dispatchEvent(new KeyboardEvent("keydown", { bubbles: true, cancelable: true, key }));
}

export function input(element) {
  element.dispatchEvent(new Event("input", { bubbles: true }));
}

export function change(element) {
  element.dispatchEvent(new Event("change", { bubbles: true }));
}
