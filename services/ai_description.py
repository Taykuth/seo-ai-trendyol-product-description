from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI()

# Yasaklı kelimeler (gerektikçe genişletilebilir)
BANNED_WORDS = [
    "en iyi", "%100", "garanti", "mucize", "kesin",
    "hastalık", "tedavi", "vaat", "iddia", "bedava"
]


def violates_rules(text: str) -> bool:
    """
    Kurallara aykırıysa True döner
    """
    if not text:
        return True

    t = text.lower()

    # HTML guard
    if "<" in t or ">" in t:
        return True

    # Yasaklı kelimeler
    for w in BANNED_WORDS:
        if w in t:
            return True

    # Çok kısa açıklama guard
    if len(text.split()) < 100:
        return True

    return False


def generate_description(product: dict) -> str:
    """
    Tek seferlik AI açıklama üretir
    """
    prompt = f"""
Ürün Bilgileri
- Ürün Adı: {product.get('title')}
- Marka: {product.get('brand')}
- Kategori: {product.get('category')}

Amaç
- Trendyol için SEO uyumlu, doğal ve güven veren bir ürün açıklaması üret.

Kurallar (zorunlu)
- HTML, emoji ve madde işareti kullanma.
- Tıbbi, tedavi edici, kesin sonuç vaat eden ifadeler kullanma.
- Aşağıdaki kelimeleri KULLANMA: {", ".join(BANNED_WORDS)}
- 120–160 kelime aralığında yaz.
- Türkçe yaz; sade, akıcı ve profesyonel bir ton kullan.
- Abartı yok; ölçülü fayda anlatımı.
- Rakip, fiyat, kampanya, “en iyi”, “%100”, “garanti” gibi iddialar yok.

İçerik Yapısı
1) İlk paragraf: Ürünün ne olduğu ve kime uygun olduğu.
2) Orta paragraf: Öne çıkan özellikler ve kullanım deneyimi.
3) Son paragraf: Kullanım rutini ve günlük fayda.

Çıktı
- Sadece yeni ürün açıklaması (düz metin).
""".strip()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=350,
        temperature=0.6,
    )

    return response.output_text.strip()


def generate_with_retry(product: dict, max_retries: int = 2) -> tuple[str, str]:
    """
    Kurallara uymuyorsa tekrar dener.
    Döner: (new_description, status)
    status: OK | FAIL
    """
    last_text = ""

    for attempt in range(max_retries + 1):
        text = generate_description(product)
        last_text = text

        if not violates_rules(text):
            return text, "OK"

    return last_text, "FAIL"
