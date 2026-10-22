import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { change, click, keydown, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-deck.js");
  await loadComponentScript("tb-group.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
  window.history.replaceState({}, "", window.location.pathname);
});

function createDeck({ count = 3, id = "example", config = undefined, captions = [] } = {}) {
  const element = document.createElement("tb-deck");
  element.id = id;
  element.setAttribute("role", "group");
  element.setAttribute("aria-label", "Card walkthrough");
  const cards = Array.from({ length: count }, (_, index) => ({
    id: `${id}-card-${index}`, caption: captions[index] ?? `Step ${index + 1}`, objects: []
  }));
  const controls = [["first", "First card", "chevron-double-left"],
    ["previous", "Previous card", "chevron-left"], ["next", "Next card", "chevron-right"],
    ["last", "Last card", "chevron-double-right"]];
  element.innerHTML = `<div class="tb-deck__controls" hidden>
    <p id="${id}-card-caption" class="tb-deck__card-caption" hidden></p>
    <div class="tb-deck__navigation">
    ${controls.map(([action, label, icon]) => `<button type="button" data-action="${action}"
      aria-label="${label}" title="${label}"><svg class="bi bi-${icon}" aria-hidden="true" focusable="false"></svg></button>`).join("")}
    <select class="tb-deck__selector" aria-label="Choose card" hidden></select>
    <p class="tb-deck__status" role="status" aria-live="polite" aria-atomic="true"></p>
    </div>
  </div>
  <div class="tb-deck__cards">${cards.map((card, index) =>
    `<tb-card id="${card.id}" role="group" aria-labelledby="${card.id}-caption"><p id="${card.id}-caption" class="tb-card__caption"></p><tb-array id="${id}-array-${index}">
    <p>Complete array ${index}</p></tb-array><tb-pointer id="${id}-pointer-${index}">Pointer ${index}</tb-pointer></tb-card>`
  ).join("")}</div>
  <script type="application/json">${config === undefined ? JSON.stringify({ version: 1, cards }) : config}</script>`;
  element.querySelectorAll(".tb-card__caption").forEach((heading, index) => {
    heading.textContent = `Card ${index + 1}: ${cards[index].caption}`;
  });
  return element;
}

function appendDeck(options) {
  const element = createDeck(options);
  document.body.append(element);
  return element;
}

function button(element, action) { return element.querySelector(`button[data-action="${action}"]`); }
function visibleCards(element) { return Array.from(element.querySelectorAll("tb-card")).filter((card) => !card.hidden); }


