import re
from typing import Any

import pandas as pd


def _has_word(q, *words):
    return any(re.search(r"\b" + re.escape(w) + r"\b", q) for w in words)


def _column_mentioned(q, column_name):
    normalized = column_name.lower().replace("_", " ")
    return _has_word(q, column_name.lower()) or normalized in q


def _numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


def _categorical_columns(df):
    return [c for c in df.columns if df[c].dtype == object or pd.api.types.is_categorical_dtype(df[c])]


def _datetime_columns(df):
    cols = []
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            cols.append(c)
    return cols


def try_compute(question, df):
    q = question.lower().strip()

    if _has_word(q, "top", "most", "highest") or "best performing" in q:
        result = _top_bottom_by_group(df, q, ascending=False)
        if result:
            return result

    if _has_word(q, "underperform", "underperforming", "lowest", "worst", "bottom", "least"):
        result = _top_bottom_by_group(df, q, ascending=True)
        if result:
            return result

    if _has_word(q, "trend", "growth", "monthly", "weekly", "yearly") or "over time" in q or "by month" in q:
        result = _time_trend(df, q)
        if result:
            return result

    if _has_word(q, "average", "mean"):
        result = _aggregate_metric(df, q, agg="mean")
        if result:
            return result

    if _has_word(q, "total", "sum"):
        result = _aggregate_metric(df, q, agg="sum")
        if result:
            return result

    return None


def _guess_metric_column(df, q):
    numeric_cols = _numeric_columns(df)
    if not numeric_cols:
        return None
    for col in numeric_cols:
        if _column_mentioned(q, col):
            return col
    priority_keywords = ["revenue", "sales", "amount", "price", "profit"]
    for keyword in priority_keywords:
        for col in numeric_cols:
            if keyword in col.lower():
                return col
    return numeric_cols[0]


def _guess_group_column(df, q):
    cat_cols = _categorical_columns(df)
    for col in cat_cols:
        if _column_mentioned(q, col):
            return col
    priority_keywords = ["category", "product", "region", "segment", "type", "name"]
    for keyword in priority_keywords:
        for col in cat_cols:
            if keyword in col.lower():
                return col
    return cat_cols[0] if cat_cols else None


def _top_bottom_by_group(df, q, ascending):
    metric_col = _guess_metric_column(df, q)
    group_col = _guess_group_column(df, q)
    if not metric_col or not group_col:
        return None

    n = 5
    match = re.search(r"top\s+(\d+)|bottom\s+(\d+)", q)
    if match:
        n = int(match.group(1) or match.group(2))

    grouped = df.groupby(group_col)[metric_col].sum().sort_values(ascending=ascending).head(n)
    label = "bottom" if ascending else "top"
    return {
        "computation": label + " " + str(n) + " '" + group_col + "' by sum of '" + metric_col + "'",
        "group_column": group_col,
        "metric_column": metric_col,
        "results": [{"group": str(idx), "value": float(val)} for idx, val in grouped.items()],
    }


def _aggregate_metric(df, q, agg):
    metric_col = _guess_metric_column(df, q)
    if not metric_col:
        return None
    group_col = _guess_group_column(df, q)

    if group_col and _column_mentioned(q, group_col):
        grouped = df.groupby(group_col)[metric_col].agg(agg).sort_values(ascending=False)
        return {
            "computation": agg + " of '" + metric_col + "' grouped by '" + group_col + "'",
            "group_column": group_col,
            "metric_column": metric_col,
            "results": [{"group": str(idx), "value": float(val)} for idx, val in grouped.items()],
        }

    value = getattr(df[metric_col], agg)()
    return {
        "computation": agg + " of '" + metric_col + "' across entire dataset",
        "metric_column": metric_col,
        "value": float(value),
    }


def _time_trend(df, q):
    date_cols = _datetime_columns(df)
    if not date_cols:
        for col in df.columns:
            if df[col].dtype == object:
                parsed = pd.to_datetime(df[col], errors="coerce", format="mixed")
                if parsed.notna().mean() > 0.8:
                    df = df.copy()
                    df[col] = parsed
                    date_cols = [col]
                    break
    if not date_cols:
        return None

    date_col = date_cols[0]
    metric_col = _guess_metric_column(df, q)
    if not metric_col:
        return None

    freq = "ME"
    if "week" in q:
        freq = "W"
    elif "year" in q:
        freq = "YE"

    series = df.dropna(subset=[date_col]).set_index(date_col)[metric_col].resample(freq).sum()
    points = [{"period": str(idx.date()), "value": float(val)} for idx, val in series.items()]

    growth_pct = None
    if len(points) >= 2 and points[-2]["value"] != 0:
        growth_pct = round((points[-1]["value"] - points[-2]["value"]) / abs(points[-2]["value"]) * 100, 2)

    return {
        "computation": "sum of '" + metric_col + "' resampled by " + freq + " using date column '" + date_col + "'",
        "date_column": date_col,
        "metric_column": metric_col,
        "period_over_period_growth_pct_latest": growth_pct,
        "series": points,
    }