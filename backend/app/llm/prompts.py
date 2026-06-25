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
    
INSIGHT_SYSTEM_PROMPT = """You are an AI data analyst generating an executive insight summary for \
a dataset, as part of a product called AI Analytics Copilot.

Rules you must always follow:
1. Base every statement ONLY on the schema, profile statistics, and anomaly/forecast results \
provided in the user message. Never invent numbers not present in that context.
2. Respond with ONLY a valid JSON object, no markdown formatting, no code fences, no preamble \
or explanation outside the JSON.
3. The JSON object must have exactly these keys: "summary" (a 2-3 sentence overview string), \
"key_findings" (a list of 3-5 short strings), "risks" (a list of 1-3 short strings, can be empty \
list if none apply), "opportunities" (a list of 1-3 short strings, can be empty list if none \
apply), "recommendations" (a list of 2-4 short strings).
4. Keep each list item concise, specific, and reference actual numbers/column names from the \
provided context where relevant.
5. Write as a knowledgeable analyst colleague, not a generic chatbot. This is a copilot for a \
human analyst, not a replacement.
"""


def build_insight_prompt(schema, profile, anomaly_summary, forecast_summary):
    import json as _json

    context_parts = [
        "## Dataset Schema",
        _json.dumps(_trim_schema(schema), indent=2),
    ]

    if profile:
        context_parts += ["", "## Dataset Profile (precomputed statistics)", _json.dumps(_trim_profile(profile), indent=2)]

    if anomaly_summary:
        context_parts += ["", "## Most Recent Anomaly Detection Run", _json.dumps(anomaly_summary, indent=2, default=str)]
    else:
        context_parts += ["", "## Anomaly Detection", "No anomaly detection has been run yet for this dataset."]

    if forecast_summary:
        context_parts += ["", "## Most Recent Forecast Run", _json.dumps(forecast_summary, indent=2, default=str)]
    else:
        context_parts += ["", "## Forecasting", "No forecast has been run yet for this dataset."]

    context_parts += [
        "",
        "## Task",
        "Generate the executive insight summary JSON object now, based strictly on the context above.",
    ]
    return "\n".join(context_parts)