from __future__ import annotations

import json
import re
from typing import Iterable

from .config import settings
from .llm_client import get_client
from .generator_stub import generate_html as generate_html_stub

# OpenAI SDK exception sınıfları sürüme göre farklı import edilebiliyor.
try:
    from openai import (
        OpenAIError,
        RateLimitError,
        AuthenticationError,
        APITimeoutError,
        APIConnectionError,
        BadRequestError,
    )
except Exception:  # pragma: no cover
    from openai import OpenAIError  # type: ignore
    RateLimitError = AuthenticationError = APITimeoutError = APIConnectionError = BadRequestError = OpenAIError  # type: ignore


def _strip_html_to_text(html: str) -> str:
    # Validator zaten HTML ile çalışıyor; burada sadece LLM'e feedback için kaba bir metin çıkarımı.
    return re.sub(r"<[^>]+>", " ", html).strip()


def _safe_str(x) -> str:
    if x is None:
        return ""
    return str(x)


def _parse_image_urls(image_urls_json: str | None) -> list[str]:
    if not image_urls_json:
        return []
    s = image_urls_json.strip()
    if not s:
        return []
    try:
        data = json.loads(s)
        if isinstance(data, list):
            out = []
            for u in data:
                u = _safe_str(u).strip()
                if u:
                    out.append(u)
            return out
    except Exception:
        pass
    # CSV'den düz string geldiyse (tek url veya virgüllü)
    if "," in s:
        return [p.strip() for p in s.split(",") if p.strip()]
    return [s]


def _build_prompt(
    title: str,
    brand: str | None,
    category_path: str | None,
    old_description: str | None,
    image_urls: Iterable[str],
) -> str:
    title = _safe_str(title).strip()
    brand = _safe_str(brand).strip()
    category_path = _safe_str(category_path).strip()
    old_description = _safe_str(old_description).strip()

    # Eski açıklama “aynen” üstte zorunlu. Varsa değiştirmeden koyduruyoruz.
    old_section = ""
    if old_description:
        old_section = (
            "<strong>Mevcut Ürün Açıklaması</strong><br/>"
            f"{old_description}<br/><br/>"
        )

    # Görseller: Trendyol tarafında <img> bazen sorun çıkarabiliyor.
    # O yüzden URL listesini <ul><li> olarak koyuyoruz (settings.inline_images True ise).
    images_section = ""
    img_list = [u for u in image_urls if u]
    if settings.inline_images and img_list:
        items = "".join([f"<li>{u}</li>" for u in img_list])
        images_section = (
            "<strong>Ürün Görselleri (URL)</strong><br/>"
            f"<ul>{items}</ul><br/>"
        )

    # LLM’in uyacağı tek HTML tag seti:
    # <strong>, <ul>, <li>, <br/>  (validator ile uyumlu)
    # Karakter hedefi: 25k–27k
    prompt = f"""
You are an SEO content generator for Trendyol-compatible e-commerce product pages.

OUTPUT RULES (VERY IMPORTANT):
- Output MUST be valid HTML.
- Use ONLY these tags: <strong>, <ul>, <li>, <br/>
- Return ONLY the HTML. No markdown, no explanations.

HARD CONSTRAINTS:
- Do NOT use banned words (assume there is a banned-word validator).
- Avoid exaggerated marketing language.
- Do NOT repeat the same sentence or near-identical sentence structure.
- Each paragraph must add NEW semantic information (no filler).
- Total length MUST be between {settings.min_chars} and {settings.max_chars} characters.

CONTEXT:
Product title: "{title}"
Brand: "{brand}"
Category path: "{category_path}"

MANDATORY ORDER:
1) If an old description exists, include it FIRST verbatim under the heading "Mevcut Ürün Açıklaması".
2) Then write a NEW SEO description under the heading "Yeni SEO Açıklaması".
3) If image urls are provided and inline_images is enabled, include them at the END as a bullet list.

CONTENT PLAN (FOLLOW):
- <strong>Yeni SEO Açıklaması</strong>
- <strong>Ürün Genel Tanımı</strong> (neutral, factual)
- <strong>Kullanım Alanları ve Senaryolar</strong> (many scenarios, all different)
- <strong>Öne Çıkan Özellikler</strong> (bullet list; each bullet different)
- <strong>Malzeme / Doku / Kesim / Kalıp</strong> (category-relevant; if unknown, write safe general guidance)
- <strong>Beden/Ölçü Rehberi ve Uyum</strong> (avoid absolute claims)
- <strong>Bakım, Temizlik ve Uzun Ömür</strong> (practical steps)
- <strong>Kombin ve Stil Önerileri</strong> (varied, category-specific)
- <strong>Hediye ve Kullanıcı Profilleri</strong> (varied)
- <strong>Sık Sorulan Sorular</strong> (Q&A; each answer adds new info)

SEO GUIDANCE:
- Use natural synonyms and related phrases instead of repeating the same keywords.
- Use category-specific terms derived from "{category_path}".
- Do not keyword-stuff. Keep it readable.
- Do not over-repeat the product title.

HERE IS THE OLD DESCRIPTION SECTION (if any). DO NOT MODIFY IT:
{old_section}

IF inline images are enabled, add this section at the end:
{images_section}

Now produce the final HTML with the required length and constraints.
""".strip()

    return prompt


