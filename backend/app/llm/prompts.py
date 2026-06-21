import json
from typing import Any

SYSTEM_PROMPT = """You are an AI data analyst assistant embedded in a product called AI Analytics Copilot. You answer questions about a SPECIFIC uploaded dataset.

Rules you must always follow:
1. Answer ONLY using the dataset schema, profile statistics, and computed query results provided in the user message. Never invent numbers that are not present in that context.
2. If the provided context does not contain enough information to answer precisely, say so plainly and suggest what computation or column would help instead of guessing.
3. Be concise, business-toned, and concrete. Prefer specific numbers and column names over vague language.
4. When relevant, surface a brief insight or recommendation, not just the raw fact.
5. You are a copilot for a human analyst, not a replacement - write as a knowledgeable colleague, not as a generic chatbot.
"""


def build_user_prompt(question, schema, profile, computed_result):
    context_parts = [
        "## Dataset Schema",
        json.dumps(_trim_schema(schema), indent=2),
    ]

    if profile:
        context_parts += ["", "## Dataset Profile (precomputed statistics)", json.dumps(_trim_profile(profile), indent=2)]

    if computed_result is not None:
        context_parts += ["", "## Computed Result For This Question", json.dumps(computed_result, indent=2, default=str)]
    else:
        context_parts += [
            "",
            "## Computed Result For This Question",
            "No direct computation matched this question automatically. Answer using only the schema/profile above, and be explicit about that limitation if it prevents a precise answer.",
        ]

    context_parts += ["", "## Analyst's Question", question]
    return "\n".join(context_parts)


def _trim_schema(schema):
    return {
        "row_count": schema.get("row_count"),
        "column_count": schema.get("column_count"),
        "columns": [
            {"name": c["name"], "type": c.get("semantic_type", c.get("dtype"))}
            for c in schema.get("columns", [])
        ],
    }


def _trim_profile(profile):
    summary = profile.get("summary", {})
    trimmed_columns = []
    for c in summary.get("columns", []):
        entry = {"name": c["name"], "null_percentage": c.get("null_percentage")}
        for key in ("mean", "min", "max", "median", "top_values"):
            if key in c:
                entry[key] = c[key]
        trimmed_columns.append(entry)

    return {
        "columns": trimmed_columns,
        "duplicates_count": profile.get("duplicates_count"),
        "strong_correlations": profile.get("correlation", {}).get("strong_pairs", []),
        "outlier_columns": profile.get("outliers", {}).get("columns", []),
    }