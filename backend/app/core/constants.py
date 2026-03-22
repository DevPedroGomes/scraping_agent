"""
Stealth and browser constants extracted from Scrapling.

Contains browser flags, resource blocking lists, header generation,
and helper functions for anti-detection.

Source: scrapling/engines/constants.py + scrapling/engines/toolbelt/fingerprints.py
"""

import random
from urllib.parse import urlparse

# Resource types to block for performance (matches Scrapling EXTRA_RESOURCES)
BLOCKED_RESOURCE_TYPES: set[str] = {
    "font",
    "image",
    "media",
    "beacon",
    "object",
    "imageset",
    "texttrack",
    "websocket",
    "csp_report",
    "stylesheet",
}

# Args to remove from Chromium defaults (harmful for stealth)
# Matches Scrapling: constants.py lines 15-22
HARMFUL_ARGS: tuple[str, ...] = (
    "--enable-automation",
    "--disable-popup-blocking",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-extensions",
)

# Default performance args (matches Scrapling: constants.py lines 24-37)
DEFAULT_ARGS: tuple[str, ...] = (
    "--no-pings",
    "--no-first-run",
    "--disable-infobars",
    "--disable-breakpad",
    "--no-service-autorun",
    "--homepage=about:blank",
    "--password-store=basic",
    "--disable-hang-monitor",
    "--no-default-browser-check",
    "--disable-session-crashed-bubble",
    "--disable-search-engine-choice-screen",
)

# Stealth browser arguments (matches Scrapling: constants.py lines 39-99)
STEALTH_ARGS: tuple[str, ...] = (
    "--test-type",
    "--lang=en-US",
    "--mute-audio",
    "--disable-sync",
    "--hide-scrollbars",
    "--disable-logging",
    "--start-maximized",
    "--enable-async-dns",
    "--accept-lang=en-US",
    "--use-mock-keychain",
    "--disable-translate",
    "--disable-voice-input",
    "--window-position=0,0",
    "--disable-wake-on-wifi",
    "--ignore-gpu-blocklist",
    "--enable-tcp-fast-open",
    "--enable-web-bluetooth",
    "--disable-cloud-import",
    "--disable-print-preview",
    "--disable-dev-shm-usage",
    "--metrics-recording-only",
    "--disable-crash-reporter",
    "--disable-partial-raster",
    "--disable-gesture-typing",
    "--disable-checker-imaging",
    "--disable-prompt-on-repost",
    "--force-color-profile=srgb",
    "--font-render-hinting=none",
    "--aggressive-cache-discard",
    "--disable-cookie-encryption",
    "--disable-domain-reliability",
    "--disable-threaded-animation",
    "--disable-threaded-scrolling",
    "--enable-simple-cache-backend",
    "--disable-background-networking",
    "--enable-surface-synchronization",
    "--disable-image-animation-resync",
    "--disable-renderer-backgrounding",
    "--disable-ipc-flooding-protection",
    "--prerender-from-omnibox=disabled",
    "--safebrowsing-disable-auto-update",
    "--disable-offer-upload-credit-cards",
    "--disable-background-timer-throttling",
    "--disable-new-content-rendering-timeout",
    "--run-all-compositor-stages-before-draw",
    "--disable-client-side-phishing-detection",
    "--disable-backgrounding-occluded-windows",
    "--disable-layer-tree-host-memory-pressure",
    "--autoplay-policy=user-gesture-required",
    "--disable-offer-store-unmasked-wallet-cards",
    "--disable-blink-features=AutomationControlled",
    "--disable-component-extensions-with-background-pages",
    "--enable-features=NetworkService,NetworkServiceInProcess,TrustTokens,TrustTokensAlwaysAllowIssuance",
    "--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4",
    "--disable-features=AudioServiceOutOfProcess,TranslateUI,BlinkGenPropertyTrees",
)

# Extra stealth flags for specific protections
CANVAS_NOISE_ARG = "--fingerprinting-canvas-image-data-noise"
WEBRTC_BLOCK_ARGS: tuple[str, ...] = (
    "--webrtc-ip-handling-policy=disable_non_proxied_udp",
    "--force-webrtc-ip-handling-policy",
)

# Fallback user agents if browserforge is not available
_FALLBACK_USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
)

# Try to use browserforge for realistic header generation (like Scrapling)
try:
    from browserforge.headers import Browser, HeaderGenerator

    def generate_headers(browser_mode: bool = True) -> dict:
        """Generate realistic browser headers using browserforge.

        In browser mode, matches Chrome/current OS to avoid fingerprinting red flags.
        """
        browsers = [Browser(name="chrome", min_version=141, max_version=143)]
        if not browser_mode:
            browsers.extend([
                Browser(name="firefox", min_version=142),
                Browser(name="edge", min_version=140),
            ])
        os_names = ("windows", "macos", "linux")
        return HeaderGenerator(browser=browsers, os=os_names, device="desktop").generate()

    def get_random_user_agent() -> str:
        """Generate a realistic user agent via browserforge."""
        return generate_headers(browser_mode=True).get(
            "User-Agent", _FALLBACK_USER_AGENTS[0]
        )

    def get_browser_headers() -> dict:
        """Generate a full set of realistic browser headers."""
        return generate_headers(browser_mode=True)

    _HAS_BROWSERFORGE = True

except ImportError:
    _HAS_BROWSERFORGE = False

    def get_random_user_agent() -> str:
        """Fallback: return a random user agent from hardcoded list."""
        return random.choice(_FALLBACK_USER_AGENTS)

    def get_browser_headers() -> dict:
        """Fallback: return minimal headers with random UA."""
        return {"User-Agent": get_random_user_agent()}


def generate_convincing_referer(url: str) -> str | None:
    """Generate a Google Search referer for the target URL's domain."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return None
        # Strip common subdomains for cleaner search query
        parts = hostname.split(".")
        if len(parts) > 2 and parts[0] in ("www", "m", "mobile"):
            domain = parts[1]
        elif len(parts) >= 2:
            domain = parts[-2]
        else:
            domain = hostname
        if domain and domain not in ("localhost", "127"):
            return f"https://www.google.com/search?q={domain}"
    except Exception:
        pass
    return None
