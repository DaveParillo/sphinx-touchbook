import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-order.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
});

function appendOrder() {
  const element = document.createElement("tb-order");
  element.id = "order-example";
  element.innerHTML = `
    <ol class="tb-order__list" aria-label="Items to order">
      <li class="tb-order__item" data-order="0">
        <div class="tb-order__content">Wake up</div>
        <div class="tb-order__controls">
          <button type="button" class="tb-order__move tb-order__move-up">↑</button>
          <button type="button" class="tb-order__move tb-order__move-down">↓</button>
        </div>
      </li>
      <li class="tb-order__item" data-order="1">
        <div class="tb-order__content">Eat breakfast</div>
        <div class="tb-order__controls">
          <button type="button" class="tb-order__move tb-order__move-up">↑</button>
          <button type="button" class="tb-order__move tb-order__move-down">↓</button>
        </div>
      </li>
      <li class="tb-order__item" data-order="2">
        <div class="tb-order__content">Go to class</div>
        <div class="tb-order__controls">
          <button type="button" class="tb-order__move tb-order__move-up">↑</button>
          <button type="button" class="tb-order__move tb-order__move-down">↓</button>
        </div>
      </li>
    </ol>
    <div class="tb-order__actions">
      <button type="button" class="tb-order__check">Check order</button>
      <p class="tb-order__status" role="status" aria-live="polite"></p>
    </div>
  `;
  document.body.appendChild(element);
  return element;
}

function orderValues(element) {
  return Array.from(element.querySelectorAll(".tb-order__item")).map((item) => item.dataset.order);
}

describe("tb-order Web Component", () => {
  it("shuffles items on initialization", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendOrder();

    expect(customElements.get("tb-order")).toBeTypeOf("function");
    expect(orderValues(element)).toEqual(["1", "2", "0"]);
    randomMock.mockRestore();
  });

  it("moves items with native buttons and updates disabled states", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendOrder();
    randomMock.mockRestore();

    expect(orderValues(element)).toEqual(["1", "0", "2"]);
    const secondItem = element.querySelectorAll(".tb-order__item")[1];
    click(secondItem.querySelector(".tb-order__move-up"));

    expect(orderValues(element)).toEqual(["0", "1", "2"]);
    expect(element.querySelector(".tb-order__item .tb-order__move-up").disabled).toBe(true);
  });

  it("reports correct order", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0.99);
    const element = appendOrder();
    randomMock.mockRestore();

    const secondItem = element.querySelectorAll(".tb-order__item")[1];
    click(secondItem.querySelector(".tb-order__move-up"));
    click(element.querySelector(".tb-order__check"));

    expect(element.querySelector(".tb-order__status").textContent).toBe("Correct.");
    expect(element.querySelector(".tb-order__item").classList.contains("tb-order__item--correct")).toBe(true);
  });

  it("reports incorrect order", () => {
    const randomMock = vi.spyOn(Math, "random").mockReturnValue(0);
    const element = appendOrder();
    randomMock.mockRestore();

    click(element.querySelector(".tb-order__check"));

    expect(element.querySelector(".tb-order__status").textContent).toBe("Not quite. Try again!");
    expect(element.querySelector(".tb-order__item").classList.contains("tb-order__item--incorrect")).toBe(true);
  });
});
