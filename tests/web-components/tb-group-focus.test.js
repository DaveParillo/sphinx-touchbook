import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, keydown, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  for (const script of [
    "tb-group.js",
    "tb-blank.js",
    "tb-choice.js",
    "tb-click.js",
    "tb-code.js",
    "tb-file.js",
    "tb-formula.js",
    "tb-match.js",
    "tb-micro-parsons.js",
    "tb-order.js",
    "tb-parsons.js",
    "tb-reveal.js",
    "tb-video.js",
  ]) {
    await loadComponentScript(script);
  }
});

beforeEach(() => {
  document.body.innerHTML = "";
  vi.restoreAllMocks();
});

const fixtures = [
  {
    name: "tb-blank",
    selector: ".tb-blank__input",
    html: `
      <tb-blank id="blank-example">
        <div class="tb-blank__prompt">
          <p>Capital <input class="tb-blank__input" type="text" data-blank-id="blank1"></p>
        </div>
        <script type="application/json" class="tb-blank__config">
          {"blanks":["blank1"],"answers":{"blank1":{"matches":["Paris"],"hints":[],"feedback":"Correct.","incorrect":"Try again.","regex":false}}}
        </script>
        <div class="tb-blank__actions">
          <button type="button" class="tb-blank__check">Check answer</button>
          <p class="tb-blank__status" role="status" aria-live="polite"></p>
        </div>
      </tb-blank>
    `,
  },
  {
    name: "tb-choice",
    selector: ".tb-choice__input",
    html: `
      <tb-choice id="choice-example" mode="single">
        <div id="choice-example-prompt" class="tb-choice__prompt"><p>Choose one.</p></div>
        <div class="tb-choice__options" role="group" aria-labelledby="choice-example-prompt">
          <div class="tb-choice__option" data-correct="true">
            <label class="tb-choice__label">
              <input class="tb-choice__input" type="radio" name="choice-example-answer" value="0">
              <div class="tb-choice__answer"><p>A</p></div>
            </label>
            <div class="tb-choice__feedback"><p>Correct.</p></div>
          </div>
        </div>
        <div class="tb-choice__actions">
          <button type="button" class="tb-choice__check">Check answer</button>
          <p class="tb-choice__status" role="status" aria-live="polite"></p>
        </div>
      </tb-choice>
    `,
  },
  {
    name: "tb-click",
    selector: ".tb-click__target",
    html: `
      <tb-click id="click-example" hints="false">
        <div class="tb-click__prompt"><p>Click the operator.</p></div>
        <div class="highlight-none notranslate tb-click__source">
          <div class="highlight"><pre>x <button type="button" class="tb-click__target" data-correct="true">&gt;</button> 0</pre></div>
        </div>
        <button type="button" class="tb-click__hint-toggle">Show Hints</button>
        <p class="tb-click__status" role="status" aria-live="polite"></p>
      </tb-click>
    `,
  },
  {
    name: "tb-code",
    selector: "button.tb-code__button:not([hidden])",
    html: `
      <tb-code id="code-example" language="python" editable="true">
        <figure class="tb-code__fallback"><pre><code>print("one")</code></pre></figure>
        <script type="application/json" class="tb-code__config">
          {"language":"python","jobeLanguage":"python3","source":"print(\\"one\\")","endpoint":"https://example.test/runs/","languagesEndpoint":"https://example.test/languages","validateLanguage":false,"stdin":"","parameters":{},"editable":true,"runLabel":"Run","editLabel":"Edit source","hideEditLabel":"Hide source","revisionLabel":"Source version"}
        </script>
      </tb-code>
    `,
  },
  {
    name: "tb-file",
    selector: ".tb-file__button",
    html: `
      <tb-file id="input-file" filename="input.txt">
        <figure class="tb-file__fallback">
          <figcaption class="tb-file__caption">input.txt</figcaption>
          <pre class="tb-file__content"><code>Alice</code></pre>
        </figure>
        <script type="application/json" class="tb-file__config">
          {"filename":"input.txt","content":"Alice","mimeType":"text/plain","isText":true,"editable":true,"editLabel":"Edit","hideEditLabel":"Hide editor"}
        </script>
      </tb-file>
    `,
  },
  {
    name: "tb-formula",
    selector: ".tb-formula__input",
    html: `
      <tb-formula id="formula-example" data-endpoint="https://example.test/jobe/index.php/restapi/runs">
        <div class="tb-formula__prompt">What is <span class="tb-formula__variable" data-variable="x">{{x}}</span>?</div>
        <script type="application/json" class="tb-formula__config">
          {"variables":{"x":{"min":1,"max":1,"integer":true}},"formula":{"language":"javascript","source":"x"},"tolerance":0}
        </script>
        <div class="tb-formula__answer">
          <label class="tb-formula__label">Answer <input class="tb-formula__input" type="text" inputmode="decimal"></label>
        </div>
        <div class="tb-formula__actions">
          <button type="button" class="tb-formula__check">Check answer</button>
          <button type="button" class="tb-formula__new-values">New values</button>
          <p class="tb-formula__status" role="status" aria-live="polite"></p>
        </div>
      </tb-formula>
    `,
  },
  {
    name: "tb-match",
    selector: ".tb-match__select",
    html: `
      <tb-match id="match-example">
        <div class="tb-match__choices">
          <div class="tb-match__choice" data-answer="0">
            <label id="match-example-source-0" class="tb-match__source" for="match-example-select-0">compiler</label>
            <select id="match-example-select-0" class="tb-match__select" data-answer="0" aria-labelledby="match-example-source-0">
              <option value="">Choose a definition</option>
              <option value="0">Translates source.</option>
            </select>
          </div>
        </div>
        <div class="tb-match__actions">
          <button type="button" class="tb-match__check" disabled>Check Me</button>
          <p class="tb-match__status" role="status" aria-live="polite"></p>
        </div>
      </tb-match>
    `,
  },
  {
    name: "tb-micro-parsons",
    selector: ".tb-micro-parsons__token-button",
    html: `
      <tb-micro-parsons id="micro-parsons-example" data-has-distractors="false">
        <div class="tb-micro-parsons__workspace">
          <div class="tb-micro-parsons__row">
            <p class="tb-micro-parsons__row-label">Tokens</p>
            <ol class="tb-micro-parsons__tokens tb-micro-parsons__source" aria-label="Available tokens">
              <li class="tb-micro-parsons__token" data-order="0" data-distractor="false" data-location="source">
                <button type="button" class="tb-micro-parsons__token-button" aria-label="Move int to answer">
                  <code class="tb-micro-parsons__content">int</code>
                </button>
              </li>
            </ol>
          </div>
          <div class="tb-micro-parsons__row">
            <p class="tb-micro-parsons__row-label">Answer</p>
            <ol class="tb-micro-parsons__tokens tb-micro-parsons__target" aria-label="Answer tokens"></ol>
          </div>
        </div>
        <div class="tb-micro-parsons__actions">
          <button type="button" class="tb-micro-parsons__check">Check answer</button>
          <p class="tb-micro-parsons__status" role="status" aria-live="polite"></p>
        </div>
      </tb-micro-parsons>
    `,
  },
  {
    name: "tb-order",
    selector: ".tb-order__move-down",
    html: `
      <tb-order id="order-example">
        <ol class="tb-order__list" aria-label="Items to order">
          <li class="tb-order__item" data-order="0">
            <div class="tb-order__content">Wake up</div>
            <div class="tb-order__controls">
              <button type="button" class="tb-order__move tb-order__move-up">Up</button>
              <button type="button" class="tb-order__move tb-order__move-down">Down</button>
            </div>
          </li>
          <li class="tb-order__item" data-order="1">
            <div class="tb-order__content">Eat breakfast</div>
            <div class="tb-order__controls">
              <button type="button" class="tb-order__move tb-order__move-up">Up</button>
              <button type="button" class="tb-order__move tb-order__move-down">Down</button>
            </div>
          </li>
        </ol>
        <div class="tb-order__actions">
          <button type="button" class="tb-order__check">Check order</button>
          <p class="tb-order__status" role="status" aria-live="polite"></p>
        </div>
      </tb-order>
    `,
  },
  {
    name: "tb-parsons",
    selector: ".tb-parsons__move-down",
    html: `
      <tb-parsons id="parsons-example">
        <ol class="tb-parsons__list" aria-label="Code fragments">
          <li class="tb-parsons__item" data-order="0" data-indent="0" data-current-indent="0" data-distractor="false">
            <pre class="tb-parsons__code"><code>def f():</code></pre>
            ${parsonsControls()}
          </li>
          <li class="tb-parsons__item" data-order="1" data-indent="4" data-current-indent="0" data-distractor="false">
            <pre class="tb-parsons__code"><code>return 1</code></pre>
            ${parsonsControls()}
          </li>
        </ol>
        <div class="tb-parsons__actions">
          <button type="button" class="tb-parsons__check">Check answer</button>
          <p class="tb-parsons__status" role="status" aria-live="polite"></p>
        </div>
      </tb-parsons>
    `,
  },
  {
    name: "tb-reveal",
    selector: ".tb-reveal__button",
    html: `
      <tb-reveal id="inline-reveal" showlabel="Open" hidelabel="Close">
        <details class="tb-reveal__fallback"><summary>Open</summary></details>
        <div class="tb-reveal__content"><p>Hidden answer</p></div>
      </tb-reveal>
    `,
  },
  {
    name: "tb-video",
    selector: ".tb-video__placeholder",
    html: `
      <tb-video id="video-example" source-url="https://www.youtube.com/watch?v=aqz-KE-bpKQ" embed-url="https://www.youtube.com/embed/aqz-KE-bpKQ">
        <figure class="tb-video__fallback">
          <a class="tb-video__placeholder" href="https://www.youtube.com/watch?v=aqz-KE-bpKQ" target="_blank" rel="noopener noreferrer">
            <img class="tb-video__thumbnail" src="https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg" alt="">
            <span class="tb-video__placeholder-label">Open video</span>
          </a>
        </figure>
        <script type="application/json" class="tb-video__config">
          {"sourceUrl":"https://www.youtube.com/watch?v=aqz-KE-bpKQ","embedUrl":"https://www.youtube.com/embed/aqz-KE-bpKQ","provider":"youtube","kind":"iframe","thumbnailUrl":"https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg","window":false,"width":"640","height":"360","playLabel":"Play video","pauseLabel":"Pause video","openLabel":"Open video in new window"}
        </script>
      </tb-video>
    `,
  },
];

