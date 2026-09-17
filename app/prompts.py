# Prompt templates for LangGraph nodes

METRICS_EXTRACTION_PROMPT = """You are an environmental data extraction AI assistant.
Your task is to analyze the user's input and extract any mentioned environmental variables and geo-location coordinates.

Target environmental metrics to look for:
- soil_organic_carbon: (e.g., "0.3%", "depleted", "low carbon", "0.5%")
- soil_ph: (e.g., "6.5", "acidic", "alkaline", "7.2")
- soil_moisture: (e.g., "dry", "10%", "low moisture", "waterlogged")
- rainfall: (e.g., "low rainfall", "semi-arid", "400mm/year", "erratic rain")
- land_use: (e.g., "monoculture wheat", "pasture", "intensive cropland", "urban park", "agroforestry")
- region_type: (e.g., "semi-arid", "tropical", "urban", "temperate")
- biodiversity_indicators: (e.g., "declining pollinators", "low species richness", "few birds")
- human_impact: (e.g., "excessive pesticide use", "heavy fertilizer application", "soil compaction", "deforestation")
- latitude: (e.g., 6.9271, 37.7749, "6.9 N")
- longitude: (e.g., 79.8612, -122.4194, "79.8 E")

Return ONLY a valid JSON object mapping metric names to their extracted values (or null if not mentioned).

Example output:
{
  "soil_organic_carbon": "0.3%",
  "rainfall": "low rainfall",
  "land_use": "monoculture wheat",
  "region_type": "semi-arid",
  "soil_ph": null,
  "soil_moisture": null,
  "biodiversity_indicators": null,
  "human_impact": null,
  "latitude": 6.9271,
  "longitude": 79.8612
}

User input:
"""

REASONING_PROMPT = """You are an expert AI Environmental Scientist.
Analyze the following extracted environmental metrics (including regional/climate context from coordinates if present) and retrieved scientific reference evidence chunks.

Your goal is to explain the ecological mechanism connecting AT LEAST 3 environmental variables simultaneously (e.g., Soil Organic Carbon ↔ Rainfall / Moisture ↔ Land Use ↔ Biodiversity ↔ Human Impact ↔ Geo-Climate Zone).

Retrieved Evidence Chunks:
{retrieved_chunks_text}

Extracted Metrics & Regional Context:
{extracted_metrics_json}

Provide a rigorous scientific analysis (2-3 paragraphs) explaining how these environmental variables interact and cause the observed environmental degradation. Highlight causal pathways supported by the scientific evidence.
"""

RECOMMENDATION_PROMPT = """You are an expert AI Environmental Scientist.
Based on the environmental metrics and scientific reasoning provided below, generate evidence-backed interventions to restore the land and improve biodiversity metrics.

Extracted Metrics & Regional Context:
{extracted_metrics_json}

Scientific Reasoning & Analysis:
{reasoning_summary}

Retrieved Scientific Evidence Chunks:
{retrieved_chunks_text}

CRITICAL INSTRUCTIONS:
1. Every recommendation MUST be grounded in the retrieved scientific evidence.
2. DO NOT fabricate any citations. Only cite real sources present in the retrieved chunks or curated evidence (e.g. FAO, IPCC, IPBES, CBD, UNEP, Project Drawdown, USDA NRCS, ICRAF).
3. Every recommendation MUST contain ALL of the following fields:
   - intervention: Specific actionable intervention title
   - mechanism: Scientific mechanism explaining why it works
   - impacted_metrics: List of metrics improved (at least 2)
   - expected_improvement: Quantified improvement (e.g., "+15-25% SOC over 2-3 years")
   - time_horizon: "short", "medium", or "long"
   - citation: Exact scientific source title / guideline name
   - confidence: "high", "medium", or "low"

Return ONLY a valid JSON array of recommendation objects.
"""
