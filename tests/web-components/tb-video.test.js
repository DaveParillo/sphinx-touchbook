import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { click, loadComponentScript } from "./helpers.js";

beforeAll(async () => {
  await loadComponentScript("tb-video.js");
});

beforeEach(() => {
  document.body.innerHTML = "";
  vi.restoreAllMocks();
});

function appendVideo(config = {}) {
  const data = {
    sourceUrl: "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
    embedUrl: "https://www.youtube.com/embed/aqz-KE-bpKQ",
    provider: "youtube",
    kind: "iframe",
    thumbnailUrl: "https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg",
    window: false,
    width: "640",
    height: "360",
    playLabel: "Play video",
    pauseLabel: "Pause video",
    openLabel: "Open video in new window",
    ...config,
  };
  const element = document.createElement("tb-video");
  element.id = "video-example";
  element.setAttribute("source-url", data.sourceUrl);
  element.setAttribute("embed-url", data.embedUrl);
  element.innerHTML = `
    <figure class="tb-video__fallback">
      <a class="tb-video__placeholder" href="${data.sourceUrl}" target="_blank" rel="noopener noreferrer">
        <img class="tb-video__thumbnail" src="${data.thumbnailUrl}" alt="">
        <span class="tb-video__placeholder-icon" aria-hidden="true"></span>
        <span class="tb-video__placeholder-label">Open video</span>
      </a>
    </figure>
    <div class="tb-video__notes"><p>Fast-forward to 1:15.</p></div>
    <script type="application/json" class="tb-video__config">${JSON.stringify(data)}</script>
  `;
  document.body.appendChild(element);
  return element;
}

function visibleMediaFrame(element) {
  const fallback = element.querySelector(".tb-video__fallback");
  const player = element.querySelector(".tb-video__player");
  if (player && !player.hidden) {
    return player;
  }
  return fallback;
}

