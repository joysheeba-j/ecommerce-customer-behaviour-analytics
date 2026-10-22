
"""Convert the Online Retail Excel dataset to CSV and inspect it."""

from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession


ROOT = Path(__file__).resolve().parent.parent
EXCEL_FILE = ROOT / "data" / "raw" / "Online Retail.xlsx"
CSV_FILE = ROOT / "data" / "raw" / "online_retail.csv"

EXPECTED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def main():
    # 1. Check that the source dataset exists.
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Excel dataset not found:\n{EXCEL_FILE}\n"
            "Place 'Online Retail.xlsx' in the data/raw folder."
        )

    print("Reading Excel dataset with Pandas...")

    # 2. Load Excel and validate its structure.
    pandas_df = pd.read_excel(EXCEL_FILE, engine="openpyxl")

    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in pandas_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset is missing expected columns: {missing_columns}"
        )

    # Keep the expected columns in a predictable order.
    pandas_df = pandas_df[EXPECTED_COLUMNS]

    # 3. Export CSV. Pandas handles the conversion; Spark does not write files.
    pandas_df.to_csv(
        CSV_FILE,
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d %H:%M:%S",
    )

    print(f"\nExcel file: {EXCEL_FILE.name}")
    print(f"CSV created: {CSV_FILE}")
    print(f"Rows: {len(pandas_df):,}")
    print(f"Columns: {len(pandas_df.columns)}")

    print("\n========== PANDAS DATA TYPES ==========")
    print(pandas_df.dtypes)

    print("\n========== MISSING VALUES ==========")
    print(pandas_df.isna().sum().to_string())

    print("\n========== FIRST 5 ROWS ==========")
    print(pandas_df.head().to_string(index=False))

    # Release the Pandas DataFrame before starting Spark.
    del pandas_df

    # 4. Inspect the exported CSV with Spark.
    spark = (
        SparkSession.builder
        .appName("InspectOnlineRetail")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        spark_df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(CSV_FILE))
        )

        print("\n========== SPARK SCHEMA ==========")
        spark_df.printSchema()

        print("\n========== FIRST 5 ROWS IN SPARK ==========")
        spark_df.show(5, truncate=False)

        print(f"\nSpark row count: {spark_df.count():,}")
        print(f"Spark column count: {len(spark_df.columns)}")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
