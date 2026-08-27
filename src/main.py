"""Entry point: load, clean, analyze, and export the orders dashboard."""

from pathlib import Path

from src import analysis, data_loading, visualization

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "messy_orders_data.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "orders_cleaned.csv"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
DASHBOARD_PATH = PROJECT_ROOT / "outputs" / "dashboard.png"


def run() -> None:
    """Run the full pipeline: clean the data, print key insights, export charts."""
    raw = data_loading.load_raw_data(RAW_DATA_PATH)
    duplicates_removed = int(raw.duplicated().sum())

    df = data_loading.load_and_clean(RAW_DATA_PATH)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    profile = analysis.profile_dataset(df)
    print(f"Rows: {profile['shape'][0]} (from {raw.shape[0]} raw rows) | Columns: {profile['shape'][1]}")
    print(f"Duplicate rows removed: {duplicates_removed}")
    print(f"Remaining missing values after cleaning: {profile['missing_pct_total']:.2f}%")

    top_category = analysis.revenue_by_category(df).iloc[0]
    print(f"Top category by order value: {top_category['categorie']} ({top_category['montant_commande']:,.0f} EUR)")

    outliers = analysis.price_outliers(df)
    print(f"Price outliers (IQR rule): {len(outliers)} orders ({100 * len(outliers) / len(df):.2f}%)")

    visualization.save_all_figures(df, FIGURES_DIR, DASHBOARD_PATH)
    print(f"Dashboard saved to {DASHBOARD_PATH}")
    print(f"Standalone charts saved to {FIGURES_DIR}")


if __name__ == "__main__":
    run()
