import pytest

from app.adapters.eml_file import EmlFileAdapter
from app.core.exceptions import AppError


def test_eml_adapter_rejects_non_eml_extension():
    with pytest.raises(AppError):
        EmlFileAdapter(b"hello", "sample.txt").load()


def test_eml_adapter_builds_envelope():
    envelope = EmlFileAdapter(b"From: a@example.com\n\nBody", "sample.eml").load()
    assert envelope.source_type == "eml"
    assert envelope.original_filename == "sample.eml"
