"""Tests for output schema validation."""

from app.services.scraper_service import OutputValidator
from app.models.schemas import OutputField


class TestOutputValidator:
    def test_valid_data(self):
        fields = [
            OutputField(name="title", type="string", required=True),
            OutputField(name="count", type="number", required=True),
        ]
        data = {"title": "Hello", "count": 42}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is True
        assert errors == []

    def test_missing_required_field(self):
        fields = [
            OutputField(name="title", type="string", required=True),
        ]
        data = {"other": "value"}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is False
        assert any("title" in e for e in errors)

    def test_optional_field_missing_ok(self):
        fields = [
            OutputField(name="title", type="string", required=True),
            OutputField(name="subtitle", type="string", required=False),
        ]
        data = {"title": "Hello"}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is True

    def test_wrong_type_string(self):
        fields = [
            OutputField(name="title", type="string", required=True),
        ]
        data = {"title": 123}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is False
        assert any("wrong type" in e for e in errors)

    def test_wrong_type_number(self):
        fields = [
            OutputField(name="count", type="number", required=True),
        ]
        data = {"count": "not a number"}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is False

    def test_array_type(self):
        fields = [
            OutputField(name="items", type="array", required=True),
        ]
        data = {"items": [1, 2, 3]}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is True

    def test_object_type(self):
        fields = [
            OutputField(name="meta", type="object", required=True),
        ]
        data = {"meta": {"key": "value"}}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is True

    def test_boolean_type(self):
        fields = [
            OutputField(name="active", type="boolean", required=True),
        ]
        data = {"active": True}
        valid, errors = OutputValidator.validate(data, fields)
        assert valid is True

    def test_non_dict_data(self):
        fields = [OutputField(name="x", type="string", required=True)]
        valid, errors = OutputValidator.validate("not a dict", fields)
        assert valid is False
        assert any("not a JSON object" in e for e in errors)

    def test_schema_prompt_generation(self):
        fields = [
            OutputField(name="title", type="string", description="The title", required=True),
        ]
        prompt = OutputValidator.build_schema_prompt(fields)
        assert "title" in prompt
        assert "string" in prompt
        assert "required" in prompt
        assert "JSON" in prompt
