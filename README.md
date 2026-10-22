
# E-Commerce Customer Behaviour Analytics Using Big Data

**A data analytics project using Python, Apache Spark, and customer segmentation techniques to investigate e-commerce purchasing patterns and business performance.**

## Overview

E-commerce transaction data can reveal valuable patterns in customer spending, product demand, sales performance, and purchasing frequency. This project develops an analytical workflow for transforming retail transaction records into actionable business insights using Python and Apache Spark.

## Business Objectives

- Analyze revenue trends and sales performance over time.
- Identify top-performing products and countries.
- Examine customer purchasing frequency and spending behaviour.
- Segment customers using Recency, Frequency, and Monetary (RFM) analysis.
- Develop data-driven recommendations to support business decisions.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data analysis and scripting |
| Apache Spark (PySpark) | Data processing and transformation |
| Pandas | Supporting data manipulation |
| Matplotlib | Data visualization |
| Power BI | Business intelligence and dashboarding |
| Git and GitHub | Version control and project documentation |

## Dataset

**UCI Online Retail Dataset**

Source: https://archive.ics.uci.edu/dataset/352/online+retail

The dataset contains historical transactions from a UK-based online retailer. It provides transaction identifiers, product descriptions, quantities, prices, timestamps, and customer information.

The analysis focuses on purchasing behaviour recorded in transaction data, rather than website browsing or clickstream activity.

## Analytical Scope

1. **Data preparation:** Handle missing values, cancelled transactions, and invalid records.
2. **Exploratory analysis:** Examine transaction patterns and the structure of the dataset.
3. **Sales analytics:** Calculate revenue and investigate trends over time.
4. **Product and geographic analysis:** Compare product performance and sales across countries.
5. **Customer analytics:** Measure spending, purchase frequency, and repeat purchasing.
6. **Customer segmentation:** Apply RFM metrics to distinguish customer groups.
7. **Business intelligence:** Present findings through visualizations and, where feasible, a Power BI dashboard.

## Business Value

The analytical workflow is designed to help identify high-value customers, understand product demand, recognize sales trends, and support customer-retention and marketing decisions.

## Reproducibility

The project uses Python-based tools and Apache Spark. The analysis will be documented with setup instructions, processing logic, and the outputs required to reproduce the findings.

## Repository Structure

The repository will organize source code, documentation, visualizations, and dashboard assets separately to support readability and maintainability.

## Data and Scope Limitations

The dataset represents historical transactions and does not capture website sessions, browsing behaviour, or abandoned carts. Findings are therefore limited to behaviour observable from purchase records.
