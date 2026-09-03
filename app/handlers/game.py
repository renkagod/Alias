import asyncio
import html as html_lib
import json
import random
import re
import unicodedata
from collections import OrderedDict
from urllib.parse import quote

import httpx
from telegram import Update, LinkPreviewOptions
from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

from ..data_manager import user_language, user_selected_dict, get_words_from_dict
from ..texts import get_text
from ..config import DEFAULT_LANG, logger

WIKTIONARY_USER_AGENT = "AliasTelegramBot/1.0 (https://github.com/renkagod/Alias)"
DEFINITION_TIMEOUT = 2.5
MAX_DEFINITIONS = 3
MAX_DEFINITION_LENGTH = 220
MAX_DEFINITION_CACHE_SIZE = 500
DEFINITION_CACHE: OrderedDict[tuple[str, str], list[str]] = OrderedDict()
_definition_cache_lock = asyncio.Lock()

_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=DEFINITION_TIMEOUT,
            headers={"User-Agent": WIKTIONARY_USER_AGENT},
            follow_redirects=True,
        )
    return _http_client


async def close_http_client():
    global _http_client
    if _http_client and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_for_compare(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _strip_headword_prefix(definition: str, word: str) -> str:
    definition = definition.strip()
    if not definition:
        return definition

    normalized_def = _normalize_for_compare(definition)
    normalized_word = _normalize_for_compare(word)
    if not normalized_def.startswith(normalized_word):
        return definition

    if len(normalized_def) > len(normalized_word) and normalized_def[len(normalized_word)].isalnum():
        return definition

    pattern_parts: list[str] = []
    for ch in word:
        if ch.isspace():
            pattern_parts.append(r"\s+")
        else:
            pattern_parts.append(f"{re.escape(ch)}\u0301?")

    pattern = r"^\s*" + "".join(pattern_parts) + r"\s*(?:[-—–:;,]\s*)?"
    stripped = re.sub(pattern, "", definition, flags=re.IGNORECASE)
    stripped = stripped.strip()
    return stripped if stripped else definition


async def _http_get_json(url: str) -> tuple[int | None, dict | None]:
    client = _get_http_client()
    try:
        response = await client.get(url)
        if response.status_code != 200:
            return response.status_code, None
        return response.status_code, response.json()
    except Exception as exc:
        logger.debug(f"Definition request failed for url={url}: {exc}")
        return None, None


def _extract_ru_definitions(extract_html: str, word: str) -> list[str]:
    heading_match = re.search(
        r"<h[2-6][^>]*>\s*(?:<span[^>]*>\s*)?Значение\s*(?:</span>\s*)?</h[2-6]>",
        extract_html,
        flags=re.DOTALL,
    )
    if not heading_match:
        return []

    section_html = extract_html[heading_match.end():]
    list_match = re.search(r"<ol>(.*?)</ol>", section_html, flags=re.DOTALL)
    if not list_match:
        return []

    definitions: list[str] = []
    for raw_item in re.findall(r"<li[^>]*>(.*?)</li>", list_match.group(1), flags=re.DOTALL):
        clean_item = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", raw_item, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", clean_item)
        text = html_lib.unescape(text)
        text = text.split("◆", 1)[0]
        text = _normalize_ws(text)
        if not text:
            continue
        if text.startswith("Отсутствует пример"):
            continue

        text = _strip_headword_prefix(text, word)
        if _normalize_for_compare(text) == _normalize_for_compare(word):
            continue

        if len(text) > MAX_DEFINITION_LENGTH:
            text = text[: MAX_DEFINITION_LENGTH - 1].rstrip() + "…"

        if text not in definitions:
            definitions.append(text)
        if len(definitions) >= MAX_DEFINITIONS:
            break

    return definitions


def _extract_en_definitions(definition_data: dict, word: str) -> list[str]:
    lang_data = definition_data.get("en", [])
    if not lang_data and definition_data:
        first_value = next(iter(definition_data.values()), [])
        if isinstance(first_value, list):
            lang_data = first_value

    definitions: list[str] = []
    for part in lang_data:
        if not isinstance(part, dict):
            continue
        for def_obj in part.get("definitions", []):
            raw_definition = def_obj.get("definition")
            if not raw_definition:
                continue

            clean_definition = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", raw_definition, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", "", clean_definition)
            text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
            text = html_lib.unescape(text)
            text = _normalize_ws(text)
            if not text:
                continue

            text = _strip_headword_prefix(text, word)
            if _normalize_for_compare(text) == _normalize_for_compare(word):
                continue

            if len(text) > MAX_DEFINITION_LENGTH:
                text = text[: MAX_DEFINITION_LENGTH - 1].rstrip() + "…"

            if text not in definitions:
                definitions.append(text)
            if len(definitions) >= MAX_DEFINITIONS:
                return definitions

    return definitions