describe("tb-video Web Component", () => {
  it("opens YouTube in a separate window because watch pages are the reliable target", () => {
    const openMock = vi.spyOn(window, "open").mockImplementation(() => null);
    const element = appendVideo();
    const fallback = element.querySelector(".tb-video__fallback");
    const button = element.querySelector("button.tb-video__button");
    const player = element.querySelector(".tb-video__player");
    const thumbnail = element.querySelector(".tb-video__thumbnail");

    expect(customElements.get("tb-video")).toBeTypeOf("function");
    expect(element.dataset.enhanced).toBe("true");
    expect(fallback.hidden).toBe(false);
    expect(thumbnail.getAttribute("src")).toBe("https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg");
    expect(thumbnail.getAttribute("alt")).toBe("");
    expect(button.textContent).toBe("Open video in new window");
    expect(fallback.nextElementSibling).toBe(element.querySelector(".tb-video__controls"));
    expect(button.hasAttribute("aria-expanded")).toBe(false);
    expect(button.hasAttribute("aria-controls")).toBe(false);
    expect(player).toBeNull();

    click(button);
    expect(openMock).toHaveBeenCalledWith(
      "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("adds an accessible inline control that swaps the placeholder for an iframe", () => {
    const element = appendVideo({
      sourceUrl: "https://vimeo.com/486845755",
      embedUrl: "https://player.vimeo.com/video/486845755",
      provider: "vimeo",
      thumbnailUrl: "",
    });
    const fallback = element.querySelector(".tb-video__fallback");
    const button = element.querySelector("button.tb-video__button");
    const player = element.querySelector(".tb-video__player");

    expect(button.textContent).toBe("Play video");
    expect(fallback.nextElementSibling).toBe(element.querySelector(".tb-video__controls"));
    expect(element.querySelector(".tb-video__controls").nextElementSibling).toBe(player);
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(button.getAttribute("aria-controls")).toBe(player.id);
    expect(player.hidden).toBe(true);
    expect(player.querySelector("iframe")).toBeNull();

    click(button);
    expect(fallback.hidden).toBe(true);
    expect(button.textContent).toBe("Pause video");
    expect(visibleMediaFrame(element).nextElementSibling).toBe(element.querySelector(".tb-video__controls"));
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(player.hidden).toBe(false);
    const iframe = player.querySelector("iframe");
    expect(iframe.src).toContain("https://player.vimeo.com/video/486845755");
    expect(iframe.src).toContain("autoplay=1");
    expect(iframe.referrerPolicy).toBe("strict-origin-when-cross-origin");

    click(button);
    expect(button.textContent).toBe("Play video");
    expect(visibleMediaFrame(element).nextElementSibling).toBe(element.querySelector(".tb-video__controls"));
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(fallback.hidden).toBe(false);
    expect(player.hidden).toBe(true);
    expect(player.querySelector("iframe")).toBeNull();
  });

  it("uses the placeholder as an inline playback trigger when possible", () => {
    const openMock = vi.spyOn(window, "open").mockImplementation(() => null);
    const element = appendVideo({
      sourceUrl: "https://vimeo.com/486845755",
      embedUrl: "https://player.vimeo.com/video/486845755",
      provider: "vimeo",
      thumbnailUrl: "",
    });
    const placeholder = element.querySelector(".tb-video__placeholder");
    const player = element.querySelector(".tb-video__player");

    click(placeholder);

    expect(openMock).not.toHaveBeenCalled();
    expect(player.hidden).toBe(false);
    expect(visibleMediaFrame(element).nextElementSibling).toBe(element.querySelector(".tb-video__controls"));
    expect(player.querySelector("iframe").src).toContain("https://player.vimeo.com/video/486845755");
  });

  it("leaves the placeholder as an external link for YouTube", () => {
    const event = new MouseEvent("click", { bubbles: true, cancelable: true });
    const element = appendVideo();
    const placeholder = element.querySelector(".tb-video__placeholder");

    placeholder.dispatchEvent(event);

    expect(event.defaultPrevented).toBe(false);
    expect(element.querySelector(".tb-video__player")).toBeNull();
  });

  it("opens a separate window when requested", () => {
    const openMock = vi.spyOn(window, "open").mockImplementation(() => null);
    const element = appendVideo({
      window: true,
      kind: "video",
      sourceUrl: "media/lecture-01.mp4",
      embedUrl: "media/lecture-01.mp4",
    });
    const button = element.querySelector("button.tb-video__button");

    expect(button.textContent).toBe("Open video in new window");
    click(button);

    expect(openMock).toHaveBeenCalledOnce();
    expect(openMock).toHaveBeenCalledWith("media/lecture-01.mp4", "_blank", "noopener,noreferrer");
    expect(element.querySelector(".tb-video__player")).toBeNull();
  });

  it("opens a Vimeo window with the embeddable autoplay URL when requested", () => {
    const openMock = vi.spyOn(window, "open").mockImplementation(() => null);
    const element = appendVideo({
      window: true,
      sourceUrl: "https://vimeo.com/486845755",
      embedUrl: "https://player.vimeo.com/video/486845755",
      provider: "vimeo",
      thumbnailUrl: "",
    });
    const button = element.querySelector("button.tb-video__button");

    click(button);

    expect(openMock).toHaveBeenCalledWith(
      "https://player.vimeo.com/video/486845755?autoplay=1",
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("creates a native video element for local webm files", () => {
    vi.spyOn(window.HTMLMediaElement.prototype, "canPlayType").mockReturnValue("probably");
    const playMock = vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue();
    const pauseMock = vi.spyOn(window.HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
    const element = appendVideo({
      provider: "local",
      kind: "video",
      sourceUrl: "_static/Baby_Chick_Hatching.webm",
      embedUrl: "_static/Baby_Chick_Hatching.webm",
      thumbnailUrl: "",
    });
    const button = element.querySelector("button.tb-video__button");

    expect(button.textContent).toBe("Play video");
    expect(visibleMediaFrame(element).nextElementSibling).toBe(element.querySelector(".tb-video__controls"));
    click(button);

    const video = element.querySelector("video");
    expect(video).not.toBeNull();
    expect(video.controls).toBe(true);
    expect(video.autoplay).toBe(true);
    expect(video.getAttribute("preload")).toBe("metadata");
    const source = video.querySelector("source");
    expect(source.src).toContain("_static/Baby_Chick_Hatching.webm");
    expect(source.type).toBe("video/webm");
    expect(playMock).toHaveBeenCalledOnce();

    click(button);
    expect(pauseMock).toHaveBeenCalledOnce();
    expect(button.textContent).toBe("Play video");
    expect(visibleMediaFrame(element).nextElementSibling).toBe(element.querySelector(".tb-video__controls"));
    expect(element.querySelector(".tb-video__fallback").hidden).toBe(true);
    expect(element.querySelector(".tb-video__player").hidden).toBe(false);
  });

  it("uses the placeholder as an inline playback trigger for local webm files", () => {
    const openMock = vi.spyOn(window, "open").mockImplementation(() => null);
    vi.spyOn(window.HTMLMediaElement.prototype, "canPlayType").mockReturnValue("probably");
    const playMock = vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue();
    const element = appendVideo({
      provider: "local",
      kind: "video",
      sourceUrl: "_static/Baby_Chick_Hatching.webm",
      embedUrl: "_static/Baby_Chick_Hatching.webm",
      thumbnailUrl: "",
    });
    const placeholder = element.querySelector(".tb-video__placeholder");

    click(placeholder);

    expect(openMock).not.toHaveBeenCalled();
    expect(element.querySelector("video source").type).toBe("video/webm");
    expect(playMock).toHaveBeenCalledOnce();
  });

  it("creates an Ogg Theora/Vorbis source for local ogv files", () => {
    vi.spyOn(window.HTMLMediaElement.prototype, "canPlayType").mockReturnValue("maybe");
    const playMock = vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue();
    const element = appendVideo({
      provider: "local",
      kind: "video",
      sourceUrl: "_static/wilms-tumor-ct-scan.ogv",
      embedUrl: "_static/wilms-tumor-ct-scan.ogv",
      thumbnailUrl: "",
    });
    const button = element.querySelector("button.tb-video__button");

    click(button);

    const source = element.querySelector("video source");
    expect(source.src).toContain("_static/wilms-tumor-ct-scan.ogv");
    expect(source.type).toBe('video/ogg; codecs="theora, vorbis"');
    expect(playMock).toHaveBeenCalledOnce();
  });

  it("shows a clear message when local ogv is unsupported by the browser", () => {
    vi.spyOn(window.HTMLMediaElement.prototype, "canPlayType").mockReturnValue("");
    const playMock = vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue();
    const element = appendVideo({
      provider: "local",
      kind: "video",
      sourceUrl: "_static/wilms-tumor-ct-scan.ogv",
      embedUrl: "_static/wilms-tumor-ct-scan.ogv",
      thumbnailUrl: "",
    });
    const button = element.querySelector("button.tb-video__button");

    click(button);

    const message = element.querySelector(".tb-video__unsupported");
    expect(element.querySelector("video")).toBeNull();
    expect(message).not.toBeNull();
    expect(message.getAttribute("role")).toBe("status");
    expect(message.textContent).toContain("This browser cannot play Ogg Theora/Vorbis video.");
    expect(message.querySelector("a").href).toContain("_static/wilms-tumor-ct-scan.ogv");
    expect(playMock).not.toHaveBeenCalled();
  });

  it("uses configured thumbnails as native video posters", () => {
    vi.spyOn(window.HTMLMediaElement.prototype, "canPlayType").mockReturnValue("probably");
    vi.spyOn(window.HTMLMediaElement.prototype, "play").mockResolvedValue();
    const element = appendVideo({
      provider: "local",
      kind: "video",
      sourceUrl: "_static/Baby_Chick_Hatching.webm",
      embedUrl: "_static/Baby_Chick_Hatching.webm",
      thumbnailUrl: "_static/hand-index-thumb.svg",
    });
    const button = element.querySelector("button.tb-video__button");

    click(button);

    expect(element.querySelector("video").poster).toContain("_static/hand-index-thumb.svg");
  });
});