describe("tb-deck manual navigation", () => {
  it("provides a native card selector with concise captions and full accessible names", () => {
    const captions = ["A".repeat(24), "B".repeat(25), "🦉".repeat(25),
      '<img src=x onerror="alert(1)">', "", "  Words\n   with   spacing  "];
    const element = appendDeck({ count: captions.length, captions });
    const select = element.querySelector("select");
    expect(select.getAttribute("aria-label")).toBe("Choose card");
    expect(select.hasAttribute("role")).toBe(false);
    expect(select.tabIndex).toBe(0);
    expect(select.hidden).toBe(false);
    expect(select.value).toBe("0");
    expect(select.options).toHaveLength(6);
    expect(select.options[0].textContent).toBe(`1 of 6: ${"A".repeat(24)}`);
    expect(select.options[1].textContent).toBe(`2 of 6: ${"B".repeat(23)}…`);
    expect(select.options[2].textContent).toBe(`3 of 6: ${"🦉".repeat(23)}…`);
    expect(select.options[3].getAttribute("aria-label")).toBe(`4 of 6: ${captions[3]}`);
    expect(select.options[3].childElementCount).toBe(0);
    expect(select.options[4].textContent).toBe("5 of 6");
    expect(select.options[5].textContent).toBe("6 of 6: Words with spacing");
    expect(select.options[1].getAttribute("aria-label")).toBe(`2 of 6: ${captions[1]}`);
    expect(select.options[1].title).toBe(`2 of 6: ${captions[1]}`);
    expect(select.title).toBe(`1 of 6: ${captions[0]}`);
  });

  it("jumps directly to any selected card while keeping focus and avoiding duplicate announcements", () => {
    const element = appendDeck({ count: 8 });
    const original = Array.from(element.querySelectorAll("tb-card"));
    const select = element.querySelector("select");
    select.focus();
    select.value = "4";
    change(select);
    expect(visibleCards(element)).toEqual([original[4]]);
    expect(element.dataset.card).toBe("5");
    expect(element.querySelector(".tb-deck__card-caption").textContent).toBe("Step 5");
    expect(button(element, "previous").disabled).toBe(false);
    expect(button(element, "next").disabled).toBe(false);
    expect(document.activeElement).toBe(select);
    expect(select.title).toBe("5 of 8: Step 5");
    expect(element.querySelector(".tb-deck__status").textContent).toBe("");
    select.value = "7";
    change(select);
    expect(visibleCards(element)).toEqual([original[7]]);
    expect(button(element, "next").disabled).toBe(true);
    expect(button(element, "last").disabled).toBe(true);
    expect(document.activeElement).toBe(select);
    click(button(element, "first"));
    expect(select.value).toBe("0");
    expect(element.querySelector(".tb-deck__status").textContent).toBe("Card 1 of 8: Step 1");
  });

  it("ignores a selector change with no selected option", () => {
    const element = appendDeck();
    click(button(element, "next"));
    const select = element.querySelector("select");
    select.selectedIndex = -1;
    change(select);
    expect(element.dataset.card).toBe("2");
  });

  it("names the carousel and its slides, following the visible caption on navigation", () => {
    const element = createDeck();
    const heading = document.createElement("p");
    heading.id = "example-caption";
    heading.className = "tb-deck__caption";
    heading.textContent = 'Inspect <values> & "labels"';
    element.prepend(heading);
    element.setAttribute("aria-labelledby", heading.id);
    element.removeAttribute("aria-label");
    document.body.append(element);
    const cards = Array.from(element.querySelectorAll("tb-card"));
    const caption = element.querySelector(".tb-deck__card-caption");
    const expectCurrentName = (index) => {
      expect(cards[index].getAttribute("aria-labelledby")).toBe(caption.id);
      expect(document.getElementById(caption.id).textContent).toBe(`Step ${index + 1}`);
      expect(caption.hidden).toBe(false);
      expect(cards[index].hasAttribute("aria-label")).toBe(false);
      cards.forEach((card, number) => {
        expect(card.getAttribute("role")).toBe("group");
        expect(card.getAttribute("aria-roledescription")).toBe("slide");
        if (number !== index) {
          expect(card.hidden).toBe(true);
          expect(card.hasAttribute("aria-labelledby")).toBe(false);
          expect(card.getAttribute("aria-label")).toBe(`Step ${number + 1}`);
        }
      });
    };
    expect(element.getAttribute("role")).toBe("group");
    expect(element.getAttribute("aria-roledescription")).toBe("carousel");
    expect(document.getElementById(element.getAttribute("aria-labelledby"))).toBe(heading);
    expectCurrentName(0);
    click(button(element, "next"));
    expectCurrentName(1);
    click(button(element, "first"));
    expectCurrentName(0);
  });

  it("names uncaptioned slides by position and count without stale label references", () => {
    const element = createDeck();
    const script = element.querySelector('script[type="application/json"]');
    const config = JSON.parse(script.textContent);
    config.cards[0].caption = "";
    config.cards[2].caption = "";
    script.textContent = JSON.stringify(config);
    document.body.append(element);
    const cards = element.querySelectorAll("tb-card");
    expect(element.getAttribute("aria-label")).toBe("Card walkthrough");
    expect(cards[0].getAttribute("aria-label")).toBe("1 of 3");
    expect(cards[0].hasAttribute("aria-labelledby")).toBe(false);
    expect(cards[2].getAttribute("aria-label")).toBe("3 of 3");
    click(button(element, "next"));
    expect(cards[1].getAttribute("aria-labelledby")).toBe("example-card-caption");
    click(button(element, "last"));
    expect(cards[1].getAttribute("aria-label")).toBe("Step 2");
    expect(cards[1].hasAttribute("aria-labelledby")).toBe(false);
    expect(cards[2].getAttribute("aria-label")).toBe("3 of 3");
    expect(cards[2].hasAttribute("aria-labelledby")).toBe(false);
    expect(element.querySelector(".tb-deck__card-caption").hidden).toBe(true);
  });

  it("shows the first complete card and enables only forward navigation", () => {
    const element = appendDeck();
    expect(customElements.get("tb-deck")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(visibleCards(element).map((card) => card.id)).toEqual(["example-card-0"]);
    expect(button(element, "first").disabled).toBe(true);
    expect(button(element, "previous").disabled).toBe(true);
    expect(button(element, "next").disabled).toBe(false);
    expect(button(element, "last").disabled).toBe(false);
    expect(element.querySelector(".tb-deck__controls").hidden).toBe(false);
    expect(element.querySelector(".tb-deck__status").textContent).toBe("Card 1 of 3: Step 1");
    expect(Array.from(element.querySelectorAll(".tb-card__caption")).every((heading) => heading.hidden)).toBe(true);
  });

  it("keeps controls above changing card content with one current card caption", () => {
    const element = appendDeck();
    const controls = element.querySelector(".tb-deck__controls");
    const cards = element.querySelector(".tb-deck__cards");
    const content = element.querySelectorAll("tb-array")[1];
    content.append(document.createElement("pre"));
    content.lastElementChild.textContent = "A larger card\n".repeat(30);
    click(button(element, "next").querySelector("svg"));
    expect(controls.nextElementSibling).toBe(cards);
    expect(controls.querySelector(".tb-deck__status").textContent).toBe("Card 2 of 3: Step 2");
    expect(controls.querySelector("select").value).toBe("1");
    const caption = controls.querySelector(".tb-deck__card-caption");
    const navigation = controls.querySelector(".tb-deck__navigation");
    expect(caption.textContent).toBe("Step 2");
    expect(caption.hidden).toBe(false);
    expect(caption.nextElementSibling).toBe(navigation);
    expect(navigation.lastElementChild.firstChild.textContent).toBe("Card 2 of 3");
    expect(navigation.lastElementChild.querySelector(".tb-deck__status-caption").textContent).toBe(": Step 2");
    expect(visibleCards(element)[0].querySelector(".tb-card__caption").hidden).toBe(true);
    expect(content.querySelector("p").hidden).toBe(false);
  });

  it("clears the separate caption when the next card has no caption", () => {
    const element = createDeck();
    const config = element.querySelector('script[type="application/json"]');
    const data = JSON.parse(config.textContent);
    data.cards[1].caption = "";
    config.textContent = JSON.stringify(data);
    document.body.append(element);
    click(button(element, "next"));
    const caption = element.querySelector(".tb-deck__card-caption");
    expect(caption.hidden).toBe(true);
    expect(caption.textContent).toBe("");
    expect(element.querySelector(".tb-deck__status").textContent).toBe("Card 2 of 3");
  });

  it("implements all four navigation actions without replaying or cloning cards", () => {
    const element = appendDeck({ count: 4 });
    const original = Array.from(element.querySelectorAll("tb-card"));
    click(button(element, "next"));
    expect(visibleCards(element)).toEqual([original[1]]);
    click(button(element, "last"));
    expect(visibleCards(element)).toEqual([original[3]]);
    expect(button(element, "next").disabled).toBe(true);
    expect(button(element, "last").disabled).toBe(true);
    click(button(element, "previous"));
    expect(visibleCards(element)).toEqual([original[2]]);
    click(button(element, "first"));
    expect(visibleCards(element)).toEqual([original[0]]);
    expect(element.querySelectorAll("tb-array")).toHaveLength(4);
    const ids = Array.from(element.querySelectorAll("[id]")).map((item) => item.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("keeps keyboard focus on an available control at an endpoint", () => {
    const element = appendDeck();
    const last = button(element, "last");
    last.focus();
    click(last);
    expect(document.activeElement).toBe(button(element, "previous"));
    const first = button(element, "first");
    first.focus();
    click(first);
    expect(document.activeElement).toBe(button(element, "next"));
    expect(element.querySelector(".tb-deck__status").hasAttribute("tabindex")).toBe(false);
  });

  it("handles a single card with all navigation disabled", () => {
    const element = appendDeck({ count: 1 });
    expect(visibleCards(element)).toHaveLength(1);
    expect(element.querySelector("select").hidden).toBe(true);
    element.querySelectorAll("button").forEach((control) => expect(control.disabled).toBe(true));
    expect(element.querySelector(".tb-deck__status").textContent).toBe("Card 1 of 1: Step 1");
    expect(element.getAttribute("aria-roledescription")).toBe("carousel");
    expect(visibleCards(element)[0].getAttribute("aria-roledescription")).toBe("slide");
  });

  it.each(["not JSON", "null", '{"version":2,"cards":[]}', '{"version":1,"cards":[]}'])(
    "retains all static cards when configuration is invalid: %s", (config) => {
      const element = appendDeck({ config });
      expect(visibleCards(element)).toHaveLength(3);
      expect(element.dataset.enhanced).toBeUndefined();
      expect(element.hasAttribute("aria-roledescription")).toBe(false);
      element.querySelectorAll("tb-card").forEach((card) => {
        expect(card.hasAttribute("aria-roledescription")).toBe(false);
        expect(document.getElementById(card.getAttribute("aria-labelledby")).hidden).toBe(false);
      });
      expect(element.querySelector(".tb-deck__controls").hidden).toBe(true);
      expect(element.querySelector("select").hidden).toBe(true);
      expect(element.querySelector("select").options).toHaveLength(0);
      expect(Array.from(element.querySelectorAll(".tb-card__caption")).every((heading) => !heading.hidden)).toBe(true);
    });

  it("retains static cards if card identifiers do not match or controls are missing", () => {
    const element = createDeck();
    element.querySelector("tb-card").id = "different-id";
    document.body.append(element);
    expect(visibleCards(element)).toHaveLength(3);
    const missing = createDeck({ id: "missing" });
    missing.querySelector(".tb-deck__controls").remove();
    document.body.append(missing);
    expect(visibleCards(missing)).toHaveLength(3);
  });

  it("retains static cards if the native selector is missing", () => {
    const element = createDeck();
    element.querySelector("select").remove();
    document.body.append(element);
    expect(visibleCards(element)).toHaveLength(3);
    expect(element.dataset.enhanced).toBeUndefined();
  });

  it("retains named static groups when the shared caption has no reference target", () => {
    const element = createDeck();
    element.querySelector(".tb-deck__card-caption").removeAttribute("id");
    document.body.append(element);
    expect(element.dataset.enhanced).toBeUndefined();
    expect(element.hasAttribute("aria-roledescription")).toBe(false);
    expect(visibleCards(element)).toHaveLength(3);
    element.querySelectorAll("tb-card").forEach((card) => {
      expect(card.hasAttribute("aria-roledescription")).toBe(false);
      expect(document.getElementById(card.getAttribute("aria-labelledby")).hidden).toBe(false);
    });
  });

  it("keeps decks independent even when semantic objects have the same names", () => {
    const first = appendDeck();
    const second = appendDeck({ id: "second" });
    click(button(first, "last"));
    expect(first.dataset.card).toBe("3");
    expect(second.dataset.card).toBe("1");
    expect(visibleCards(first)[0].getAttribute("aria-labelledby")).toBe("example-card-caption");
    expect(visibleCards(second)[0].getAttribute("aria-labelledby")).toBe("second-card-caption");
  });
});


describe("tb-deck document targets and lifecycle", () => {
  it("follows links to cards in another deck while preserving the departure card", () => {
    const first = appendDeck();
    const second = appendDeck({ id: "second" });
    const link = document.createElement("a");
    link.href = "#second-card-2";
    first.querySelector("tb-card").append(link);

    click(link);

    expect(visibleCards(first)[0].id).toBe("example-card-0");
    expect(visibleCards(second)[0].id).toBe("second-card-2");
    expect(second.querySelector(".tb-deck__status").textContent).toBe("Card 3 of 3: Step 3");
    expect(second.querySelector("select").value).toBe("2");
    expect(first.querySelector("select").value).toBe("0");
    expect(button(second, "next").disabled).toBe(true);
    expect(button(second, "previous").disabled).toBe(false);
  });

  it("initializes to the card containing the current document target", () => {
    window.history.replaceState({}, "", "#example-pointer-2");
    const element = appendDeck();
    expect(visibleCards(element)[0].id).toBe("example-card-2");
    expect(element.querySelector("select").value).toBe("2");
  });

  it("reveals inactive card content on hash changes and repeated same-hash links", () => {
    const element = appendDeck();
    window.history.replaceState({}, "", "#example-array-2");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    expect(element.dataset.card).toBe("3");
    expect(element.querySelector("select").value).toBe("2");
    click(button(element, "first"));
    const link = document.createElement("a");
    link.href = "#example-array-2";
    document.body.append(link);
    click(link);
    expect(element.dataset.card).toBe("3");
  });

  it("ignores malformed and unrelated document targets", () => {
    const element = appendDeck();
    element.revealHashTarget("#%invalid");
    element.revealHashTarget("#missing");
    expect(element.dataset.card).toBe("1");
  });

  it("does not duplicate controls or listeners after reconnecting", () => {
    const element = appendDeck();
    click(button(element, "next"));
    element.remove();
    document.body.append(element);
    const show = vi.spyOn(element, "showCard");
    click(button(element, "next"));
    expect(show).toHaveBeenCalledTimes(1);
    expect(element.dataset.card).toBe("3");
    expect(element.querySelectorAll(".tb-deck__controls")).toHaveLength(1);
    expect(element.getAttribute("aria-roledescription")).toBe("carousel");
    expect(visibleCards(element)[0].getAttribute("aria-labelledby")).toBe("example-card-caption");
    const select = element.querySelector("select");
    expect(element.querySelectorAll("select")).toHaveLength(1);
    expect(select.options).toHaveLength(3);
    select.value = "1";
    change(select);
    expect(show).toHaveBeenCalledTimes(2);
    expect(element.dataset.card).toBe("2");
    window.history.replaceState({}, "", "#example-pointer-0");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    expect(element.dataset.card).toBe("1");
  });

  it("preserves access to deck controls inside tb-group panels", () => {
    const group = document.createElement("tb-group");
    group.id = "tabs";
    group.innerHTML = `<div class="tb-group__fallback">
      <tb-tab label="Source"><div class="tb-tab__content">Source text</div></tb-tab>
      <tb-tab label="Rendered"><div class="tb-tab__content"></div></tb-tab>
      </div>`;
    group.querySelectorAll(".tb-tab__content")[1].append(createDeck());
    document.body.append(group);
    const tabs = group.ownTabs();
    click(tabs[1]);
    keydown(tabs[1], "Tab");
    expect(document.activeElement.getAttribute("aria-label")).toBe("Next card");
    click(document.activeElement);
    expect(group.querySelector("tb-deck").dataset.card).toBe("2");
  });
});
