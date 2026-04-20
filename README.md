# Trendyol SEO AI — LLM-Powered Product Description Generator

An end-to-end automation pipeline that fetches product data from the Trendyol Seller API and generates SEO-optimized, platform-compliant product descriptions using Large Language Models.

## Problem

Manual product description writing does not scale for large catalogs. Uncontrolled AI output can violate platform rules. Direct automated publishing carries operational risk.

## Solution

A controlled, auditable pipeline with human approval before any content goes live.

## Pipeline
Trendyol Seller API → Fetch Products → Normalize → Rule-Based Filter → LLM (OpenAI) → SEO Description → Excel Report

## Features

- Fetches live product data via Trendyol Seller API
- Rule-based filtering: prohibited terms, length limits, exaggerated claims
- LLM-generated SEO-optimized descriptions
- Retry mechanism and rate limit handling
- Excel output comparing old vs. new descriptions
- Human approval required before publishing — safe by design

## Stack

Python · OpenAI API · Trendyol Seller API · Pandas · OpenPyXL

## Setup

1. Clone the repo
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Copy `.env.example` to `.env` and fill in:
   TRENDYOL_API_KEY=...
  TRENDYOL_API_SECRET=...
  TRENDYOL_SUPPLIER_ID=...
  OPENAI_API_KEY=...

4. Run:
```bash
   python main_fetch_products.py
```

## Output

| File | Content |
|------|---------|
| `products_raw.xlsx` | Original descriptions from Trendyol |
| `products_with_ai.xlsx` | Original + AI-generated descriptions + status (OK/FAIL) |

## Design Decisions

AI-generated descriptions are **not** automatically published to Trendyol. All output is reviewed by a human before going live. This is intentional — to ensure platform compliance and eliminate operational risk.
