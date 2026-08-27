"""Load and clean the raw orders dataset."""

from __future__ import annotations

import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

CATEGORIE_MAPPING = {
    "jouet": "jouets",
    "vetement": "vetements",
    "sport": "sports",
    "electro": "electronique",
}

STATUT_MAPPING = {
    "livre": "livre",
    "annule": "annule",
}

REGION_MAPPING = {
    "idf": "ile_de_france",
    "ara": "auvergne_rhone_alpes",
}


def _strip_accents(text: str) -> str:
    """Decompose accented characters and drop the combining marks (e.g. 'ô' -> 'o')."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def _normalize_text(series: pd.Series, collapse_spaces: bool = True) -> pd.Series:
    """Strip whitespace, remove all French accents, and lowercase a text column."""
    cleaned = series.str.strip().map(_strip_accents, na_action="ignore")
    if collapse_spaces:
        cleaned = cleaned.str.replace(" ", "_").str.replace("-", "_")
    return cleaned.str.lower()


def load_raw_data(path: str | Path) -> pd.DataFrame:
    """Read the raw orders CSV from disk."""
    return pd.read_csv(path)


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows."""
    return df.drop_duplicates()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize categorical text, parse numeric/date fields, and derive order value.

    Accents/casing are normalized first, so the mapping dictionaries only need to
    cover post-normalization spellings (e.g. abbreviations like "idf") rather than
    accented variants that can no longer occur at that point in the pipeline.
    """
    df = df.copy()

    df["produit"] = _normalize_text(df["produit"])
    df["categorie"] = _normalize_text(df["categorie"]).replace(CATEGORIE_MAPPING)
    df["region"] = _normalize_text(df["region"]).replace(REGION_MAPPING)
    df["statut"] = _normalize_text(df["statut"]).replace(STATUT_MAPPING)
    df["client_email"] = df["client_email"].str.strip().str.replace("AT", "@").str.lower()

    # Prices are entered inconsistently, including with a leading "-" for a subset
    # of rows. There is no business reason for a negative unit price in this
    # dataset (no returns/adjustments column), so a "-" is treated as a data-entry
    # artifact rather than a genuine negative amount, and is stripped like other
    # non-numeric characters.
    df["prix"] = (
        df["prix"].astype(str).str.strip().str.replace("-", "").str.replace(",", ".").str.replace("€", "")
    )
    df["quantite"] = df["quantite"].astype(str).str.strip().str.replace("-", "").str.replace(",", ".")

    df["prix"] = df["prix"].astype(float)
    df["quantite"] = df["quantite"].astype(float)

    df = df.drop(columns="montant")
    df["montant_commande"] = df["prix"] * df["quantite"]

    df["date_vente"] = pd.to_datetime(df["date_vente"], format="mixed", dayfirst=True)
    df["annee_vente"] = df["date_vente"].dt.year
    df["mois_vente"] = df["date_vente"].dt.month
    df["jour_vente"] = df["date_vente"].dt.day

    return df


def fill_blanks(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values: mode for categoricals/numerics, forward-fill for dates.

    `montant_commande` is recomputed from `prix` and `quantite` after they are
    filled, rather than being filled independently from its own mode. Filling it
    separately would break the prix * quantite = montant_commande relationship
    for any row where quantite was originally missing.
    """
    df = df.copy()

    for col in ["statut", "quantite", "prix", "categorie", "region", "produit"]:
        df[col] = df[col].fillna(df[col].mode()[0])

    df["montant_commande"] = df["prix"] * df["quantite"]

    df["client_email"] = df["client_email"].fillna(np.nan)

    for col in ["date_vente", "annee_vente", "mois_vente", "jour_vente"]:
        df[col] = df[col].ffill()

    return df


def load_and_clean(path: str | Path) -> pd.DataFrame:
    """Run the full loading pipeline: read, dedupe, clean, and fill missing values."""
    df = load_raw_data(path)
    df = remove_duplicates(df)
    df = clean_data(df)
    df = fill_blanks(df)
    return df
