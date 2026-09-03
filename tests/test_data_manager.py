import asyncio
import os
import json
import pytest
import app.data_manager as dm


def test_get_words_from_dict_and_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(dm, "DICT_PATH", str(tmp_path))
    dm.clear_cache()

    dict_file = tmp_path / "test_dict.txt"
    dict_file.write_text("яблоко\nгруша\nапельсин\n", encoding="utf-8")

    words = asyncio.run(dm.get_words_from_dict("test_dict.txt"))
    assert words == ["яблоко", "груша", "апельсин"]

    # Cached
    assert "test_dict.txt" in dm.WORDS_CACHE
    cached = asyncio.run(dm.get_words_from_dict("test_dict.txt"))
    assert cached == words

    dm.clear_cache("test_dict.txt")
    assert "test_dict.txt" not in dm.WORDS_CACHE


def test_get_words_from_dict_with_bom(tmp_path, monkeypatch):
    monkeypatch.setattr(dm, "DICT_PATH", str(tmp_path))
    dm.clear_cache()

    # Write file with UTF-8 BOM (as produced by Windows Notepad)
    dict_file = tmp_path / "bom_dict.txt"
    dict_file.write_bytes("\ufeffяблоко\nгруша\n".encode("utf-8"))

    words = asyncio.run(dm.get_words_from_dict("bom_dict.txt"))
    assert words[0] == "яблоко"
    assert not words[0].startswith("\ufeff")


def test_get_words_from_dict_nonexistent(tmp_path, monkeypatch):
    monkeypatch.setattr(dm, "DICT_PATH", str(tmp_path))
    words = asyncio.run(dm.get_words_from_dict("nonexistent.txt"))
    assert words == []


def test_save_and_load_data_atomic(tmp_path, monkeypatch):
    data_file = tmp_path / "subfolder" / "user_data.json"
    monkeypatch.setattr(dm, "USER_DATA_FILE", str(data_file))

    lang_data = {12345: "ru", 67890: "en"}
    dict_data = {12345: "Alias 2017 (Normal).txt", 67890: "Alias 2017 (Easy).txt"}

    asyncio.run(dm.save_data(lang_data, dict_data))

    assert data_file.exists()
    loaded_lang, loaded_dict = dm.load_data()
    assert loaded_lang == lang_data
    assert loaded_dict == dict_data


def test_clear_cache_with_path_traversal():
    dm.WORDS_CACHE["secret.txt"] = ["word"]
    dm.clear_cache("../../secret.txt")
    assert "secret.txt" not in dm.WORDS_CACHE
