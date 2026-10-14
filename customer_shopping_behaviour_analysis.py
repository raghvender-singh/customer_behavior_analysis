
import pandas as pd
from sqlalchemy import create_engine


# ==========================================
# 1. LOAD DATASET
# ==========================================

file_path = r"C:\Users\Gyanendra singh\OneDrive\ドキュメント\customer_shopping_behaviour\customer_shopping_behavior.csv"

df = pd.read_csv(file_path)

print("First 5 rows:")
print(df.head())

print("\nDataset Information:")
df.info()

print("\nDescriptive Statistics:")
print(df.describe())

print("\nMissing Values Before Cleaning:")
print(df.isnull().sum())


# ==========================================
# 2. HANDLE MISSING VALUES
# ==========================================

# Fill missing review ratings with the median
# rating of the corresponding product category.

df["Review Rating"] = (
    df.groupby("Category")["Review Rating"]
    .transform(lambda column: column.fillna(column.median()))
)

print("\nMissing Values After Cleaning:")
print(df.isnull().sum())


# ==========================================
# 3. CLEAN COLUMN NAMES
# ==========================================

df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

# Rename the purchase amount column
df = df.rename(
    columns={"purchase_amount_(usd)": "purchase_amount"}
)

print("\nCleaned Column Names:")
print(df.columns.tolist())


# ==========================================
# 4. CREATE AGE GROUPS
# ==========================================

age_group_labels = [
    "Young Adult",
    "Adult",
    "Middle-aged",
    "Senior"
]

df["age_group"] = pd.qcut(
    df["age"],
    q=4,
    labels=age_group_labels
)

print("\nAge Groups:")
print(df[["age", "age_group"]].head(10))


# ==========================================
# 5. CONVERT PURCHASE FREQUENCY TO DAYS
# ==========================================

frequency_mapping = {
    "Fortnightly": 14,
    "Weekly": 7,
    "Monthly": 30,
    "Quarterly": 90,
    "Bi-Weekly": 14,
    "Annually": 365,
    "Every 3 months": 90
}

df["purchase_frequency_days"] = (
    df["frequency_of_purchases"].map(frequency_mapping)
)

print("\nPurchase Frequency in Days:")
print(
    df[
        ["frequency_of_purchases", "purchase_frequency_days"]
    ].head(10)
)


# ==========================================
# 6. REMOVE REDUNDANT COLUMN
# ==========================================

# Check whether both columns contain identical values.
columns_match = (
    df["discount_applied"] == df["promo_code_used"]
).all()

print("\nDo discount_applied and promo_code_used match?")
print(columns_match)

# Remove the redundant column.
df = df.drop(columns=["promo_code_used"])

print("\nFinal Columns:")
print(df.columns.tolist())


# ==========================================
# 7. CONNECT TO MYSQL
# ==========================================

username = "root"
password = "password"
host = "localhost"
port = 3306
database = "customer_behavior"

connection_url = (
    f"mysql+pymysql://{username}:{password}"
    f"@{host}:{port}/{database}"
)

engine = create_engine(connection_url)


# ==========================================
# 8. UPLOAD DATA TO MYSQL
# ==========================================

table_name = "customer_shopping"

df.to_sql(
    name=table_name,
    con=engine,
    if_exists="replace",
    index=False
)

print(f"\nData successfully uploaded to {database}.{table_name}")


# ==========================================
# 9. VERIFY UPLOADED DATA
# ==========================================

query = f"SELECT * FROM {table_name} LIMIT 5"

mysql_df = pd.read_sql(query, con=engine)

print("\nSample Data Retrieved from MySQL:")
print(mysql_df)

engine.dispose()
