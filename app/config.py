import os
from pydantic import BaseModel

class Settings(BaseModel):
    db_url: str = os.getenv("DB_URL", "sqlite:///seo_gen.db")
    min_chars: int = int(os.getenv("MIN_CHARS", "25000"))
    max_chars: int = int(os.getenv("MAX_CHARS", "27000"))
    inline_images: bool = os.getenv("INLINE_IMAGES", "false").lower() == "true"
    banned_words_path: str = os.getenv("BANNED_WORDS_PATH", "data/banned_words.txt")

settings = Settings()
