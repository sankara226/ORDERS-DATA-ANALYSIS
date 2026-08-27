"""Descriptive statistics and aggregations over the cleaned orders dataset."""

import numpy as np
import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    """Return basic data-quality metrics: shape, duplicate count, missing-value rates."""
    na_df = df.isna()
    return {
        "shape": df.shape,
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_by_column": na_df.sum().sort_values(ascending=False),
        "missing_pct_total": float((na_df.sum().sum() / df.size) * 100),
    }


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Total order value per category, sorted descending."""
    return (
        df.groupby("categorie")["montant_commande"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def avg_price_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Mean unit price per region, sorted descending."""
    return (
        df.groupby("region")["prix"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )


def price_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Rows whose unit price falls outside the IQR-based outlier fence."""
    q1 = df["prix"].quantile(0.25)
    q3 = df["prix"].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return df[(df["prix"] < lower) | (df["prix"] > upper)]


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation matrix over numeric columns."""
    return df.select_dtypes(include=np.number).corr()


def top_correlation_pairs(corr: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Rank column pairs by absolute correlation strength."""
    pairs = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            pairs.append(
                {
                    "var1": corr.columns[i],
                    "var2": corr.columns[j],
                    "corr": corr.iloc[i, j],
                }
            )
    return pd.DataFrame(pairs).sort_values("corr", key=abs, ascending=False).head(n)


def monthly_revenue_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Total order value per calendar month across the dataset's date range."""
    trend = (
        df.set_index("date_vente")["montant_commande"]
        .resample("MS")
        .sum()
        .reset_index()
    )
    trend.columns = ["mois", "montant_commande"]
    return trend
