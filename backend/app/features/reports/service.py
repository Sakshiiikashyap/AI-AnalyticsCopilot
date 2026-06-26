"""
Executive PDF report generator.

Pulls together whatever has already been computed for a dataset (profile,
most recent anomaly run, most recent forecast run, most recent AI insight
run) into a single downloadable PDF. Deliberately does NOT trigger fresh
LLM calls here - it reuses the latest existing InsightRun if one exists,
to keep report generation fast and avoid extra API quota usage.
"""
import uuid
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.core.config import settings
from app.features.anomaly.models import AnomalyRun
from app.features.datasets.models import Dataset
from app.features.datasets.service import get_dataset
from app.features.forecasting.models import ForecastRun
from app.features.insights.models import InsightRun
from app.features.profiling.models import DatasetProfile
from app.features.reports.models import ReportRun
from app.shared.exceptions import parse_uuid

REPORTS_DIR = Path(settings.UPLOAD_DIR).parent / "reports"


def _styles():
    base = getSampleStyleSheet()
    base.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=base["Heading2"],
            textColor=colors.HexColor("#1d4ed8"),
            spaceAfter=8,
            spaceBefore=16,
        )
    )
    return base


def _build_pdf(file_path: Path, dataset: Dataset, profile, anomaly_run, forecast_run, insight_run):
    doc = SimpleDocTemplate(str(file_path), pagesize=letter, topMargin=0.7 * inch, bottomMargin=0.7 * inch)
    styles = _styles()
    elements = []

    elements.append(Paragraph("AI Analytics Copilot", styles["Title"]))
    elements.append(Paragraph("Executive Report: " + dataset.name, styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(
        Paragraph(
            str(dataset.row_count) + " rows, " + str(dataset.column_count) + " columns, file type: "
            + dataset.file_type.upper(),
            styles["Normal"],
        )
    )

    if insight_run and insight_run.result_json:
        result = insight_run.result_json
        elements.append(Paragraph("Executive Summary", styles["SectionHeading"]))
        elements.append(Paragraph(result.get("summary", ""), styles["Normal"]))

        if result.get("key_findings"):
            elements.append(Paragraph("Key Findings", styles["SectionHeading"]))
            for item in result["key_findings"]:
                elements.append(Paragraph("- " + item, styles["Normal"]))

        if result.get("risks"):
            elements.append(Paragraph("Risks", styles["SectionHeading"]))
            for item in result["risks"]:
                elements.append(Paragraph("- " + item, styles["Normal"]))

        if result.get("opportunities"):
            elements.append(Paragraph("Opportunities", styles["SectionHeading"]))
            for item in result["opportunities"]:
                elements.append(Paragraph("- " + item, styles["Normal"]))

        if result.get("recommendations"):
            elements.append(Paragraph("Recommendations", styles["SectionHeading"]))
            for item in result["recommendations"]:
                elements.append(Paragraph("- " + item, styles["Normal"]))
    else:
        elements.append(Paragraph("Executive Summary", styles["SectionHeading"]))
        elements.append(Paragraph("No AI insight summary has been generated for this dataset yet.", styles["Normal"]))

    if profile:
        elements.append(Paragraph("Data Quality Profile", styles["SectionHeading"]))
        table_data = [["Metric", "Value"]]
        table_data.append(["Duplicate rows", str(profile.duplicates_count or 0)])
        missing = (profile.missing_values_json or {}).get("total_missing_cells", 0)
        table_data.append(["Total missing cells", str(missing)])
        outlier_cols = (profile.outliers_json or {}).get("columns", [])
        table_data.append(["Columns with outliers", str(len(outlier_cols))])
        corr_pairs = (profile.correlation_json or {}).get("strong_pairs", [])
        table_data.append(["Strong correlations found", str(len(corr_pairs))])

        t = Table(table_data, colWidths=[3 * inch, 3 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(t)

    if anomaly_run:
        elements.append(Paragraph("Anomaly Detection", styles["SectionHeading"]))
        elements.append(
            Paragraph(
                "Method: " + anomaly_run.method + ". Flagged " + str(anomaly_run.anomaly_count)
                + " anomalous rows out of " + str((anomaly_run.result_json or {}).get("total_rows", "N/A")) + ".",
                styles["Normal"],
            )
        )
    else:
        elements.append(Paragraph("Anomaly Detection", styles["SectionHeading"]))
        elements.append(Paragraph("No anomaly detection has been run for this dataset yet.", styles["Normal"]))

    if forecast_run:
        elements.append(Paragraph("Forecast", styles["SectionHeading"]))
        result = forecast_run.result_json or {}
        backtest = result.get("backtest")
        line = (
            "Forecasted '" + forecast_run.metric_column + "' using '" + forecast_run.date_column
            + "' for " + str(forecast_run.periods) + " periods ahead."
        )
        elements.append(Paragraph(line, styles["Normal"]))
        if backtest:
            elements.append(
                Paragraph(
                    "Backtest accuracy: MAE " + str(backtest.get("mae")) + ", RMSE " + str(backtest.get("rmse"))
                    + " (validated on " + str(backtest.get("holdout_periods")) + " held-out periods).",
                    styles["Normal"],
                )
            )
    else:
        elements.append(Paragraph("Forecast", styles["SectionHeading"]))
        elements.append(Paragraph("No forecast has been run for this dataset yet.", styles["Normal"]))

    doc.build(elements)


def generate_report(db: Session, user_id: str, dataset_id: str) -> ReportRun:
    dataset: Dataset = get_dataset(db, user_id, dataset_id)

    profile = db.query(DatasetProfile).filter(DatasetProfile.dataset_id == dataset.id).first()
    anomaly_run = (
        db.query(AnomalyRun).filter(AnomalyRun.dataset_id == dataset.id).order_by(AnomalyRun.created_at.desc()).first()
    )
    forecast_run = (
        db.query(ForecastRun).filter(ForecastRun.dataset_id == dataset.id).order_by(ForecastRun.created_at.desc()).first()
    )
    insight_run = (
        db.query(InsightRun).filter(InsightRun.dataset_id == dataset.id).order_by(InsightRun.created_at.desc()).first()
    )

    user_dir = REPORTS_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    file_name = str(uuid.uuid4()) + ".pdf"
    file_path = user_dir / file_name

    _build_pdf(file_path, dataset, profile, anomaly_run, forecast_run, insight_run)

    run = ReportRun(
        dataset_id=parse_uuid(dataset_id, "dataset"),
        user_id=parse_uuid(user_id, "user"),
        file_path=str(file_path),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_report(db: Session, user_id: str, report_id: str) -> ReportRun:
    from app.shared.exceptions import NotFoundError

    run = (
        db.query(ReportRun)
        .filter(ReportRun.id == parse_uuid(report_id, "report"), ReportRun.user_id == parse_uuid(user_id, "user"))
        .first()
    )
    if not run:
        raise NotFoundError("Report not found.")
    return run