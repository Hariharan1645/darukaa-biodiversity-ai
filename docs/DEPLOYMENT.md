# Manual Production Deployment Guide

This guide provides step-by-step instructions for deploying the **Darukaa Biodiversity Intelligence AI** application to production cloud services.

---

## 📋 Required Environment Variables

Set the following environment variables on your cloud hosting platforms:

| Variable | Description | Example / Recommended Value |
|---|---|---|
| `GROQ_API_KEY` | Groq API Secret Key | `gsk_...` |
| `GROQ_MODEL_NAME` | Non-agentic Groq LLM model ID | `openai/gpt-oss-120b` |
| `DATABASE_URL` | PostgreSQL connection string (with pgvector) | `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres` |
| `EMBEDDING_MODEL_NAME` | Local open-source embedding model | `BAAI/bge-small-en-v1.5` |
| `EMBEDDING_DIMENSION` | Vector embedding dimension | `384` |
| `ALLOWED_ORIGINS` | Permitted CORS origins for API requests | `https://your-app-domain.com,http://localhost:8000` |
| `PORT` | Container listening port (injected by Render/Railway) | `8000` |

---

## 🗄️ Step 1: PostgreSQL + pgvector Database Setup (Supabase / Render Postgres)

### Option A: Supabase
1. Create a new project in [Supabase Dashboard](https://supabase.com).
2. Go to **Project Settings** $\rightarrow$ **Database** and copy the **URI Connection String**.
3. Open **SQL Editor** in Supabase and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Run database initialization script locally pointed at your Supabase `DATABASE_URL`:
   ```bash
   DATABASE_URL="postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" python app/init_db.py
   ```

### Option B: Render PostgreSQL
1. Create a **New PostgreSQL** instance on Render.
2. Select **PostgreSQL 16** with `pgvector` enabled.
3. Copy the **Internal / External Database URL**.

---

## 🚀 Step 2: FastAPI Backend Deployment (Render / Railway)

### Option A: Render Web Service
1. Connect your GitHub repository to [Render](https://render.com).
2. Select **New Web Service** $\rightarrow$ choose repository `darukaa-biodiversity-ai`.
3. Select **Docker** environment.
4. Set Build / Start Commands:
   - **Environment**: `Docker`
   - **Docker Command**: Automatically reads [`Dockerfile`](file:///c:/Users/harih/OneDrive/Desktop/Darukaa/Dockerfile).
5. Add Environment Variables under **Environment**:
   - `GROQ_API_KEY` = `gsk_...`
   - `GROQ_MODEL_NAME` = `openai/gpt-oss-120b`
   - `DATABASE_URL` = `postgresql://...`
   - `ALLOWED_ORIGINS` = `*`
6. Click **Deploy Web Service**.

### Option B: Railway
1. Create a **New Project** on [Railway](https://railway.app) $\rightarrow$ **Deploy from GitHub repo**.
2. Railway automatically detects `Dockerfile`.
3. Add Environment Variables under **Variables**.
4. Railway will automatically expose the app and inject the `PORT` variable.

---

## 🌐 Step 3: Frontend Web UI Access

The frontend nature-tech Web UI is bundled and mounted directly inside the FastAPI backend container via `app/main.py` (`StaticFiles` at `/`).

Once your backend service is deployed to Render or Railway (e.g. `https://darukaa-biodiversity-ai.onrender.com`), visiting the URL in any browser serves the full interactive Web UI automatically!

### Health Check Verification
Verify service health at:
`GET https://your-backend-url.com/health`

Response:
```json
{
  "status": "healthy",
  "groq_model": "openai/gpt-oss-120b",
  "embedding_model": "BAAI/bge-small-en-v1.5"
}
```
