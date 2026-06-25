"""
Insight Engine - generates a proactive, structured executive summary by
combining everything already computed for a dataset (profile stats, most
recent anomaly run, most recent forecast run) and asking the LLM to narrate
it as findings/risks/opportunities/recommendations.

Same RAG-grounding principle as the chat feature: the LLM only ever sees
real computed numbers, never raw row-level data, and is instructed to
respond in strict JSON so we can render it as structured UI cards rather
than a wall of text.
"""
import json

from sqlalchemy.orm import Session

from app.features.anomaly.models import AnomalyRun
from app.features.datasets.models import Dataset
from app.features.datasets.service import get_dataset
from app.features.forecasting.models import ForecastRun
from app.features.insights.models import InsightRun
from app.features.profiling.models import DatasetProfile
from app.llm.factory import get_llm_provider
from app.llm.prompts import INSIGHT_SYSTEM_PROMPT, build_insight_prompt
from app.shared.exceptions import UpstreamError, parse_uuid


def _get_latest_anomaly_summary(db: Session, dataset_id):
    run = (
        db.query(AnomalyRun)
        .filter(AnomalyRun.dataset_id == dataset_id)
        .order_by(AnomalyRun.created_at.desc())
        .first()
    )
    if not run:
        return None
    top_anomalies = (run.result_json or {}).get("anomalies", [])[:5]
    return {
        "method": run.method,
        "anomaly_count": run.anomaly_count,
        "columns_used": (run.result_json or {}).get("columns_used", []),
        "top_anomalies_sample": top_anomalies,
    }


def _get_latest_forecast_summary(db: Session, dataset_id):
    run = (
        db.query(ForecastRun)
        .filter(ForecastRun.dataset_id == dataset_id)
        .order_by(ForecastRun.created_at.desc())
        .first()
    )
    if not run:
        return None
    result = run.result_json or {}
    forecast_points = result.get("forecast", [])
    backtest = result.get("backtest")
    return {
        "metric_column": run.metric_column,
        "date_column": run.date_column,
        "periods_forecasted": run.periods,
        "first_forecast_point": forecast_points[0] if forecast_points else None,
        "last_forecast_point": forecast_points[-1] if forecast_points else None,
        "backtest_accuracy": backtest,
    }


def _parse_llm_json(raw_text: str) -> dict:
    """LLMs sometimes wrap JSON in markdown code fences despite instructions
    not to. Strip those defensively before parsing."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    return json.loads(cleaned)


def generate_insights(db: Session, user_id: str, dataset_id: str) -> InsightRun:
    dataset: Dataset = get_dataset(db, user_id, dataset_id)

    profile = db.query(DatasetProfile).filter(DatasetProfile.dataset_id == dataset.id).first()
    profile_dict = None
    if profile:
        profile_dict = {
            "summary": profile.summary_json,
            "duplicates_count": profile.duplicates_count,
            "correlation": profile.correlation_json,
            "outliers": profile.outliers_json,
        }

    anomaly_summary = _get_latest_anomaly_summary(db, dataset.id)
    forecast_summary = _get_latest_forecast_summary(db, dataset.id)

    prompt = build_insight_prompt(
        schema=dataset.schema_json or {},
        profile=profile_dict,
        anomaly_summary=anomaly_summary,
        forecast_summary=forecast_summary,
    )

    llm = get_llm_provider()
    try:
        raw_response = llm.generate(INSIGHT_SYSTEM_PROMPT, prompt, max_output_tokens=2048)
    except Exception:
        raise UpstreamError("Could not generate insights right now. Please try again in a moment.")

    try:
        parsed = _parse_llm_json(raw_response)
    except Exception:
        raise UpstreamError("Could not generate insights right now. Please try again in a moment.")

    result = {
        "summary": parsed.get("summary", ""),
        "key_findings": parsed.get("key_findings", []),
        "risks": parsed.get("risks", []),
        "opportunities": parsed.get("opportunities", []),
        "recommendations": parsed.get("recommendations", []),
    }

    run = InsightRun(
        dataset_id=parse_uuid(dataset_id, "dataset"),
        user_id=parse_uuid(user_id, "user"),
        result_json=result,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run