"""Tests for SSRF URL validation."""

from app.core.url_validator import validate_url


class TestValidateUrl:
    def test_valid_https_url(self):
        valid, error = validate_url("https://example.com")
        assert valid is True
        assert error is None

    def test_valid_http_url(self):
        valid, error = validate_url("http://example.com")
        assert valid is True
        assert error is None

    def test_blocks_localhost(self):
        valid, error = validate_url("http://localhost")
        assert valid is False
        assert "not allowed" in error

    def test_blocks_localhost_with_port(self):
        valid, error = validate_url("http://localhost:8080")
        assert valid is False
        assert "not allowed" in error

    def test_blocks_127_0_0_1(self):
        valid, error = validate_url("http://127.0.0.1")
        assert valid is False
        assert "private" in error.lower() or "not allowed" in error.lower()

    def test_blocks_private_10_range(self):
        valid, error = validate_url("http://10.0.0.1")
        assert valid is False

    def test_blocks_private_172_range(self):
        valid, error = validate_url("http://172.16.0.1")
        assert valid is False

    def test_blocks_private_192_range(self):
        valid, error = validate_url("http://192.168.1.1")
        assert valid is False

    def test_blocks_metadata_endpoint(self):
        valid, error = validate_url("http://169.254.169.254/latest/meta-data/")
        assert valid is False

    def test_blocks_gcp_metadata(self):
        valid, error = validate_url("http://metadata.google.internal")
        assert valid is False
        assert "not allowed" in error

    def test_blocks_ftp_scheme(self):
        valid, error = validate_url("ftp://example.com/file.txt")
        assert valid is False
        assert "scheme" in error.lower()

    def test_blocks_file_scheme(self):
        valid, error = validate_url("file:///etc/passwd")
        assert valid is False
        assert "scheme" in error.lower()

    def test_blocks_empty_url(self):
        valid, error = validate_url("")
        assert valid is False

    def test_blocks_no_hostname(self):
        valid, error = validate_url("https://")
        assert valid is False

    def test_valid_url_with_path(self):
        valid, error = validate_url("https://example.com/page?q=test")
        assert valid is True
        assert error is None

    def test_blocks_unresolvable_hostname(self):
        valid, error = validate_url("https://this-domain-definitely-does-not-exist-abc123xyz.com")
        assert valid is False
        assert "resolve" in error.lower()
