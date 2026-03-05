"""
Stealth and browser constants inspired by Scrapling.

Contains browser flags, resource blocking lists, user agents,
and helper functions for anti-detection.
"""

import random
from urllib.parse import urlparse

# Resource types to block for performance
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

# Stealth browser arguments (inspired by Scrapling)
STEALTH_ARGS: tuple[str, ...] = (
    "--disable-blink-features=AutomationControlled",
    "--disable-features=AutomationControlled",
    "--disable-automation",
    "--mute-audio",
    "--disable-sync",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-breakpad",
    "--disable-client-side-phishing-detection",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-dev-shm-usage",
    "--disable-domain-reliability",
    "--disable-extensions",
    "--disable-features=TranslateUI",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--disable-setuid-sandbox",
    "--disable-site-isolation-trials",
    "--disable-speech-api",
    "--disable-web-security",
    "--force-color-profile=srgb",
    "--metrics-recording-only",
    "--no-sandbox",
    "--password-store=basic",
    "--use-mock-keychain",
    "--ignore-certificate-errors",
    "--allow-running-insecure-content",
    "--window-size=1920,1080",
)

# Default performance args
DEFAULT_ARGS: tuple[str, ...] = (
    "--no-pings",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-infobars",
    "--disable-gpu",
    "--disable-notifications",
    "--disable-offer-store-unmasked-wallet-cards",
    "--disable-offer-upload-credit-cards",
    "--hide-scrollbars",
    "--lang=en-US",
)

# Args to remove from defaults (harmful for stealth)
HARMFUL_ARGS: tuple[str, ...] = (
    "--enable-automation",
    "--disable-popup-blocking",
)

# Realistic user agents (Chrome 130-131 on Windows/Mac/Linux + Edge)
USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
)


def get_random_user_agent() -> str:
    """Return a random realistic user agent string."""
    return random.choice(USER_AGENTS)


def generate_convincing_referer(url: str) -> str | None:
    """Generate a Google Search referer for the target URL's domain."""
    try:
        parsed = urlparse(url)
        domain = parsed.hostname
        if domain:
            return f"https://www.google.com/search?q={domain}"
    except Exception:
        pass
    return None
