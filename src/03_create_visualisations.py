
"""Create portfolio charts from the processed analytics CSV files."""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "outputs" / "figures"


def save_monthly_revenue():
    df = pd.read_csv(DATA_DIR / "monthly_revenue.csv")
    df = df.sort_values("InvoiceMonth")

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        df["InvoiceMonth"],
        df["Revenue"],
        marker="o",
        linewidth=2,
    )
    ax.set_title("Monthly Revenue Trend", fontsize=16)
    ax.set_xlabel("Invoice month")
    ax.set_ylabel("Revenue")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "monthly_revenue.png", dpi=200)
    plt.close(fig)


def save_top_countries():
    df = pd.read_csv(DATA_DIR / "country_revenue.csv")
    df = df.nlargest(10, "Revenue").sort_values("Revenue")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df["Country"], df["Revenue"])
    ax.set_title("Top 10 Countries by Revenue", fontsize=16)
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Country")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "top_countries_revenue.png", dpi=200)
    plt.close(fig)


def save_top_products():
    df = pd.read_csv(DATA_DIR / "product_revenue.csv")
    df = df.nlargest(10, "Revenue").sort_values("Revenue")

    labels = df["Description"].fillna("Unknown").str.slice(0, 35)

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(labels, df["Revenue"])
    ax.set_title("Top 10 Products by Revenue", fontsize=16)
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Product")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "top_products_revenue.png", dpi=200)
    plt.close(fig)


def save_customer_distribution():
    df = pd.read_csv(DATA_DIR / "customer_revenue.csv")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df["TotalRevenue"], bins=40)
    ax.set_title("Distribution of Customer Revenue", fontsize=16)
    ax.set_xlabel("Customer revenue")
    ax.set_ylabel("Number of customers")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "customer_revenue_distribution.png", dpi=200)
    plt.close(fig)


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    required_files = [
        "monthly_revenue.csv",
        "country_revenue.csv",
        "product_revenue.csv",
        "customer_revenue.csv",
    ]

    missing = [
        filename for filename in required_files
        if not (DATA_DIR / filename).exists()
    ]

    if missing:
        raise FileNotFoundError(
            f"Missing processed files: {missing}\n"
            "Run src/02_clean_and_analyse.py first."
        )

    save_monthly_revenue()
    save_top_countries()
    save_top_products()
    save_customer_distribution()

    print("\nCharts created successfully:")
    for path in sorted(FIGURES_DIR.glob("*.png")):
        print(f" - {path}")


if __name__ == "__main__":
    main()
