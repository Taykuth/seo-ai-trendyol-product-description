# Trendyol için Yapay Zeka Tabanlı SEO Uyumlu Ürün Açıklaması Üretim Sistemi

Bu proje, Trendyol Seller API üzerinden bir markaya ait ürün verilerini çekerek, büyük dil modelleri (LLM) kullanımıyla SEO uyumlu ve platform kurallarına uygun yeni ürün açıklamaları üreten uçtan uca bir otomasyon sistemidir. Proje, bitirme projesi kapsamında akademik ve mühendislik odaklı olarak geliştirilmiştir.

## Projenin Amacı

E-ticaret platformlarında ürün açıklamaları çoğu zaman SEO açısından yetersiz, tekrarlı ve manuel olarak üretildiği için zaman alıcıdır. Bu çalışmanın amacı; Trendyol’daki mevcut ürün açıklamalarını otomatik olarak analiz etmek, yapay zeka yardımıyla SEO uyumlu yeni açıklamalar üretmek ve eski–yeni açıklamaları karşılaştırmalı şekilde sunmaktır.

## Problem Tanımı

Büyük ürün kataloglarında manuel açıklama üretimi ölçeklenebilir değildir. Yapay zeka çıktıları kontrolsüz bırakıldığında platform kurallarına aykırı içerikler oluşabilir. Ayrıca canlı sistemlere doğrudan otomatik yazım operasyonel riskler taşır. Bu proje, bu problemlere kontrollü, denetlenebilir ve güvenli bir çözüm sunar.

## Önerilen Çözüm

Geliştirilen sistem aşağıdaki adımlardan oluşan bir veri işleme hattı (pipeline) sunar:
1. Trendyol Seller API üzerinden ürün verilerinin çekilmesi  
2. Ürün bilgilerinin normalize edilmesi  
3. Kural tabanlı filtreleme (yasaklı kelimeler, iddialı ifadeler, uzunluk sınırları)  
4. Büyük dil modeli (OpenAI) ile SEO uyumlu açıklama üretimi  
5. Rate limit ve hata yönetimi (retry mekanizması)  
6. Eski ve yeni açıklamaların Excel formatında raporlanması  

## Sistem Mimarisi

Trendyol Seller API → Ürün Verisi → Normalizasyon → Kural Tabanlı Filtreleme → Yapay Zeka (LLM) → SEO Uyumlu Açıklama → Excel Çıktı

## Proje Yapısı

SEO-based-product-description/  
├── config/ (API ve yapılandırma dosyaları)  
├── services/ (Trendyol API ve AI servisleri)  
├── outputs/ (Üretilen Excel çıktıları)  
├── .env.example (Ortam değişkenleri örneği)  
├── main_fetch_products.py (Ana çalıştırma dosyası)  
├── requirements.txt (Gerekli Python paketleri)  
└── README.md  

## Kurulum

Ön koşul olarak Python 3.10 veya üzeri gereklidir.

Gerekli paketlerin kurulması:
pip install -r requirements.txt

Ortam değişkenlerinin ayarlanması için `.env.example` dosyası kopyalanarak `.env` olarak adlandırılır ve aşağıdaki bilgiler girilir:

TRENDYOL_API_KEY=...  
TRENDYOL_API_SECRET=...  
TRENDYOL_SUPPLIER_ID=...  

OPENAI_API_KEY=...

## Projenin Çalıştırılması

python main_fetch_products.py

## Üretilen Çıktılar

Çalıştırma sonrası `outputs/` klasörü altında iki temel çıktı üretilir:

products_raw.xlsx  
→ Trendyol’dan çekilen orijinal ürün açıklamaları

products_with_ai.xlsx  
→ Orijinal açıklamalar  
→ Yapay zeka ile üretilmiş yeni açıklamalar  
→ ai_status bilgisi (OK / FAIL)

Bu yapı sayesinde eski ve yeni açıklamalar doğrudan karşılaştırılabilir.

## Bilinçli Tasarım Kararları

Yapay zeka ile üretilen açıklamalar Trendyol’a otomatik olarak yazılmamaktadır. Üretilen içerikler insan onayına sunulmak üzere raporlanmaktadır. Bu tercih, platform kurallarına uyum ve operasyonel risklerin önlenmesi amacıyla bilinçli olarak yapılmıştır.

## Kullanılan Teknolojiler

Python  
Trendyol Seller API  
OpenAI API (Büyük Dil Modeli)  
Pandas  
Excel (OpenPyXL)

## Sonuç

Bu proje ile gerçek bir e-ticaret problemi ele alınmış, yapay zeka kontrollü ve denetlenebilir biçimde kullanılmış ve ölçeklenebilir bir ürün açıklaması üretim sistemi geliştirilmiştir. Sistem, üretime hazır veri üretmekte ve gerçek dünya senaryolarına uygun bir mimari sunmaktadır.
