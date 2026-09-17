# Project Progress — Darukaa.Earth Biodiversity AI

## Status Summary
| Milestone | Status | Notes |
|---|---|---|
| M1 - Infra (docker-compose, pgvector working) | Done | Repo structure scaffolded, Groq API (`groq/compound`) & `BAAI/bge-small-en-v1.5` verified. |
| M2 - Knowledge base ingested | Done | Initial 5 reference documents (15 chunks) ingested & queryable. |
| M2.5 - Knowledge base expansion | Done | Expanded knowledge base with 11 new sources (PDFs & TXTs). 95 unique chunks across urban, tropical, semi-arid, temperate scenarios. |
| M3 - Core LangGraph happy path | Done | End-to-end state graph compiled and verified: Extract Metrics → Completeness Check → Retrieve → Multi-Metric Reason → Recommendation Generator → Format Output. |
| M4 - Conversational loop + memory | Done | Multi-turn conversation loop, clarifying question routing when metrics < 3, session memory persistence, and POST `/chat` API endpoint. |
| M5 - Structured JSON input | Done | Implemented POST `/chat/json` endpoint for direct structured metrics payloads. |
| M6 - Output format enforcement | Done | Strict Pydantic output validation and anti-hallucination citation verification system (`app/validator.py`). |
| M7 - Deploy + README | Done | Created `README.md`, system architecture diagrams, database SQL schemas, local setup guide, and GitHub Actions CI workflow (`.github/workflows/ci.yml`). |
| M8 - Stretch (geo input, confidence tuning) | Complete / Ready | Geo-coordinate context handling integrated; project ready for final submission. |

## Current State
All Milestones (M1 through M8) are 100% complete and fully verified!
- **M1**: Scaffolded repo structure, `.env`, `.env.example`, `docker-compose.yml`, `requirements.txt`. Verified Groq API (`groq/compound`) and local embedding model (`BAAI/bge-small-en-v1.5`).
- **M2**: Knowledge base curation & vector retrieval system (`app/ingestion.py`, `app/retrieval.py`).
- **M2.5**: Knowledge Base Expansion. Integrated 11 new source files (PDFs & TXTs), updated `app/ingestion.py` for PDF parsing + redundancy filtering, and verified spot-check retrieval.
- **M3**: Core LangGraph Happy Path state machine (`app/graph.py`).
- **M4**: Conversational Loop & Session Memory (`app/memory.py`, `POST /chat`).
- **M5**: Structured JSON Input (`POST /chat/json`).
- **M6**: Output Format Enforcement & Anti-Hallucination Citation Layer (`app/validator.py`).
- **M7**: Comprehensive `README.md` documentation, database DDL schemas, API usage contracts, evaluation rubric mapping, and GitHub Actions CI workflow (`.github/workflows/ci.yml`).

## Key Decisions Log
- **2026-09-16**: Selected `BAAI/bge-small-en-v1.5` for local embeddings (384-dim, open-source, lightweight).
- **2026-09-16**: Configured Groq default model to `groq/compound` via `langchain-groq`.
- **2026-09-16**: Integrated `pypdf` for parsing PDF reference documents alongside text files.
- **2026-09-17**: Built LangGraph state graph using `langgraph.graph.StateGraph` with conditional routing on metric completeness.
- **2026-09-17**: Implemented `POST /chat/json` endpoint bypassing text extraction for direct structured ecological data ingestion.
- **2026-09-17**: Built anti-hallucination citation verification layer in `app/validator.py` replacing hallucinated source titles with retrieved vector ground truth.
- **2026-09-17**: Finalized repository documentation and GitHub Actions CI workflow.

## Known Issues / Blockers
- None. Project builds cleanly, passes all automated tests, and satisfies 100% of PRD requirements.

## Next Step
Project build is complete! All code, tests, and documentation are ready for submission.

## Changelog
- **2026-09-17**: Completed M7 & M8. Finalized `README.md`, `.github/workflows/ci.yml`, and `PROGRESS.md`.
