"""Tests for HTML to Markdown conversion."""

from app.services.scraper_service import HTMLToMarkdown


class TestHTMLToMarkdown:
    def test_basic_conversion(self):
        html = "<h1>Hello</h1><p>World</p>"
        markdown, reduction = HTMLToMarkdown.convert(html)
        assert "Hello" in markdown
        assert "World" in markdown

    def test_removes_script_tags(self):
        html = "<p>Content</p><script>alert('xss')</script>"
        markdown, _ = HTMLToMarkdown.convert(html)
        assert "alert" not in markdown
        assert "Content" in markdown

    def test_removes_style_tags(self):
        html = "<p>Content</p><style>body{color:red}</style>"
        markdown, _ = HTMLToMarkdown.convert(html)
        assert "color" not in markdown
        assert "Content" in markdown

    def test_removes_nav_footer_header(self):
        html = "<nav>Menu</nav><main><p>Main content</p></main><footer>Footer</footer>"
        markdown, _ = HTMLToMarkdown.convert(html)
        assert "Menu" not in markdown
        assert "Footer" not in markdown
        assert "Main content" in markdown

    def test_reduction_percentage(self):
        html = "<html><head><style>.x{}</style></head><body><p>Short</p></body></html>"
        markdown, reduction = HTMLToMarkdown.convert(html)
        assert reduction > 0
        assert len(markdown) < len(html)

    def test_empty_html(self):
        markdown, reduction = HTMLToMarkdown.convert("")
        assert markdown == ""
        assert reduction == 0

    def test_cleans_excessive_whitespace(self):
        html = "<p>A</p>\n\n\n\n\n<p>B</p>"
        markdown, _ = HTMLToMarkdown.convert(html)
        assert "\n\n\n" not in markdown

    def test_removes_form_elements(self):
        html = "<form><input type='text'><button>Submit</button></form><p>Data</p>"
        markdown, _ = HTMLToMarkdown.convert(html)
        assert "Submit" not in markdown
        assert "Data" in markdown
