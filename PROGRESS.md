# Project Progress — Darukaa.Earth Biodiversity AI

## Status Summary
| Milestone | Status | Notes |
|---|---|---|
| M1 - Infra (docker-compose, pgvector working) | Done | Repo structure scaffolded, Groq API (`groq/compound`) & `BAAI/bge-small-en-v1.5` verified. |
| M2 - Knowledge base ingested | Done | Initial 5 reference documents (15 chunks) ingested & queryable. |
| M2.5 - Knowledge base expansion | Done | Expanded knowledge base with 11 new sources (PDFs & TXTs). 95 unique chunks across urban, tropical, semi-arid, temperate scenarios. |
| M3 - Core LangGraph happy path | Not started / Next | Build LangGraph state machine: Extract Metrics → Completeness Check → Retrieve → Multi-Metric Reason → Recommendation Generator → Format Output. |
| M4 - Conversational loop + memory | Not started | Completeness check loop + clarifying question + memory persistence. |
| M5 - Structured JSON input | Not started | `/chat/json` endpoint. |
| M6 - Output format enforcement | Not started | Output schema validation. |
| M7 - Deploy + README | Not started | Documentation and local deployment guide. |
| M8 - Stretch (geo input, confidence tuning) | Not started | Geo coordinates support. |

## Current State
Milestones M1, M2, and M2.5 are complete!
- **M1**: Scaffolded repo structure, `.env`, `.env.example`, `docker-compose.yml`, `requirements.txt`. Verified Groq API (`groq/compound`) and local embedding model (`BAAI/bge-small-en-v1.5`).
- **M2**: Initial knowledge base curation & vector retrieval system (`app/ingestion.py`, `app/retrieval.py`).
- **M2.5**: Knowledge Base Expansion. Enhanced `app/ingestion.py` with PDF text extraction (`pypdf`), redundancy filtering (cosine similarity threshold 0.88), and metadata tagging (`confidence`, `biome`, `category`). Ingested Project Drawdown (Nutrient Management & Annual Cropping), FAO SWSR 2026, ICRAF Sri Lanka Tropical Agroforestry Guidelines, IPBES Asia-Pacific Assessment, and USDA NRCS Urban Soil Technical Notes.

## Knowledge Base Metrics & Coverage (M2.5)
- **Total Unique Chunks Ingested**: 95 unique chunks
- **Total Redundant Chunks Skipped**: 52 chunks (e.g. `TN 470-SH-19 Soil Health Principles.pdf` and near-duplicate general principles)

### Category Breakdown
- `human_impact`: 84 chunks
- `soil`: 11 chunks
- `biodiversity`: Included
- `land_use`: Included
- `climate`: Included

### Biome / Scenario Breakdown
- `urban`: 54 chunks
- `tropical`: 33 chunks
- `semi-arid`: 4 chunks
- `temperate`: 4 chunks

### Confidence Breakdown
- `high_evidence` (Contains verifiable numbers, mechanisms, or citations): 43 chunks
- `background_only` (Contextual background): 52 chunks

## Retrieval Spot-Check Results (M2.5 Verification)
1. **Query**: `"tropical agroforestry land with declining pollinators"`
   - Top Result: IPBES Global Assessment Report (Similarity: **0.7549**)
   - Rank 2: IPBES Asia-Pacific Regional Assessment (Similarity: **0.7545**)
2. **Query**: `"urban green space with compacted soil"`
   - Top Result: USDA NRCS TN 470-SH-02 Basics of Urban Soil Health (Similarity: **0.7418**)
   - Rank 2: USDA NRCS TN 470-SH-02 Basics of Urban Soil Health (Similarity: **0.7377**)
3. **Query**: `"nitrogen over-application in intensive cropland"`
   - Top Result: Project Drawdown — Improved Nutrient Management (Similarity: **0.7534**)
   - Rank 2: Project Drawdown — Improved Annual Cropping (Similarity: **0.7494**)

## Key Decisions Log
- **2026-09-16**: Selected `BAAI/bge-small-en-v1.5` for local embeddings (384-dim, open-source, lightweight).
- **2026-09-16**: Configured Groq default model to `groq/compound` via `langchain-groq`.
- **2026-09-16**: Integrated `pypdf` for parsing PDF reference documents alongside text files.
- **2026-09-16**: Added semantic redundancy filtering (similarity threshold 0.88) to prevent bloating vector store with duplicate general principles.

## Known Issues / Blockers
- None.

## Next Step
Proceed to **M3 — Core LangGraph Graph (Happy Path)**: construct the complete LangGraph state machine (`app/graph.py`) defining nodes for metric extraction, retrieval, multi-metric scientific reasoning, recommendation generation, and output formatting.

## Changelog
- **2026-09-16**: Completed M2.5 Knowledge Base Expansion. Integrated 11 new source files (PDFs & TXTs), updated `app/ingestion.py` for PDF parsing + redundancy filtering, and verified spot-check retrieval for urban, tropical, and nutrient management scenarios.
