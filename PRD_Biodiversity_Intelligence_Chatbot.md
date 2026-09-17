# Product Requirements Document (PRD)
## Darukaa.Earth Hackathon — AI Biodiversity Intelligence Chatbot

**Version:** 1.0
**Author:** Hariharan Malwad
**Purpose of this document:** Defines what to build, why, and how, so that both a human developer and an AI coding assistant can implement this project with minimal ambiguity.

---

## 1. Background & Problem Statement

Darukaa.Earth operates in climate-tech / nature finance, and needs AI systems that reason about biodiversity and environmental data — not generic chatbots. The hackathon asks us to build a system that behaves like an **AI environmental scientist**: given information about a piece of land (soil, climate, land use, biodiversity indicators), it should diagnose issues and produce **specific, scientifically-grounded, multi-variable recommendations** to improve biodiversity outcomes.

This is explicitly **not** a UI showcase and **not** a "wrap GPT in a chat window" project. The core evaluation is on reasoning depth, scientific grounding, and knowledge-system design (75% of the grading rubric combined).

---

## 2. Goals

1. Build a working RAG-based conversational system with a real, queryable knowledge base (not just prompt engineering).
2. Generate recommendations that are non-obvious, causally explained, quantified, and cited.
3. Reason across ≥3 environmental variables simultaneously (soil ↔ biodiversity ↔ water ↔ land use ↔ climate).
4. Support multi-turn conversation with memory and clarifying questions.
5. Accept both free text and structured (JSON) input.
6. Produce clearly structured output (recommendation, impacted metrics, time horizon, confidence).
7. Ship a working demo + clean repo + README in time for submission (72-hour window).

## 3. Non-Goals (Out of Scope)

- Polished / elaborate frontend UI. A minimal chat interface (or even API + simple HTML form) is sufficient.
- Mobile app.
- User authentication / multi-tenant accounts.
- Real-time satellite or IoT data ingestion (bonus only, not required).
- Fine-tuning a custom model (prompt engineering + RAG is sufficient; do not over-invest here).

---

## 4. Users & Use Case

**Primary user:** A landowner, farmer, or land-restoration project manager describing the condition of their land and seeking science-backed interventions to improve biodiversity.

**Example interaction:**
> User: "Biodiversity is declining on my land."
> System: "Can you share your soil organic carbon %, rainfall pattern, and current land use / crop type?"
> User: "Soil organic carbon is 0.3%, rainfall is low, and I grow monoculture wheat in a semi-arid region."
> System: Produces a structured recommendation (e.g. agroforestry/intercropping) with mechanism, quantified impact, metrics affected, time horizon, and citation.

---

## 5. Functional Requirements

### FR1 — Knowledge Base (Critical, weighted heaviest indirectly)
- Must ingest real reference material covering:
  - Soil health (pH, organic carbon, moisture)
  - Land use / land cover
  - Biodiversity indicators (species richness, habitat diversity)
  - Climate factors (temperature, rainfall)
  - Human impact (pollution, deforestation)
- Source documents: FAO, IPCC, IPBES, CBD, UNEP reports/briefs (5–10 documents is sufficient for the hackathon scope).
- Documents are chunked (~500–800 tokens), embedded, and stored in a vector database.
- Retrieval must be demonstrably used in generating each answer (not decorative).

### FR2 — Conversational Intelligence
- Multi-turn conversation with persisted memory per session.
- If the user's input lacks sufficient structured metrics (fewer than 3 relevant variables known), the system asks a targeted clarifying question instead of guessing.
- Once enough metrics are known, the system proceeds to reasoning + recommendation.
- Context (previously stated metrics) must persist and be reused across turns — do not re-ask for information already provided.

### FR3 — Evidence-Backed Recommendations (Mandatory)
Every recommendation returned to the user must include, at minimum:
| Field | Description | Example |
|---|---|---|
| Intervention | The specific action | "Introduce legume-based cover crops" |
| Mechanism | Why it works, scientifically | "Nitrogen fixation increases microbial activity and organic matter turnover" |
| Impacted metric(s) | Which measurable variable(s) improve | Soil organic carbon, pollinator diversity |
| Expected improvement | Quantified where possible | "~15–25% increase in SOC over 2–3 years" |
| Time horizon | short / medium / long term | Medium term |
| Citation | Real source | FAO / IPCC / named study |
| Confidence (optional) | Qualitative or numeric | High / Medium / Low |