def _normalize_html(html: str) -> str:
    # Bazı modeller <br> üretebiliyor; standartla.
    html = html.replace("<br>", "<br/>")
    # Boşlukları aşırı şişirmesin.
    html = re.sub(r"[ \t]+\n", "\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def generate_html_llm(
    title: str,
    brand: str | None,
    category_path: str | None,
    old_description: str | None,
    image_urls_json: str | None = None,
    model: str | None = None,
) -> str:
    """
    LLM ile HTML üretir.
    - Quota / auth / rate-limit gibi hatalarda stub generator'a düşer (sistem bozulmasın diye).
    - settings.min_chars / settings.max_chars aralığını hedefler.
    """
    image_urls = _parse_image_urls(image_urls_json)

    prompt = _build_prompt(
        title=title,
        brand=brand,
        category_path=category_path,
        old_description=old_description,
        image_urls=image_urls,
    )

    client = get_client()
    use_model = model or getattr(settings, "llm_model", None) or "gpt-4.1-mini"

    # 2 deneme: ilk üretim + gerekirse “uzat ama tekrar etme” düzeltmesi
    # (Validator zaten son sözü söyleyecek; burada sadece hedef aralığına yaklaşmaya çalışıyoruz.)
    try:
        resp = client.responses.create(
            model=use_model,
            input=[
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]}
            ],
        )
        html = _normalize_html(getattr(resp, "output_text", "") or "")
        if not html:
            # Boş döndüyse stub’a düş.
            return generate_html_stub(title, brand, category_path, old_description, image_urls_json)

        # Çok kısa kaldıysa bir kez “genişlet” iste.
        if len(html) < settings.min_chars:
            delta = settings.min_chars - len(html)
            fix_prompt = f"""
You previously generated HTML but it is too short by approximately {delta} characters.

RULES:
- Keep the existing HTML exactly as-is at the beginning.
- Append NEW sections and NEW sentences only (no repetition).
- Use ONLY <strong>, <ul>, <li>, <br/> tags.
- Do NOT use banned words.
- Reach total length between {settings.min_chars} and {settings.max_chars} characters.

EXISTING HTML (DO NOT EDIT, ONLY APPEND):
{html}

Now append new, non-repetitive content to reach the target length.
""".strip()

            resp2 = client.responses.create(
                model=use_model,
                input=[
                    {"role": "user", "content": [{"type": "input_text", "text": fix_prompt}]}
                ],
            )
            html2 = _normalize_html(getattr(resp2, "output_text", "") or "")
            if html2:
                html = html2

        # Fazla uzunsa güvenli kırp (validator max_chars kontrolü var)
        if len(html) > settings.max_chars:
            html = html[: settings.max_chars - 3] + "..."

        return html

    except (RateLimitError, AuthenticationError) as e:
        # RateLimit: quota/429 vb. — demo/production için stub’a düşmek mantıklı.
        return generate_html_stub(title, brand, category_path, old_description, image_urls_json)

    except (APITimeoutError, APIConnectionError) as e:
        # Bağlantı sorunları: stub
        return generate_html_stub(title, brand, category_path, old_description, image_urls_json)

    except (BadRequestError, OpenAIError) as e:
        # Prompt hatası vs. — yine stub (pipeline kırılmasın)
        return generate_html_stub(title, brand, category_path, old_description, image_urls_json)
