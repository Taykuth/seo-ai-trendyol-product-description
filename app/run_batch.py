from __future__ import annotations

import json
from sqlalchemy import select, func

from .config import settings
from .db import SessionLocal
from .models import Product, Generation
from .validator import Validator
from .generator_llm import generate_html_llm


def has_pass_generation(db, product_id: int) -> bool:
    q = select(func.count()).select_from(Generation).where(
        Generation.product_id == product_id,
        Generation.status == "PASS",
    )
    return db.execute(q).scalar_one() > 0


def next_version(db, product_id: int) -> int:
    q = select(func.max(Generation.version)).where(Generation.product_id == product_id)
    v = db.execute(q).scalar_one()
    return int(v or 0) + 1


def run_batch(limit: int | None = None, force: bool = False) -> dict:
    validator = Validator(settings.banned_words_path)

    with SessionLocal() as db:
        products = db.execute(select(Product)).scalars().all()
        if limit:
            products = products[:limit]

        results = {"processed": 0, "skipped": 0, "pass": 0, "fail": 0}

        for p in products:
            if (not force) and has_pass_generation(db, p.id):
                results["skipped"] += 1
                continue

            html = generate_html_llm(
    title=p.title,
    brand=p.brand,
    category_path=p.category_path,
    old_description=p.old_description,
    image_urls_json=p.image_urls_json
)


            vr = validator.validate(html)

            gen = Generation(
                product_id=p.id,
                version=next_version(db, p.id),
                prompt_hash=None,
                model_name="LLM",
                generated_html=html,
                char_count=len(html),
                status="PASS" if vr.ok else "FAIL",
                validation_report_json=json.dumps(vr.report, ensure_ascii=False),
            )

            db.add(gen)
            results["processed"] += 1
            if vr.ok:
                results["pass"] += 1
            else:
                results["fail"] += 1

        db.commit()
        return results


if __name__ == "__main__":
    # modül olarak değil direkt çalıştırırsan da çalışsın diye
    print(run_batch(limit=None, force=False))
