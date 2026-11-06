export function renderText(container, result) {
  const listing = document.createElement("pre");
  listing.className = "tb-code__text-output";
  listing.textContent = result.text || "(no output)";
  container.append(listing);
}
