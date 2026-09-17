# Darukaa.Earth — AI Biodiversity Intelligence Chatbot

An AI-powered RAG conversational intelligence platform that acts as an **AI Environmental Scientist**. It reasons about complex multi-variable ecological data (soil health, climate factors, water retention, land use, and human impact) to generate scientifically-grounded, multi-metric, cited ecological restoration recommendations.

Built for the **Darukaa.Earth Climate-Tech Hackathon**.

---

## 🌟 Key Features

1. **Grounded RAG Knowledge System**:
   - Ingests **95 curated reference chunks** across 16 global ecological reports (FAO, IPCC, IPBES, CBD, UNEP, Project Drawdown, USDA NRCS, ICRAF Sri Lanka).
   - Covers 4 distinct biomes/scenarios: `semi-arid`, `tropical`, `urban`, and `temperate`.
   - Embeddings run locally via `BAAI/bge-small-en-v1.5` (384-dimensional vectors, zero external API embedding cost).
2. **LangGraph Multi-Metric Reasoning Engine**:
   - Executes multi-variable causal reasoning across $\ge 3$ environmental variables simultaneously (e.g. Soil Organic Carbon $\leftrightarrow$ Moisture Retention $\leftrightarrow$ Microclimate Shade $\leftrightarrow$ Species Richness).
   - State machine architecture built using LangGraph (`StateGraph`).
3. **Anti-Hallucination Citation Verification**:
   - Pydantic output validation schema (`app/validator.py`).
   - Cross-references generated citations against retrieved vector chunks, automatically replacing hallucinated sources with verified ground truth titles.
4. **Conversational Intelligence & Memory**:
   - Persisted multi-turn session memory across chat turns.
   - Evaluates metric completeness: if user input contains $< 3$ environmental metrics, the system returns a targeted clarifying question instead of guessing.
   - Accumulates metrics across conversation turns.
5. **Dual API Input Interfaces**:
   - Free-form text endpoint (`POST /chat`).
   - Direct structured JSON metrics endpoint (`POST /chat/json`).

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    User([User Text / JSON Input]) --> API[FastAPI Entrypoint /chat & /chat/json]
    API --> Memory[Session Memory Manager app/memory.py]
    Memory --> LG[LangGraph Flow app/graph.py]
    
    subgraph LangGraph Flow
        Extract[Extract Metrics Node] --> Check{Completeness Check: Count >= 3?}
        Check -->|Metrics < 3| Clarify[Return Clarifying Question]
        Check -->|Metrics >= 3| Retrieve[Retrieve Vector Chunks app/retrieval.py]
        Retrieve --> Reason[Multi-Metric Reasoning Node]
        Reason --> Recommend[Recommendation Generator Node]
        Recommend --> Validate[Anti-Hallucination & Pydantic Validator app/validator.py]
        Validate --> Format[Format Output Node]
    end
    
    Retrieve <--> VectorStore[(PostgreSQL pgvector / Local Vector Cache)]
    Reason <--> GroqAPI[Groq LLM API: groq/compound]
    Recommend <--> GroqAPI
    
    Clarify --> Response([API JSON Response])
    Format --> Response
```

---

## 🗄️ Database Data Model

```sql
-- Knowledge base chunks (RAG source material)
CREATE TABLE knowledge_chunks (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),        -- 'soil' | 'biodiversity' | 'climate' | 'land_use' | 'human_impact'
    source_title TEXT,
    source_url TEXT,
    content TEXT,
    embedding VECTOR(384)
);

-- Evidence-backed recommendation templates (seed layer)
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

-- Turn messages & accumulated structured context
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES conversations(session_id),
    role VARCHAR(10),            -- 'user' | 'assistant'
    content TEXT,
    extracted_metrics JSONB,     -- running accumulated state
    created_at TIMESTAMP DEFAULT now()
);
```

---

## 🚀 Local Setup & Installation

### Prerequisites
- Python 3.13 (or Python $\ge$ 3.10)
- Docker & Docker Compose (optional, for PostgreSQL + `pgvector`)

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/Hariharan1645/darukaa-biodiversity-ai.git
cd darukaa-biodiversity-ai

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your Groq API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=groq/compound
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/darukaa_biodiversity
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSION=384
```

### 3. Start PostgreSQL + pgvector (Optional)
```bash
docker-compose up -d
```
*Note: If running without Docker, the application automatically operates on an in-memory vector cache (`data/knowledge_cache.json`) with zero degradation in functionality.*

