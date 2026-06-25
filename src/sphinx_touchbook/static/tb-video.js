class TbVideo extends HTMLElement {
  connectedCallback() {
    if (this.dataset.enhanced === "true") {
      return;
    }
    this.dataset.enhanced = "true";
    this.config = this.readConfig();
    this.playing = false;
    this.fallback = this.querySelector(":scope > .tb-video__fallback");
    if (!this.fallback) {
      return;
    }

    this.notes = this.querySelector(":scope > .tb-video__notes");
    this.placeholder = this.querySelector(":scope > .tb-video__fallback .tb-video__placeholder");
    this.controls = document.createElement("div");
    this.controls.className = "tb-video__controls";

    this.button = document.createElement("button");
    this.button.type = "button";
    this.button.className = "tb-video__button";
    this.button.textContent = this.buttonLabel();

    if (!this.usesExternalPlayback()) {
      this.button.setAttribute("aria-expanded", "false");
      this.button.setAttribute("aria-controls", this.playerId());
      this.player = document.createElement("div");
      this.player.className = "tb-video__player";
      this.player.id = this.playerId();
      this.player.hidden = true;
    }

    this.button.addEventListener("click", () => this.activate());
    if (this.placeholder) {
      this.placeholder.addEventListener("click", (event) => this.activateFromPlaceholder(event));
    }

    const anchor = this.notes || this.querySelector(":scope > script.tb-video__config");
    if (anchor) {
      anchor.before(this.controls);
      if (this.player) {
        this.controls.after(this.player);
      }
    } else if (this.player) {
      this.append(this.player, this.controls);
    } else {
      this.append(this.controls);
    }
    this.controls.append(this.button);
  }

  readConfig() {
    const script = this.querySelector(":scope > script.tb-video__config");
    if (!script) {
      return {};
    }
    try {
      return JSON.parse(script.textContent);
    } catch (error) {
      return {};
    }
  }

  buttonLabel() {
    if (this.usesExternalPlayback()) {
      return this.config.openLabel || "Open video in new window";
    }
    return this.config.playLabel || "Play video";
  }

  activate() {
    if (this.usesExternalPlayback()) {
      window.open(this.externalPlaybackUrl(), "_blank", "noopener,noreferrer");
      return;
    }

    if (this.playing) {
      this.pausePlayer();
    } else {
      this.showPlayer({ autoplay: true });
    }
  }

  activateFromPlaceholder(event) {
    if (this.usesExternalPlayback()) {
      return;
    }
    event.preventDefault();
    this.showPlayer({ autoplay: true });
  }

  showPlayer(options = {}) {
    if (!this.player.firstElementChild) {
      this.player.append(this.createPlayerElement(options));
    }
    this.controls.before(this.player);
    this.fallback.hidden = true;
    this.player.hidden = false;
    this.button.textContent = this.config.pauseLabel || this.config.hideLabel || "Pause video";
    this.button.setAttribute("aria-expanded", "true");
    this.playing = true;
    this.playNativeVideoIfRequested(options);
  }

  pausePlayer() {
    if (this.config.kind === "video") {
      const video = this.player.querySelector("video");
      if (video && typeof video.pause === "function") {
        video.pause();
      }
    } else {
      this.player.replaceChildren();
      this.fallback.hidden = false;
      this.player.hidden = true;
      this.controls.after(this.player);
      this.button.setAttribute("aria-expanded", "false");
    }
    this.button.textContent = this.config.playLabel || "Play video";
    this.playing = false;
  }

  createPlayerElement(options = {}) {
    if (this.config.kind === "video") {
      const video = document.createElement("video");
      video.controls = true;
      video.preload = "metadata";
      if (this.config.thumbnailUrl) {
        video.poster = this.config.thumbnailUrl;
      }
      if (options.autoplay) {
        video.autoplay = true;
      }
      const source = document.createElement("source");
      source.src = this.config.embedUrl || this.config.sourceUrl || "";
      const mimeType = this.mimeTypeFor(source.src);
      if (mimeType) {
        source.type = mimeType;
      }
      if (this.isUnsupportedNativeVideo(video, mimeType)) {
        return this.createUnsupportedMessage(source.src, mimeType);
      }
      video.append(source);
      video.append("This browser cannot play the video inline. Use the video link above.");
      return video;
    }

    const iframe = document.createElement("iframe");
    iframe.src = this.playerUrl();
    iframe.title = "Video player";
    iframe.loading = "lazy";
    iframe.allowFullscreen = true;
    iframe.referrerPolicy = "strict-origin-when-cross-origin";
    iframe.setAttribute(
      "allow",
      "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
    );
    return iframe;
  }

  playNativeVideoIfRequested(options = {}) {
    if (!options.autoplay || this.config.kind !== "video") {
      return;
    }
    const video = this.player.querySelector("video");
    if (video && typeof video.play === "function") {
      video.play().catch(() => {});
    }
  }

  isUnsupportedNativeVideo(video, mimeType) {
    if (!mimeType || typeof video.canPlayType !== "function") {
      return false;
    }
    return video.canPlayType(mimeType) === "";
  }

  createUnsupportedMessage(src, mimeType) {
    const message = document.createElement("div");
    message.className = "tb-video__unsupported";
    message.setAttribute("role", "status");

    const text = document.createElement("p");
    text.textContent = this.unsupportedMessage(mimeType);

    const link = document.createElement("a");
    link.href = src;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Open video file";

    message.append(text, link);
    return message;
  }

  unsupportedMessage(mimeType) {
    if (mimeType.includes("ogg")) {
      return "This browser cannot play Ogg Theora/Vorbis video.";
    }
    return "This browser cannot play this video format.";
  }

  playerUrl() {
    const url = this.config.embedUrl || this.config.sourceUrl || "";

    try {
      const parsed = new URL(url, window.location.href);
      if (this.config.provider === "vimeo" && !parsed.searchParams.has("autoplay")) {
        parsed.searchParams.set("autoplay", "1");
      }
      if (
        this.config.provider === "youtube" &&
        !parsed.searchParams.has("origin") &&
        /^https?:$/.test(window.location.protocol)
      ) {
        parsed.searchParams.set("origin", window.location.origin);
      }
      return parsed.toString();
    } catch (error) {
      return url;
    }
  }

  externalPlaybackUrl() {
    if (this.config.provider === "youtube") {
      return this.config.sourceUrl || this.config.embedUrl || "";
    }
    if (this.config.window && this.config.kind === "iframe") {
      return this.playerUrl();
    }
    return this.config.sourceUrl || this.config.embedUrl || "";
  }

  mimeTypeFor(url) {
    try {
      const parsed = new URL(url, window.location.href);
      const path = parsed.pathname.toLowerCase();
      if (path.endsWith(".webm")) {
        return "video/webm";
      }
      if (path.endsWith(".mp4")) {
        return "video/mp4";
      }
      if (path.endsWith(".ogv")) {
        return 'video/ogg; codecs="theora, vorbis"';
      }
      if (path.endsWith(".ogg") || path.endsWith(".ogm")) {
        return "video/ogg";
      }
      if (path.endsWith(".mov")) {
        return "video/quicktime";
      }
    } catch (error) {
      return "";
    }
    return "";
  }

  usesExternalPlayback() {
    return this.config.window || this.config.provider === "youtube";
  }

  playerId() {
    if (!this.id) {
      this.id = `tb-video-${TbVideo.nextId++}`;
    }
    return `${this.id}-player`;
  }
}

TbVideo.nextId = 1;

if (!customElements.get("tb-video")) {
  customElements.define("tb-video", TbVideo);
}