async def fetch_definitions(word: str, lang: str) -> list[str]:
    normalized_word = word.strip().lower()
    cache_key = (lang, normalized_word)
    cached_definitions = None
    async with _definition_cache_lock:
        if cache_key in DEFINITION_CACHE:
            DEFINITION_CACHE.move_to_end(cache_key)
            cached_definitions = DEFINITION_CACHE[cache_key]
    if cached_definitions is not None:
        return cached_definitions

    candidates = [normalized_word]
    if normalized_word:
        candidates.append(normalized_word.capitalize())

    definitions: list[str] = []

    if lang == "ru":
        for candidate in candidates:
            url = (
                "https://ru.wiktionary.org/w/api.php"
                f"?action=query&prop=extracts&titles={quote(candidate.replace(' ', '_'))}&format=json"
            )
            status, payload = await _http_get_json(url)
            if status != 200 or not payload:
                continue

            page = next(iter(payload.get("query", {}).get("pages", {}).values()), {})
            extract_html = page.get("extract", "")
            definitions = _extract_ru_definitions(extract_html, normalized_word)
            if definitions:
                break
    else:
        for candidate in candidates:
            url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{quote(candidate.replace(' ', '_'))}"
            status, payload = await _http_get_json(url)
            if status != 200 or not payload:
                continue
            definitions = _extract_en_definitions(payload, normalized_word)
            if definitions:
                break

    async with _definition_cache_lock:
        cached_definitions = DEFINITION_CACHE.get(cache_key)
        if cached_definitions is not None:
            DEFINITION_CACHE.move_to_end(cache_key)
            return cached_definitions
        DEFINITION_CACHE[cache_key] = definitions
        while len(DEFINITION_CACHE) > MAX_DEFINITION_CACHE_SIZE:
            DEFINITION_CACHE.popitem(last=False)
    return definitions


def _build_word_message(word: str, lang: str, definitions: list[str] | None = None) -> str:
    dictionary_link = f"https://{lang}.wiktionary.org/wiki/{quote(word.replace(' ', '_'))}"
    safe_word = html_lib.escape(word)
    message_text = f"{get_text('random_word_title', lang)} <a href='{dictionary_link}'><b>{safe_word}</b></a>"

    if definitions:
        title = html_lib.escape(get_text("definition_title", lang))
        message_text += f"\n\n📖 <b>{title}:</b>\n<tg-spoiler>"
        
        spoiler_content = ""
        for index, item in enumerate(definitions):
            item_escaped = html_lib.escape(item)
            label_regex = r'^((?:(?:[а-яё0-9-+]+\.|\bсленг\b|\bтабу\b|\bкино\b)\s*,?\s*)+)(\s*)'
            item_bolded = re.sub(label_regex, r'<b>\1</b>\2', item_escaped)
            
            prefix = f"{index + 1}. " if len(definitions) > 1 else "• "
            spoiler_content += f"{prefix}{item_bolded}\n\n"

        message_text += f"{spoiler_content.strip()}</tg-spoiler>"

    return message_text


def _log_background_task(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    try:
        task.result()
    except Exception as exc:
        logger.error(f"Definition background task failed: {exc}")


async def _append_definition_spoiler(message, word: str, lang: str) -> None:
    definitions = await fetch_definitions(word, lang)
    if not definitions:
        return

    updated_text = _build_word_message(word, lang, definitions)
    try:
        await message.edit_text(
            updated_text, 
            parse_mode="HTML", 
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except BadRequest as exc:
        if "message is not modified" not in str(exc).lower():
            logger.warning(f"Failed to edit message with definition: {exc}")
    except TelegramError as exc:
        logger.debug(f"Telegram error while editing definition: {exc}")


async def handle_random_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .settings import handle_change_dict
    user_id = update.effective_user.id
    lang = user_language.get(user_id, DEFAULT_LANG)
    active_dict = user_selected_dict.get(user_id)

    if not active_dict:
        await handle_change_dict(update, context)
        return

    words = await get_words_from_dict(active_dict)
    if not words:
        await update.message.reply_text(get_text('no_words_in_dict', lang))
        return

    last_word = context.user_data.get('last_word')
    if len(words) > 1 and last_word in words:
        candidates = [w for w in random.sample(words, min(5, len(words))) if w != last_word]
        word_text = candidates[0] if candidates else random.choice(words)
    else:
        word_text = random.choice(words)

    context.user_data['last_word'] = word_text
    base_message = _build_word_message(word_text, lang)
    sent_message = await update.message.reply_text(
        base_message,
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )

    definition_task = asyncio.create_task(_append_definition_spoiler(sent_message, word_text, lang))
    definition_task.add_done_callback(_log_background_task)