Generic advice (e.g. "use sustainable practices") is an explicit failure condition per the challenge brief and must never be output.

### FR4 — Multi-Metric Reasoning
- The reasoning step must explicitly connect at least 2 relationships among: soil health, biodiversity, water availability, land use, climate, human impact.
- Single-variable answers (e.g. only discussing soil with no downstream biodiversity/water link) are non-compliant with the brief.

### FR5 — Input Handling
- **Text input** (mandatory): free-form natural language.
- **Structured input** (mandatory): JSON payload with fields such as `soil_organic_carbon`, `rainfall`, `land_use`, `region_type`, etc.
- **Bonus:** geo-coordinates (lat/long) accepted as optional context, potentially used to infer regional climate norms.

### FR6 — Output Format
Every final response must clearly separate:
- Recommendation (text)
- Impacted metrics (list)
- Time horizon (enum: short/medium/long)
- Confidence (optional)
- Supporting citation(s)

Output should be structured (JSON internally, rendered as readable text/cards in the chat UI).

---

## 6. Non-Functional Requirements

- **Explainability:** Every claim traceable to a retrieved knowledge chunk or curated recommendation record — no hallucinated citations.
- **Reproducibility:** `docker-compose up` should bring up DB + app locally with minimal manual steps.
- **Performance:** Response latency is not scored directly, but should be reasonable for a live demo (< ~15s per turn).
- **Code quality:** Clean, modular repo structure (see Section 9) since reviewers will read the code, not just the demo.

---

## 7. System Architecture

```
                     ┌─────────────────────┐
   User (text/JSON) →│   FastAPI /chat      │
                     └──────────┬──────────┘
                                ▼
                     ┌─────────────────────┐
                     │   LangGraph Flow     │
                     └──────────┬──────────┘
        ┌───────────────────────┼─────────────────────────┐
        ▼                       ▼                          ▼
 Extract Metrics Node   Completeness Check Node    (loop if incomplete)
        │                       │
        │                       ▼ (if complete)
        │              Retrieve Node (pgvector similarity search)
        │                       │
        │                       ▼
        │           Multi-Metric Reasoning Node
        │                       │
        │                       ▼
        │           Recommendation Generator Node
        │                       │
        │                       ▼
        │             Format Output Node
        │                       │
        └───────────────────────┴──────────────► Response to user
```

**Tech stack:**
- Backend: Python, FastAPI
- Orchestration: LangChain + LangGraph
- Vector store: PostgreSQL + pgvector
- Embeddings: `text-embedding-3-small` (OpenAI) or `bge-small-en` (open-source, no API cost)
- LLM: GPT-4o-mini / Claude Sonnet / any capable chat model via API
- Deployment: Render / Railway / GCP Cloud Run
- CI/CD: GitHub Actions (lint + basic tests on push)

---

## 8. Data Model

```sql
-- Knowledge base chunks (RAG source material)
CREATE TABLE knowledge_chunks (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),        -- 'soil' | 'biodiversity' | 'climate' | 'land_use' | 'human_impact'
    source_title TEXT,
    source_url TEXT,
    content TEXT,
    embedding VECTOR(1536)
);

-- Curated evidence-backed recommendation templates (optional seed layer)
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    intervention TEXT,
    mechanism TEXT,
    impacted_metrics TEXT[],
    expected_improvement TEXT,
    time_horizon VARCHAR(20),
    citation TEXT,
    source_chunk_id INT REFERENCES knowledge_chunks(id)
);

-- Conversation sessions
CREATE TABLE conversations (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT now()
);

-- Individual turns + accumulated structured context
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES conversations(session_id),
    role VARCHAR(10),            -- 'user' | 'assistant'
    content TEXT,
    extracted_metrics JSONB,     -- running structured state for this session
    created_at TIMESTAMP DEFAULT now()
);
```

---

## 9. Repository Structure

