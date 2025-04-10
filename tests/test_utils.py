import pytest
from app.utils import preprocess_text


def test_preprocess_text():
    assert preprocess_text("  Hello World!  ") == "hello world!"
    assert preprocess_text(None) == ""