### 4. Ingest Knowledge Base
Ingest reference documents (PDFs & TXTs) into vector embeddings:
```bash
python app/ingestion.py
```

### 5. Run API Server
```bash
uvicorn app.main:app --reload --port 8000
```
Access interactive API documentation at: `http://localhost:8000/docs`.

---

## 🧪 Running Automated Tests

Run the complete test suite:
```bash
python tests/test_infra.py
python tests/test_m2_ingestion.py
python tests/test_m2_5_expansion.py
python tests/test_m3_graph.py
python tests/test_m4_conversation.py
python tests/test_m5_json_input.py
python tests/test_m6_output_enforcement.py
```

---

## 📡 API Contract & Usage Examples

### 1. Free-Text Conversation (`POST /chat`)

#### Request (Turn 1 - Incomplete Metrics)
```json
POST /chat
{
  "session_id": null,
  "message": "Biodiversity is declining on my land."
}
```
#### Response (Clarifying Question)
```json
{
  "session_id": "28beac56-dba4-4af7-921c-aca59f728027",
  "reply_type": "clarifying_question",
  "message": "To provide scientifically-grounded multi-metric recommendations, I need a bit more detail about your land. Could you please share your soil organic carbon %, annual rainfall pattern, soil pH, or current land use / crop type?",
  "extracted_metrics": {
    "biodiversity_indicators": "declining"
  }
}
```

#### Request (Turn 2 - Providing Remaining Metrics)
```json
POST /chat
{
  "session_id": "28beac56-dba4-4af7-921c-aca59f728027",
  "message": "Soil organic carbon is 0.3%, rainfall is low, and I grow monoculture wheat in a semi-arid region."
}
```
#### Response (Evidence-Backed Multi-Metric Recommendations)
```json
{
  "session_id": "28beac56-dba4-4af7-921c-aca59f728027",
  "reply_type": "recommendation",
  "reasoning_summary": "In semi-arid agroecosystems with 0.3% soil organic carbon and monoculture wheat cropping...",
  "recommendations": [
    {
      "intervention": "Introduce legume-based cover crops",
      "mechanism": "Nitrogen fixation fuels microbial decomposition, accelerating soil organic matter turnover and forming stable humus fractions.",
      "impacted_metrics": ["soil_organic_carbon", "soil_moisture", "species_richness"],
      "expected_improvement": "15-25% increase in SOC over 2-3 years, +12-18% moisture retention",
      "time_horizon": "medium",
      "citation": "FAO Technical Manual on Soil Organic Carbon Management (2020), Vol 3, pp. 45-52",
      "confidence": "high"
    }
  ],
  "extracted_metrics": {
    "biodiversity_indicators": "declining",
    "soil_organic_carbon": "0.3%",
    "rainfall": "low rainfall",
    "land_use": "monoculture wheat",
    "region_type": "semi-arid"
  }
}
```

### 2. Direct Structured JSON Input (`POST /chat/json`)

#### Request
```json
POST /chat/json
{
  "session_id": null,
  "metrics": {
    "soil_organic_carbon": 0.3,
    "rainfall": "low",
    "land_use": "monoculture wheat",
    "region_type": "semi-arid"
  }
}
```

---

## 🏆 Evaluation Rubric Mapping

| Rubric Criterion | Weight | Implementation Details |
|---|---|---|
| **Depth of Reasoning** | **30%** | `multi_metric_reasoning_node` in `app/graph.py` explicitly connects $\ge 3$ environmental variables simultaneously (soil ↔ moisture ↔ microclimate ↔ species richness). |
| **Scientific Grounding** | **25%** | `app/retrieval.py` fetches vector evidence from 16 global reports. `app/validator.py` enforces anti-hallucination citation verification. |
| **Knowledge System Design** | **20%** | Dual vector store (`pgvector` PostgreSQL + local cache), `BAAI/bge-small-en-v1.5` embeddings, PDF parsing (`pypdf`), and semantic redundancy filtering ($>0.88$). |
| **Conversational Intelligence**| **15%** | Multi-turn session memory (`app/memory.py`), metric accumulation across turns, and completeness check loop ($<3$ metrics triggers clarifying question). |
| **Output Clarity** | **10%** | Pydantic schema validation (`app/validator.py`), strict `time_horizon` enums (`short`/`medium`/`long`), and structured JSON response formatting. |

---

## 📄 License & Attribution
Developed for the **Darukaa.Earth Climate-Tech Hackathon**. Source data attributed to FAO, IPCC, IPBES, CBD, UNEP, Project Drawdown, and USDA NRCS.