```
darukaa-biodiversity-ai/
├── app/
│   ├── main.py            # FastAPI entrypoint, /chat and /chat/json routes
│   ├── graph.py            # LangGraph node + edge definitions
│   ├── retrieval.py         # pgvector similarity search logic
│   ├── ingestion.py          # one-off script: chunk + embed + load source docs
│   ├── models.py              # SQLAlchemy models + Pydantic schemas
│   ├── prompts.py               # prompt templates for each node
│   └── config.py                  # env vars, DB connection, API keys
├── data/
│   └── sources/                     # raw source PDFs/reports used for ingestion
├── tests/
│   └── test_graph.py
├── .github/workflows/ci.yml         # lint + test on push
├── docker-compose.yml                # postgres+pgvector + app service
├── requirements.txt
├── .env.example
└── README.md
```

---

## 10. API Contract (minimum viable)

**POST `/chat`**
Request:
```json
{ "session_id": "uuid-or-null", "message": "Biodiversity is declining on my land" }
```
Response:
```json
{
  "session_id": "uuid",
  "reply_type": "clarifying_question" ,
  "message": "Can you share soil organic carbon %, rainfall pattern, and land use type?"
}
```

**POST `/chat/json`**
Request:
```json
{
  "session_id": "uuid-or-null",
  "metrics": {
    "soil_organic_carbon": 0.3,
    "rainfall": "low",
    "land_use": "monoculture wheat",
    "region_type": "semi-arid"
  }
}
```
Response:
```json
{
  "session_id": "uuid",
  "reply_type": "recommendation",
  "recommendations": [
    {
      "intervention": "Introduce agroforestry / intercropping",
      "mechanism": "Tree-crop integration increases root biomass and organic matter input, improving soil structure and microhabitat diversity",
      "impacted_metrics": ["soil_organic_carbon", "species_richness"],
      "expected_improvement": "Soil organic carbon +10-20% over 3 years",
      "time_horizon": "medium",
      "citation": "FAO Agroforestry and Land Restoration Guidelines",
      "confidence": "high"
    }
  ]
}
```

---

## 11. Evaluation Rubric Mapping (build priorities)

| Rubric criterion | Weight | PRD sections that satisfy it |
|---|---|---|
| Depth of reasoning | 30% | FR3, FR4, Section 7 (Reasoning Node) |
| Scientific grounding | 25% | FR1, FR3, Section 8 (citation fields) |
| Knowledge system design | 20% | FR1, Section 7 (Retrieve Node), Section 8 |
| Conversational intelligence | 15% | FR2, Section 7 (Completeness Check loop) |
| Output clarity | 10% | FR6, Section 10 |

**Implication for build order:** prioritize the RAG pipeline and multi-metric reasoning quality over UI polish. A CLI or bare API + Postman/curl demo is acceptable if reasoning quality is high.

---

## 12. Build Milestones

1. **M1 — Infra:** Postgres + pgvector running via docker-compose; one document embedded and retrievable via similarity search.
2. **M2 — Knowledge base:** 5–10 source documents ingested across all 5 categories (FR1).
3. **M3 — Core graph (happy path):** Extract → Retrieve → Reason → Recommend → Format, working end-to-end for a single complete input.
4. **M4 — Conversational loop:** Completeness check + clarifying question loop + persisted session memory (FR2).
5. **M5 — Structured input:** `/chat/json` endpoint accepting direct metrics (FR5).
6. **M6 — Output polish:** Enforce structured output schema on every response (FR6).
7. **M7 — Deploy + document:** Deploy demo, write README (architecture, schema, setup, CI/CD), push CI pipeline.
8. **M8 (stretch):** Geo-coordinate input, confidence scoring refinement.

---

## 13. Acceptance Criteria (Definition of Done)

- [ ] System refuses to answer with fewer than 3 known environmental variables — it asks a clarifying question instead.
- [ ] Every recommendation includes intervention, mechanism, impacted metric(s), quantified improvement (where evidence supports it), time horizon, and a real citation.
- [ ] At least one response demonstrably connects ≥2 variable relationships (e.g. soil ↔ biodiversity ↔ water).
- [ ] Retrieval step is visible/traceable in logs or response metadata (proves RAG is real, not decorative).
- [ ] Both text and JSON input paths work.
- [ ] Conversation memory persists across at least 3 turns in the same session.
- [ ] Repo runs locally via `docker-compose up` with instructions in README.
- [ ] CI pipeline runs on push (lint/tests, even minimal).
- [ ] Live demo URL is reachable (if deployed).

---
