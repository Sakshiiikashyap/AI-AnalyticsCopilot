import pandas as pd

df = pd.read_csv(r"C:\Users\pc\Downloads\DailyDelhiClimateTest.csv")
print("Columns:", list(df.columns))
print("Date column dtype:", df["date"].dtype)
print("First 5 date values:", df["date"].head().tolist())

parsed = pd.to_datetime(df["date"], errors="coerce", format="mixed")
print("Parsed successfully for:", parsed.notna().mean() * 100, "% of rows")
print("Any parsing errors (NaT count):", parsed.isna().sum())
