"""Chart-generation functions for the orders dataset.

All charts share one palette: PRIMARY_COLOR for single-series charts,
CATEGORY_PALETTE for grouped/categorical charts, and OUTLIER_COLOR to flag
anomalies. Every export is saved at 200 DPI or higher.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src import analysis

PRIMARY_COLOR = "#2E5EAA"
ACCENT_COLOR = "#E8743B"
OUTLIER_COLOR = "#C0392B"
CATEGORY_PALETTE = sns.color_palette("crest", 8)
DPI = 200

sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.titlesize"] = 15
plt.rcParams["axes.labelsize"] = 12


def plot_distribution(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Figure:
    """Histogram of order value with a KDE overlay and a skew annotation."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure

    sns.histplot(data=df, x="montant_commande", bins=25, kde=True, color=PRIMARY_COLOR, edgecolor="white", ax=ax)
    skew = df["montant_commande"].skew()
    ax.set_title("Distribution of Order Value")
    ax.set_xlabel("Order value (EUR)")
    ax.set_ylabel("Number of orders")
    ax.annotate(
        f"Skew = {skew:.2f}",
        xy=(0.97, 0.93),
        xycoords="axes fraction",
        ha="right",
        fontsize=11,
        bbox=dict(boxstyle="round", facecolor="white", edgecolor=PRIMARY_COLOR),
    )
    if standalone:
        fig.tight_layout()
    return fig


def plot_comparison_by_category(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Figure:
    """Bar chart of total order value per category, sorted descending, with value labels."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure

    data = analysis.revenue_by_category(df)
    palette = CATEGORY_PALETTE[: len(data)]
    sns.barplot(data=data, x="montant_commande", y="categorie", hue="categorie", palette=palette, legend=False, ax=ax)
    ax.set_title("Total Order Value by Category")
    ax.set_xlabel("Total order value (EUR)")
    ax.set_ylabel("Category")
    for i, value in enumerate(data["montant_commande"]):
        ax.text(value, i, f" {value:,.0f} EUR", va="center", fontsize=10)
    ax.margins(x=0.15)
    if standalone:
        fig.tight_layout()
    return fig


def plot_dispersion_by_region(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Figure:
    """Boxplot of unit price by region, with IQR outliers highlighted."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(12, 6))
    else:
        fig = ax.figure

    order = df.groupby("region")["prix"].median().sort_values(ascending=False).index
    sns.boxplot(
        data=df,
        x="region",
        y="prix",
        order=order,
        hue="region",
        palette=CATEGORY_PALETTE[: len(order)],
        legend=False,
        flierprops=dict(marker="o", markerfacecolor=OUTLIER_COLOR, markeredgecolor=OUTLIER_COLOR, markersize=6),
        ax=ax,
    )
    ax.set_title("Price Dispersion by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Unit price (EUR)")
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_ha("right")

    n_outliers = len(analysis.price_outliers(df))
    ax.annotate(
        f"Red points = outliers (IQR rule)\n{n_outliers} outlier orders overall",
        xy=(0.98, 0.95),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", edgecolor=OUTLIER_COLOR),
    )
    if standalone:
        fig.tight_layout()
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Figure:
    """Annotated correlation heatmap with the upper triangle masked."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(9, 7))
    else:
        fig = ax.figure

    corr = analysis.correlation_matrix(df)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title("Correlation Matrix (Numeric Fields)")
    if standalone:
        fig.tight_layout()
    return fig


def plot_monthly_trend(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Figure:
    """Line chart of total order value per month."""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(11, 6))
    else:
        fig = ax.figure

    trend = analysis.monthly_revenue_trend(df)
    ax.plot(trend["mois"], trend["montant_commande"], color=PRIMARY_COLOR, marker="o", linewidth=2.2)
    ax.fill_between(trend["mois"], trend["montant_commande"], color=PRIMARY_COLOR, alpha=0.12)
    ax.set_title("Monthly Order Value Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total order value (EUR)")
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    if standalone:
        fig.tight_layout()
    return fig


def build_dashboard(df: pd.DataFrame) -> plt.Figure:
    """Combine the four core charts into one 2x2 dashboard figure."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Orders Analysis Dashboard", fontsize=18, fontweight="bold")

    plot_distribution(df, ax=axes[0, 0])
    plot_comparison_by_category(df, ax=axes[0, 1])
    plot_dispersion_by_region(df, ax=axes[1, 0])
    plot_correlation_heatmap(df, ax=axes[1, 1])

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def save_all_figures(df: pd.DataFrame, figures_dir: str | Path, dashboard_path: str | Path) -> None:
    """Generate and save the dashboard plus every standalone chart, at >=150 DPI."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    dashboard_fig = build_dashboard(df)
    dashboard_fig.savefig(dashboard_path, dpi=DPI, bbox_inches="tight")
    plt.close(dashboard_fig)

    exports = [
        ("01_distribution_montant_commande.png", plot_distribution),
        ("02_comparison_by_categorie.png", plot_comparison_by_category),
        ("03_dispersion_by_region.png", plot_dispersion_by_region),
        ("04_correlation_heatmap.png", plot_correlation_heatmap),
        ("05_trend_monthly_revenue.png", plot_monthly_trend),
    ]
    for filename, plot_fn in exports:
        fig = plot_fn(df)
        fig.savefig(figures_dir / filename, dpi=DPI, bbox_inches="tight")
        plt.close(fig)
