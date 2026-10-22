
"""Clean Online Retail transactions and calculate business metrics."""

from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "raw" / "online_retail.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


def save_spark_result(spark_df, filename):
    """Export a manageable aggregate Spark DataFrame through Pandas."""
    output_file = OUTPUT_DIR / filename

    pandas_df = spark_df.toPandas()
    pandas_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Saved: {output_file.name} ({len(pandas_df):,} rows)")
    return pandas_df


def main():
    # 1. Validate input and create the output directory.
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input CSV not found:\n{INPUT_FILE}\n"
            "Run src/01_inspect_data.py first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    spark = (
        SparkSession.builder
        .appName("EcommerceCustomerBehaviourAnalysis")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        # 2. Read the source data.
        raw = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(INPUT_FILE))
        )

        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in raw.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Dataset is missing required columns: {missing_columns}"
            )

        raw = raw.select(*REQUIRED_COLUMNS).cache()
        input_rows = raw.count()

        # 3. Normalize types before filtering and calculating metrics.
        df = (
            raw
            .withColumn("InvoiceNo", F.col("InvoiceNo").cast("string"))
            .withColumn("CustomerID", F.col("CustomerID").cast("long"))
            .withColumn("Quantity", F.col("Quantity").cast("long"))
            .withColumn("UnitPrice", F.col("UnitPrice").cast("double"))
            .withColumn(
                "ParsedInvoiceDate",
                F.to_timestamp(F.col("InvoiceDate"))
            )
        )

        # 4. Calculate data-quality counts in one aggregation.
        quality = df.agg(
            F.count("*").alias("InputRows"),
            F.sum(
                F.when(F.col("CustomerID").isNull(), 1).otherwise(0)
            ).alias("MissingCustomerIDRows"),
            F.sum(
                F.when(F.col("InvoiceNo").startswith("C"), 1).otherwise(0)
            ).alias("CancelledInvoiceRows"),
            F.sum(
                F.when(F.col("Quantity") <= 0, 1).otherwise(0)
            ).alias("NonpositiveQuantityRows"),
            F.sum(
                F.when(F.col("UnitPrice") <= 0, 1).otherwise(0)
            ).alias("NonpositiveUnitPriceRows"),
            F.sum(
                F.when(F.col("ParsedInvoiceDate").isNull(), 1).otherwise(0)
            ).alias("InvalidInvoiceDateRows"),
        ).first().asDict()

        print("\n========== DATA QUALITY ==========")
        for metric, value in quality.items():
            print(f"{metric}: {value:,}")

        # 5. Keep positive, non-cancelled sales with valid customer IDs
        #    and parseable invoice dates.
        sales = (
            df.filter(
                F.col("CustomerID").isNotNull()
                & F.col("InvoiceNo").isNotNull()
                & ~F.col("InvoiceNo").startswith("C")
                & (F.col("Quantity") > 0)
                & (F.col("UnitPrice") > 0)
                & F.col("ParsedInvoiceDate").isNotNull()
            )
            .withColumn(
                "Revenue",
                F.round(F.col("Quantity") * F.col("UnitPrice"), 2)
            )
            .withColumn(
                "InvoiceMonth",
                F.date_format("ParsedInvoiceDate", "yyyy-MM")
            )
            .cache()
        )

        valid_rows = sales.count()

        totals = sales.agg(
            F.countDistinct("CustomerID").alias("Customers"),
            F.countDistinct("InvoiceNo").alias("Invoices"),
            F.round(F.sum("Revenue"), 2).alias("TotalRevenue"),
            F.round(F.avg("Revenue"), 2).alias("AverageLineRevenue"),
        ).first()

        customer_count = totals["Customers"]
        invoice_count = totals["Invoices"]
        total_revenue = totals["TotalRevenue"]

        print("\n========== CLEANED DATA ==========")
        print(f"Valid sales rows: {valid_rows:,}")
        print(f"Distinct customers: {customer_count:,}")
        print(f"Distinct invoices: {invoice_count:,}")
        print(f"Total revenue: {total_revenue:,.2f}")
        print(f"Average transaction-line revenue: {totals['AverageLineRevenue']:,.2f}")

        # 6. Build reusable business analysis tables.
        monthly_revenue = (
            sales.groupBy("InvoiceMonth")
            .agg(
                F.round(F.sum("Revenue"), 2).alias("Revenue"),
                F.countDistinct("InvoiceNo").alias("Invoices"),
                F.countDistinct("CustomerID").alias("Customers"),
            )
            .orderBy("InvoiceMonth")
        )

        country_revenue = (
            sales.groupBy("Country")
            .agg(
                F.round(F.sum("Revenue"), 2).alias("Revenue"),
                F.countDistinct("InvoiceNo").alias("Invoices"),
                F.countDistinct("CustomerID").alias("Customers"),
            )
            .orderBy(F.desc("Revenue"))
        )

        product_revenue = (
            sales.groupBy("StockCode", "Description")
            .agg(
                F.sum("Quantity").alias("UnitsSold"),
                F.round(F.sum("Revenue"), 2).alias("Revenue"),
                F.countDistinct("InvoiceNo").alias("Invoices"),
            )
            .orderBy(F.desc("Revenue"))
        )

        customer_revenue = (
            sales.groupBy("CustomerID")
            .agg(
                F.countDistinct("InvoiceNo").alias("Orders"),
                F.sum("Quantity").alias("UnitsPurchased"),
                F.round(F.sum("Revenue"), 2).alias("TotalRevenue"),
                F.round(
                    F.sum("Revenue") / F.countDistinct("InvoiceNo"), 2
                ).alias("RevenuePerOrder"),
            )
            .orderBy(F.desc("TotalRevenue"))
        )

        # 7. Print concise summaries.
        print("\n========== MONTHLY REVENUE ==========")
        monthly_revenue.show(20, truncate=False)

        print("\n========== TOP 10 COUNTRIES ==========")
        country_revenue.show(10, truncate=False)

        print("\n========== TOP 10 PRODUCTS ==========")
        product_revenue.show(10, truncate=False)

        print("\n========== TOP 10 CUSTOMERS ==========")
        customer_revenue.show(10, truncate=False)

        # 8. Save a data-quality report.
        quality_df = pd.DataFrame([
            {"Metric": metric, "Value": int(value or 0)}
            for metric, value in quality.items()
        ])
        quality_df.to_csv(
            OUTPUT_DIR / "data_quality_report.csv",
            index=False,
            encoding="utf-8-sig",
        )
        print("Saved: data_quality_report.csv")

        # 9. Save headline KPIs.
        kpi_df = pd.DataFrame([
            {"Metric": "Input rows", "Value": input_rows},
            {"Metric": "Valid sales rows", "Value": valid_rows},
            {"Metric": "Distinct customers", "Value": customer_count},
            {"Metric": "Distinct invoices", "Value": invoice_count},
            {"Metric": "Total revenue", "Value": total_revenue},
            {
                "Metric": "Average transaction-line revenue",
                "Value": totals["AverageLineRevenue"],
            },
        ])
        kpi_df.to_csv(
            OUTPUT_DIR / "kpi_summary.csv",
            index=False,
            encoding="utf-8-sig",
        )
        print("Saved: kpi_summary.csv")

        # 10. Export aggregate tables using Pandas.
        save_spark_result(monthly_revenue, "monthly_revenue.csv")
        save_spark_result(country_revenue, "country_revenue.csv")
        save_spark_result(product_revenue, "product_revenue.csv")
        save_spark_result(customer_revenue, "customer_revenue.csv")

        print("\nAnalysis completed successfully.")

        sales.unpersist()
        raw.unpersist()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
