"""normalize() loads each language's RBNF engine once, not once per call."""
import pytest

from phoonnx.normalization import text as text_module


@pytest.fixture
def counting_engine(monkeypatch):
    """Count RbnfEngine.for_language calls; start from an empty engine cache."""
    calls = []
    real = text_module.RbnfEngine.for_language

    def counted(language):
        calls.append(language)
        return real(language)

    monkeypatch.setattr(text_module.RbnfEngine, "for_language", staticmethod(counted))
    monkeypatch.setattr(text_module, "_RBNF_ENGINES", {})
    return calls


def test_engine_is_loaded_once_per_language(counting_engine):
    first = text_module.normalize("I have 12 apples", "en")
    second = text_module.normalize("I have 12 apples", "en")
    assert first == second
    assert counting_engine == ["en"]
    text_module.normalize("J'ai 12 pommes", "fr")
    assert counting_engine == ["en", "fr"]


def test_same_output_as_an_uncached_engine(counting_engine, monkeypatch):
    cached = text_module.normalize("It costs 1234 euros and 5 cents", "en")
    monkeypatch.setattr(text_module, "_RBNF_ENGINES", {})
    assert text_module.normalize("It costs 1234 euros and 5 cents", "en") == cached


def test_unsupported_language_is_not_cached(monkeypatch):
    monkeypatch.setattr(text_module, "_RBNF_ENGINES", {})
    with pytest.raises(ValueError):
        text_module._rbnf_engine("zz-not-a-language")
    assert text_module._RBNF_ENGINES == {}
    # normalize() still works for it, without number spelling
    assert text_module.normalize("hello world", "zz") == "hello world"
