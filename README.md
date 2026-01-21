# SEO Tabanlı Ürün Açıklaması Üretim Sistemi

Bu proje, e-ticaret platformları (özellikle Trendyol) için **SEO uyumlu, HTML formatında ürün açıklamaları** üreten uçtan uca bir otomasyon sistemidir.

Sistem; CSV ile ürün verisi alır, büyük dil modeli (LLM) ile içerik üretir, kurallara göre doğrular ve sonucu kayıt altına alır.

---

## Projenin Amacı

- Ürün açıklamalarını otomatik üretmek  
- SEO kurallarına uyumu garanti altına almak  
- Trendyol HTML standartlarıyla %100 uyum sağlamak  
- Tekrarlı, yasaklı veya düşük kaliteli içerikleri engellemek  
- Mevcut sistemlere **kolay entegre edilebilir** bir yapı sunmak  

---

## Temel Özellikler

- CSV tabanlı ürün aktarımı  
- Trendyol uyumlu HTML çıktı (`<strong>`, `<ul>`, `<li>`, `<br/>`)  
- LLM (Large Language Model) destekli içerik üretimi  
- Yasaklı kelime kontrolü  
- Tekrarlı cümle tespiti  
- Minimum / maksimum karakter kontrolü  
- PASS / FAIL doğrulama mekanizması  
- Hata durumunda otomatik **fallback (stub generator)**  
- Versiyonlu çıktı kaydı  

---

## Proje Yapısı
app/
├─ ingest.py # CSV → veritabanı aktarımı
├─ pipeline.py # Uçtan uca çalıştırma
├─ run_batch.py # Toplu üretim mantığı
├─ generator_llm.py # LLM tabanlı HTML üretimi
├─ generator_stub.py # Yedek (fallback) üretici
├─ validator.py # SEO ve içerik doğrulama
├─ models.py # Veritabanı modelleri
├─ db.py # DB bağlantısı
data/
├─ input_products.csv
├─ banned_words.txt

---

## Kurulum

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main_fetch_products.py

