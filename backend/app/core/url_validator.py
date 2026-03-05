"""
URL Validator with SSRF Protection.

Blocks requests to internal/private networks, metadata endpoints,
and other dangerous targets.
"""

import ipaddress
import socket
from urllib.parse import urlparse

# Private/reserved IP ranges that should never be accessed
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "metadata.google",
    "169.254.169.254",
}

ALLOWED_SCHEMES = {"http", "https"}


def validate_url(url: str) -> tuple[bool, str | None]:
    """
    Validate a URL for SSRF protection.

    Returns:
        (True, None) if valid
        (False, error_message) if blocked
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format."

    # Check scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"URL scheme '{parsed.scheme}' is not allowed. Use http or https."

    # Check hostname exists
    hostname = parsed.hostname
    if not hostname:
        return False, "URL must include a hostname."

    # Check blocked hostnames
    if hostname.lower() in BLOCKED_HOSTNAMES:
        return False, f"Access to '{hostname}' is not allowed."

    # Resolve DNS and check IP
    try:
        addr_infos = socket.getaddrinfo(hostname, parsed.port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False, f"Could not resolve hostname '{hostname}'."

    for addr_info in addr_infos:
        ip_str = addr_info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        for network in BLOCKED_IP_NETWORKS:
            if ip in network:
                return False, f"Access to private/internal network addresses is not allowed."

    return True, None
