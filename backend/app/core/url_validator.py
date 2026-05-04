"""
URL Validator with SSRF Protection.

Blocks requests to internal/private networks, metadata endpoints,
and other dangerous targets. Also normalizes hostnames to defeat
common evasion tricks (punycode, octal/hex IPs, IPv4-mapped IPv6).
"""

import ipaddress
import re
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
    ipaddress.ip_network("198.18.0.0/15"),  # Benchmark
    ipaddress.ip_network("192.0.0.0/24"),  # IETF protocol assignments
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved (former Class E)
    ipaddress.ip_network("192.0.2.0/24"),  # TEST-NET-1
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
    ipaddress.ip_network("255.255.255.255/32"),  # Limited broadcast
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ipaddress.ip_network("64:ff9b::/96"),  # IPv4/IPv6 translation
    ipaddress.ip_network("2001:db8::/32"),  # Documentation
    ipaddress.ip_network("2002::/16"),  # 6to4
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "metadata.google",
    "169.254.169.254",
    "metadata.aws.internal",
    "fd00:ec2::254",
    "metadata.azure.internal",
    "metadata.packet.net",
    "metadata.tencentyun.com",
    "metadata.oraclecloud.com",
    "100.100.100.200",
    "host.docker.internal",
    "gateway.docker.internal",
}

ALLOWED_SCHEMES = {"http", "https"}

# Strict dotted-quad: rejects octal, hex, integer-int forms
_DOTTED_QUAD_RE = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")


def _normalize_hostname(hostname: str) -> tuple[str | None, str | None]:
    """Normalize a hostname before DNS resolution.

    Returns (normalized_hostname, error). On error, normalized_hostname is None.
    """
    if not hostname:
        return None, "URL must include a hostname."

    if "@" in hostname:
        return None, "Hostname cannot contain '@'."

    # Strip a single trailing dot
    if hostname.endswith("."):
        hostname = hostname[:-1]

    # Unwrap [IPv6] forms (urlparse usually does this, defensive)
    if hostname.startswith("[") and hostname.endswith("]"):
        hostname = hostname[1:-1]

    # Try IPv6 IPv4-mapped substitution (::ffff:7f00:1 -> 127.0.0.1)
    try:
        ip = ipaddress.ip_address(hostname)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            hostname = str(ip.ipv4_mapped)
    except ValueError:
        pass

    # Decode punycode (IDNA) for Unicode hostnames; harmless for ASCII
    try:
        hostname = hostname.encode("idna").decode("ascii")
    except (UnicodeError, UnicodeDecodeError):
        # If IDNA fails for an apparent IP literal, that's fine; otherwise reject.
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            return None, "Invalid hostname encoding."

    # If the hostname looks numeric (any digit + dot pattern) but not a strict
    # dotted-quad and not a valid IPv6 literal, reject (octal/hex/integer evasion).
    looks_ipv4_ish = bool(re.match(r"^[0-9xXa-fA-F.]+$", hostname)) and "." in hostname
    if looks_ipv4_ish:
        m = _DOTTED_QUAD_RE.match(hostname)
        if not m:
            # try IPv6 literal as fallback
            try:
                ipaddress.IPv6Address(hostname)
            except ValueError:
                return None, "Numeric hostname must be a strict dotted-quad IPv4."
        else:
            for octet in m.groups():
                if not (0 <= int(octet) <= 255) or (len(octet) > 1 and octet.startswith("0")):
                    return None, "Invalid IPv4 octet (octal/leading-zero forms blocked)."

    return hostname.lower(), None


def validate_url(url: str) -> tuple[bool, str | None, set[str] | None]:
    """
    Validate a URL for SSRF protection.

    Returns:
        (True, None, allowed_ips_set) if valid (allowed_ips contains the resolved IPs)
        (False, error_message, None) if blocked
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format.", None

    # Check scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"URL scheme '{parsed.scheme}' is not allowed. Use http or https.", None

    hostname = parsed.hostname
    normalized, err = _normalize_hostname(hostname)
    if err:
        return False, err, None

    # Check blocked hostnames
    if normalized in BLOCKED_HOSTNAMES:
        return False, f"Access to '{normalized}' is not allowed.", None

    # Resolve DNS and check IPs
    try:
        addr_infos = socket.getaddrinfo(normalized, parsed.port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False, f"Could not resolve hostname '{normalized}'.", None

    allowed_ips: set[str] = set()
    for addr_info in addr_infos:
        ip_str = addr_info[4][0]
        # strip IPv6 zone identifier if present (e.g. fe80::1%eth0)
        if "%" in ip_str:
            ip_str = ip_str.split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        for network in BLOCKED_IP_NETWORKS:
            if ip in network:
                return False, "Access to private/internal network addresses is not allowed.", None

        allowed_ips.add(str(ip))

    if not allowed_ips:
        return False, f"No usable IPs resolved for '{normalized}'.", None

    return True, None, allowed_ips
