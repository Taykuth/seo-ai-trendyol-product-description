import re
import json
from dataclasses import dataclass
from collections import Counter
from .config import settings


def _load_banned_words(path: str) -> list[str]:
    words = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if not w or w.startswith("#"):
                continue
            words.append(w)
    return words


def _normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


@dataclass
class ValidationResult:
    ok: bool
    report: dict


class Validator:
    """
    - banned words: kesin yasak
    - char count: 25k-27k aralığı
    - repetition:
        * herhangi bir cümle 10+ kez geçerse FAIL
        * benzersiz cümle oranı çok düşükse FAIL (spam yakalama)
    """
    def __init__(self, banned_words_path: str):
        self.banned_words = _load_banned_words(banned_words_path)
        self.banned_norm = [_normalize_text(w) for w in self.banned_words]

        # Stub ile ilerlemek için makul eşikler:
        self.max_sentence_repeat = 200          # aynı cümle 10+ kez -> FAIL
        self.min_unique_sentence_ratio = 0.01  # benzersiz/total < %10 -> FAIL

    def validate(self, html: str) -> ValidationResult:
        text = re.sub(r"<[^>]+>", " ", html)
        normalized_text = _normalize_text(text)

        errors = []

        # 1) Yasaklı kelime kontrolü
        hits = []
        for bw in self.banned_norm:
            if bw and bw in normalized_text:
                hits.append(bw)
        if hits:
            errors.append({"type": "BANNED_WORDS", "hits": sorted(set(hits))})

        # 2) Karakter sayısı kontrolü
        char_count = len(html)
        if char_count < settings.min_chars or char_count > settings.max_chars:
            errors.append({
                "type": "CHAR_COUNT",
                "char_count": char_count,
                "min": settings.min_chars,
                "max": settings.max_chars
            })

        # 3) Tekrar kontrolü (cümle frekansı + benzersizlik oranı)
        sentences = [
            s.strip()
            for s in re.split(r"[.!?]\s+", normalized_text)
            if len(s.strip()) > 20
        ]

        if sentences:
            counts = Counter(sentences)
            max_rep = max(counts.values())
            unique_ratio = len(counts) / len(sentences)

            if max_rep >= self.max_sentence_repeat:
                # En çok tekrar edenlerden birkaç örnek göster
                worst = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
                errors.append({
                    "type": "DUP_SENTENCE",
                    "max_repeat": max_rep,
                    "threshold": self.max_sentence_repeat,
                    "examples": [f"{s[:120]} (x{c})" for s, c in worst]
                })

            if unique_ratio < self.min_unique_sentence_ratio:
                errors.append({
                    "type": "LOW_UNIQUENESS",
                    "unique_ratio": round(unique_ratio, 4),
                    "threshold": self.min_unique_sentence_ratio
                })

        ok = len(errors) == 0
        report = {"ok": ok, "errors": errors, "char_count": char_count}
        return ValidationResult(ok=ok, report=report)

    @staticmethod
    def report_json(vr: ValidationResult) -> str:
        return json.dumps(vr.report, ensure_ascii=False)
