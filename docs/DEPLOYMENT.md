# Darukaa.Earth — Production Deployment Walkthrough

This document provides exact, project-specific, step-by-step instructions for deploying the **Darukaa.Earth AI Biodiversity Intelligence Assistant** using **Supabase** for PostgreSQL + `pgvector` and **Render** for FastAPI backend & frontend web hosting.

---

## 📋 System Architecture & Component Mapping

- **Database**: Supabase PostgreSQL (Free Tier) with `pgvector` extension (384-dimensional vector embeddings).
- **Backend & API**: FastAPI running on Render Web Service (Free Tier Docker Container).
- **Frontend UI**: Nature-Tech Glassmorphism Web App (`app/static/`) mounted directly by FastAPI on root (`/`).
- **LLM Engine**: Groq API using `llama-3.3-70b-versatile`.
- **Embedding Model**: Local `BAAI/bge-small-en-v1.5` (384-dim open-source embeddings).

---

## 🗄️ Step 1: Supabase Database Setup

### 1.1 Create Supabase Project
1. Log in to [Supabase Dashboard](https://supabase.com).
2. Click **New Project**, name it `darukaa-biodiversity`, select your region, and set a strong database password (keep this password handy).
3. Once provisioned, go to **Project Settings** $\rightarrow$ **Database** $\rightarrow$ **Connection String** $\rightarrow$ **URI**.
4. Copy the connection string. It will look like:
   ```text
   postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```
   *(Note: Ensure you replace `[YOUR_PASSWORD]` with your actual database password).*

### 1.2 Enable Vector Extension & Apply Database Schema
Go to **SQL Editor** in the Supabase Dashboard, create a **New Query**, paste the following SQL schema, and click **Run**:

```sql
-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create Knowledge Chunks table (Stores 384-dim BAAI/bge-small-en-v1.5 embeddings)
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    source_title TEXT NOT NULL,
    source_url TEXT,
    content TEXT NOT NULL,
    embedding vector(384)
);

-- 3. Create Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    intervention TEXT NOT NULL,
    mechanism TEXT NOT NULL,
    impacted_metrics TEXT[] NOT NULL,
    expected_improvement TEXT,
    time_horizon VARCHAR(20),
    citation TEXT NOT NULL,
    source_chunk_id INTEGER REFERENCES knowledge_chunks(id)
);

-- 4. Create Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES conversations(session_id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    extracted_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 📥 Step 2: Populate Knowledge Base Database

Run the repository database initialization script (`app/init_db.py`) from your **local terminal** pointing at your remote Supabase connection string. This reads all 16 reference documents (PDFs & TXTs), computes embeddings, filters redundancies, and populates Supabase.

### On Windows PowerShell:
```powershell
$env:DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres"
$env:GROQ_API_KEY="<your_groq_api_key>"
python app/init_db.py
```

### On macOS / Linux (Bash):
```bash
DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres" \
GROQ_API_KEY="<your_groq_api_key>" \
python app/init_db.py
```

*Expected Output:*
```text
INFO:app.init_db:Connecting to database: ...
INFO:app.init_db:Enabling pgvector extension...
INFO:app.init_db:Creating database tables...
INFO:app.ingestion:Parsed 95 total raw chunks from source directory.
INFO:app.ingestion:Redundancy filtering: Accepted 95 chunks, Skipped 0 redundant chunks.
INFO:app.ingestion:PostgreSQL pgvector database updated with 95 chunks and 8 recommendations.
INFO:app.init_db:Initialization Complete!
```

---

## 🚀 Step 3: Render Web Service Setup

### 3.1 Create Web Service on Render
1. Push your repository to GitHub / GitLab.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** $\rightarrow$ **Web Service**.
4. Connect your `darukaa-biodiversity-ai` repository.

### 3.2 Service Configuration Settings
Fill in the following fields on Render:

- **Name**: `darukaa-biodiversity-ai`
- **Language / Environment**: `Docker` (or `Python 3`)
- **Region**: Choose closest to your database (e.g. Oregon/US West or Frankfurt/EU)
- **Branch**: `main`
- **Dockerfile Path**: `./Dockerfile`
- **Build Command**: *(Leave empty when using Docker option)*
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` *(Handled automatically by Dockerfile)*

### 3.3 Environment Variables
In Render's **Environment** tab, add the following environment variables:

| Environment Variable | Description / Value |
|---|---|
| `GROQ_API_KEY` | `<your_groq_api_key>` (Your active Groq API Key) |
| `GROQ_MODEL_NAME` | `llama-3.3-70b-versatile` (Default instruction model) |
| `DATABASE_URL` | `postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres` |
| `EMBEDDING_MODEL_NAME` | `BAAI/bge-small-en-v1.5` |
| `EMBEDDING_DIMENSION` | `384` |
| `ALLOWED_ORIGINS` | `*` (or your specific custom domain URL) |

4. Click **Create Web Service**. Render will build the container, install dependencies, and start Uvicorn.

---

## 🌐 Step 4: Frontend Verification

No separate deployment step is needed for the Web UI!
FastAPI automatically serves the static nature-tech UI mounted at `/` (`app/static/index.html`).

Once Render completes building, your application will be live at:
`https://darukaa-biodiversity-ai.onrender.com`

---

## ✅ Step 5: Post-Deployment Verification Checklist

Run these manual checks against your live deployed URL (`https://<your-render-app>.onrender.com`):

### 1. Health Endpoint Check
Visit `https://<your-render-app>.onrender.com/health` in your browser or curl:
```bash
curl https://<your-render-app>.onrender.com/health
```
*Expected Response (`200 OK`):*
```json
{
  "status": "healthy",
  "groq_model": "llama-3.3-70b-versatile",
  "embedding_model": "BAAI/bge-small-en-v1.5"
}
```

### 2. Conversational Clarifying Question Check (`POST /chat`)
Send an incomplete query with fewer than 3 environmental metrics:
```bash
curl -X POST https://<your-render-app>.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My farm in Rajasthan has soil organic carbon of 0.35%."}'
```
*Expected Response:* `reply_type: "clarifying_question"` asking for missing climate/moisture/land-use details.

### 3. Structured Metric Ingestion Check (`POST /chat/json`)
Send a complete structured JSON payload (PRD semi-arid monoculture scenario):
```bash
curl -X POST https://<your-render-app>.onrender.com/chat/json \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": {
      "soil_organic_carbon": "0.35%",
      "rainfall": "420mm annual",
      "crop_type": "Wheat monoculture",
      "land_use": "Agricultural cropland",
      "latitude": "26.9124",
      "longitude": "75.7873"
    }
  }'
```
*Expected Response:* `reply_type: "recommendation"` returning multi-metric ecological reasoning summary, 3+ cited recommendations, and top matching vector chunk sources in `retrieval_trace`.

### 4. Interactive Web UI Check
Open `https://<your-render-app>.onrender.com` in Chrome/Edge/Firefox. Verify:
- Dark mode Nature-Tech glassmorphism interface loads seamlessly.
- Switching between "Conversational Chat" and "Structured Metric Form" works.
- Submitting a query renders recommendation cards and retrieval trace drawer.

---

## ⚠️ Step 6: Known Platform Limitations to Expect

1. **Render Free Tier Cold Starts**: Render spins down free web services after 15 minutes of inactivity. The first HTTP request after idle will take **30 to 60 seconds** to start up and load the PyTorch sentence-transformer model into memory. Subsequent requests respond in < 1-2s.
2. **Supabase Free Tier Pausing**: Inactive Supabase databases pause after 7 days without traffic. Log into Supabase dashboard to restore with a single click if paused.