function parsonsControls() {
  return `
    <div class="tb-parsons__controls" aria-label="Arrange fragment">
      <button type="button" class="tb-parsons__move tb-parsons__move-up">Up</button>
      <button type="button" class="tb-parsons__move tb-parsons__move-down">Down</button>
      <button type="button" class="tb-parsons__indent tb-parsons__outdent">Outdent</button>
      <button type="button" class="tb-parsons__indent tb-parsons__indent-in">Indent</button>
      <button type="button" class="tb-parsons__toggle" aria-pressed="true" aria-label="Included in solution">
        <span class="tb-parsons__toggle-label">Use</span>
      </button>
    </div>
  `;
}

function appendGroupWithRenderedFixture(fixture) {
  const group = document.createElement("tb-group");
  group.id = `focus-${fixture.name}`;
  group.innerHTML = `
    <div class="tb-group__fallback">
      <tb-tab label="Source">
        <div class="tb-tab__content"><p>Source tab</p></div>
      </tb-tab>
      <tb-tab label="Rendered">
        <div class="tb-tab__content">${fixture.html}</div>
      </tb-tab>
    </div>
  `;
  document.body.appendChild(group);
  return group;
}

function ownTabs(group) {
  return Array.from(group.querySelectorAll(":scope > .tb-group__tablist > .tb-group__tab"));
}

describe("tb-group nested focus regression", () => {
  it.each(fixtures)("tabs from a selected tab into the $name controls", (fixture) => {
    vi.spyOn(Math, "random").mockReturnValue(0.99);
    const group = appendGroupWithRenderedFixture(fixture);
    const tabs = ownTabs(group);
    const expected = group.querySelector(fixture.selector);

    expect(expected).not.toBeNull();

    click(tabs[1]);
    keydown(tabs[1], "Tab");

    expect(document.activeElement).toBe(expected);
  });
});
