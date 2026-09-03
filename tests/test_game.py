import pytest
from app.handlers.game import (
    _normalize_ws,
    _normalize_for_compare,
    _strip_headword_prefix,
    _extract_ru_definitions,
    _extract_en_definitions,
    _build_word_message,
)


def test_normalize_ws():
    assert _normalize_ws("  hello   world  \n\t") == "hello world"
    assert _normalize_ws("") == ""


def test_normalize_for_compare():
    assert _normalize_for_compare("Яблоко") == "яблоко"
    assert _normalize_for_compare("ко́шка") == "кошка"


def test_strip_headword_prefix():
    assert _strip_headword_prefix("яблоко — плод яблони", "яблоко") == "плод яблони"
    assert _strip_headword_prefix("яблоко: сочный плод", "яблоко") == "сочный плод"
    assert _strip_headword_prefix("сочный плод", "яблоко") == "сочный плод"


def test_extract_ru_definitions():
    html_sample = """
    <h2><span id="Значение">Значение</span></h2>
    <ol>
      <li>плод яблони, кисло-сладкий фрукт ◆ <span>Отсутствует пример</span></li>
      <li><style>.some-css{display:none}</style>архит. декоративная деталь</li>
    </ol>
    """
    defs = _extract_ru_definitions(html_sample, "яблоко")
    assert len(defs) == 2
    assert defs[0] == "плод яблони, кисло-сладкий фрукт"
    assert defs[1] == "архит. декоративная деталь"
    assert "some-css" not in defs[1]


def test_extract_en_definitions_strips_style_tags():
    data = {
        "en": [
            {
                "definitions": [
                    {
                        "definition": '<style data-mw-deduplicate="foo">.defdate{font-size:smaller}</style>A round fruit.'
                    },
                    {
                        "definition": "The tree of the genus [[Malus]]."
                    }
                ]
            }
        ]
    }
    defs = _extract_en_definitions(data, "apple")
    assert len(defs) == 2
    assert defs[0] == "A round fruit."
    assert "defdate" not in defs[0]
    assert defs[1] == "The tree of the genus Malus."


def test_build_word_message_without_definitions():
    msg = _build_word_message("яблоко", "ru")
    assert "<b>яблоко</b>" in msg
    assert "https://ru.wiktionary.org/wiki/%D1%8F%D0%B1%D0%BB%D0%BE%D0%BA%D0%BE" in msg
    assert "<tg-spoiler>" not in msg


def test_build_word_message_with_definitions():
    msg = _build_word_message("яблоко", "ru", ["сочный плод", "декоративная деталь"])
    assert "<tg-spoiler>" in msg
    assert "</tg-spoiler>" in msg
    assert "1. сочный плод" in msg
    assert "2. декоративная деталь" in msg


def test_build_word_message_escapes_html_in_word():
    msg = _build_word_message("<script>alert(1)</script>", "en")
    assert "<script>" not in msg
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in msg
