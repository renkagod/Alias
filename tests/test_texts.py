from app.texts import get_text, TEXTS


def test_get_text_existing():
    assert get_text("btn_random_word", "ru") == "🎲 Случайное слово"
    assert get_text("btn_random_word", "en") == "🎲 Random Word"


def test_get_text_unknown_key():
    assert get_text("nonexistent_key_12345", "ru") == "<nonexistent_key_12345>"


def test_get_text_invalid_lang_fallback():
    assert get_text("btn_random_word", "invalid_lang", default_lang="ru") == "🎲 Случайное слово"
    assert get_text("btn_random_word", "invalid_lang", default_lang="en") == "🎲 Random Word"


def test_all_keys_in_both_languages():
    ru_keys = set(TEXTS["ru"].keys())
    en_keys = set(TEXTS["en"].keys())
    assert ru_keys == en_keys
