# Prompt for Antigravity — Darukaa.Earth Biodiversity Chatbot

Paste everything below into Antigravity as your project kickoff prompt. `PRD_Biodiversity_Intelligence_Chatbot.md` should be in the same folder/workspace so the agent can read it.

---

## PROMPT START

I'm building a hackathon project. The full requirements are in `PRD_Biodiversity_Intelligence_Chatbot.md` in this workspace — **read that file completely before writing any code.**

### Project
An AI Biodiversity Intelligence Chatbot: a RAG-based conversational system that reasons about soil, biodiversity, climate, land use, and human-impact data, and produces evidence-backed, multi-metric recommendations. Full functional/non-functional requirements, data model, API contract, and acceptance criteria are all in the PRD — follow it as the source of truth. Do not simplify away any of its "mandatory" requirements (structured knowledge base, evidence-backed recommendations, multi-metric reasoning, conversational memory).

### Fixed tech choices (do not substitute these)
- **LLM / reasoning:** Groq API (use `langchain-groq`'s `ChatGroq` client). Use a strong currently-available Groq-hosted model — check Groq's model list at build time and pick their best general-purpose instruction model (e.g. a Llama 3.x / Llama 4 model on Groq); make the model name a config value, not hardcoded, so I can swap it.
- **Embeddings:** open-source, run locally, no external API cost — use `sentence-transformers` with `BAAI/bge-small-en-v1.5` (or `all-MiniLM-L6-v2` if you want smaller/faster). Wrap it as a LangChain-compatible embeddings class.
- **Vector store / DB:** PostgreSQL + `pgvector` extension.
- **Orchestration:** LangChain + LangGraph, matching the graph design in the PRD (Extract Metrics → Completeness Check → [loop for clarifying question] → Retrieve → Multi-Metric Reasoning → Recommendation Generator → Format Output).
- **Backend:** Python + FastAPI, matching the API contract in the PRD (`/chat` and `/chat/json`).
- **Deployment target:** Docker Compose locally (Postgres+pgvector container + app container). Keep it deployable to Render/Railway later, but local-first for now.
- **Env vars:** `GROQ_API_KEY`, `DATABASE_URL`, `EMBEDDING_MODEL_NAME`, `GROQ_MODEL_NAME` — put these in `.env.example`, never hardcode secrets.

### Critical working instruction: maintain a PROGRESS.md file

Because this build will span multiple sessions and you (the AI agent) do not retain memory between them, you must maintain a file called `PROGRESS.md` at the project root, and treat it as your own working memory:

1. **Before starting any work in a session**, read `PROGRESS.md` first (if it exists) to recall exactly where the project stands, what decisions were already made, and what's next. Do not re-derive architecture decisions already logged there — treat them as settled unless I explicitly tell you to change them.
2. **After completing any meaningful unit of work** (a milestone, a file, a working feature, a bug fix, or a decision I gave you), update `PROGRESS.md` immediately with:
   - What was just completed
   - Which PRD milestone (M1–M8) this maps to
   - Any deviations from the PRD and why
   - Any open questions/blockers
   - The exact next step to pick up with
3. Structure `PROGRESS.md` like this and keep it current (don't just append forever — update the status table in place, and keep a short changelog below it):

```markdown
# Project Progress

## Status Summary
| Milestone | Status | Notes |
|---|---|---|
| M1 - Infra (docker-compose, pgvector working) | Not started / In progress / Done | |
| M2 - Knowledge base ingested | | |
| M3 - Core LangGraph happy path | | |
| M4 - Conversational loop + memory | | |
| M5 - Structured JSON input | | |
| M6 - Output format enforcement | | |
| M7 - Deploy + README | | |
| M8 - Stretch (geo input, confidence tuning) | | |

## Current State
[1-2 paragraphs: what works right now if you ran the app today]

## Key Decisions Log
- [Date] Chose X over Y because Z
- ...

## Known Issues / Blockers
- ...

## Next Step
[The single next concrete action to take]

## Changelog
- [Date/session] Did X, Y, Z
```

4. If you ever have to make an architecture or scope decision not explicitly covered in the PRD, make a reasonable choice, log it under "Key Decisions Log," and keep going rather than stalling to ask me — unless it's something expensive or hard to reverse (e.g. changing the DB or LLM provider), in which case flag it clearly and ask.

### Build order

Follow the milestone order from the PRD Section 12 (M1 → M8). Do not jump to polishing output formatting before the core RAG + reasoning pipeline actually retrieves and reasons over real ingested content — that's the part being evaluated most heavily (55% of the hackathon score is reasoning depth + scientific grounding).

For the knowledge base (M2), source 5–10 real documents/reports from FAO, IPCC, IPBES, CBD, or UNEP covering soil, land use, biodiversity, climate, and human impact, chunk them (~500–800 tokens), embed with the local embedding model, and load into `knowledge_chunks` per the schema in the PRD. Never let the LLM fabricate a citation — only cite sources that are actually in the ingested knowledge base.

### First deliverable

Start with M1: scaffold the repo structure exactly as laid out in PRD Section 9, set up `docker-compose.yml` with Postgres+pgvector, confirm the embedding model and Groq client both work with a trivial test script, create `PROGRESS.md` with the status table above (all "Not started" except M1 which you're now working on), and report back what's done.

## PROMPT END
