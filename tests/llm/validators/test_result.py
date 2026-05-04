from wealthai.llm.validators.result import ValidationResult


def test_empty_is_valid():
    assert ValidationResult().valid is True


def test_with_errors_is_invalid():
    assert ValidationResult(errors=["oops"]).valid is False


def test_addition_merges_errors():
    result = ValidationResult(errors=["a"]) + ValidationResult(errors=["b"])
    assert result.errors == ["a", "b"]


def test_addition_with_empty_is_identity():
    result = ValidationResult(errors=["a"]) + ValidationResult()
    assert result.errors == ["a"]
