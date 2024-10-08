import streamlit as st
import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL connection using environment variables
connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),           # AWS RDS endpoint
    user=os.getenv("MYSQL_USER"),           # MySQL username
    password=os.getenv("MYSQL_PASSWORD"),   # MySQL password
    database=os.getenv("MYSQL_DATABASE"),   # MySQL database name
    port=int(os.getenv("MYSQL_PORT", 3306)) # MySQL port (default 3306)
)
 
# Load data from MySQL into a DataFrame
query = "SELECT * FROM repositories"
df = pd.read_sql(query, connection)

# Close the connection
connection.close()

# Sidebar for filtering options
st.sidebar.header("Filter Options")

# Filter by programming language
languages = st.sidebar.multiselect("Select Programming Languages", df["programming_language"].unique())

# Search for repository by name
repo_search = st.sidebar.multiselect("Search by Repository Name", df["repository_name"].unique())

# Filter by license type
license_type = st.sidebar.multiselect("Select License Type", df["license_type"].unique())

# Apply filters
if languages:
    df = df[df["programming_language"].isin(languages)]

if repo_search:
    df = df[df["repository_name"].isin(repo_search)]

if license_type:
    df = df[df["license_type"].isin(license_type)]

# Main App Title
st.title(":red[GitHub Repositories Analysis]")

# Calculate average stars and handle NaN values
average_stars = df["number_of_stars"].mean()

# Check if the result is NaN and set to 0 if so
# if pd.isna(average_stars):
#     average_stars = 0

# 1. General Statistics Section
st.header("General Statistics")
st.metric("**Total Repositories**", df.shape[0])
st.metric("**Average Stars**", int(df["number_of_stars"].mean()))
st.metric("**Average Forks**", int(df["number_of_forks"].mean()))

# 2. Popular Programming Languages Section
st.header("Popular Programming Languages")
language_counts = df['programming_language'].value_counts()
st.bar_chart(language_counts)

# 3. Top Repository Owners Section
st.header("Top Repository Owners")
top_owners = df["owner"].value_counts().head(5)
st.bar_chart(top_owners)

# 4. Most and Least Starred Repositories
st.header("Repository with Maximum Stars")
max_stars = df["number_of_stars"].max()
repository_with_max_stars = df[df["number_of_stars"] == max_stars]
st.write(repository_with_max_stars)

# 7. Repository with least Stars
st.header("Repository with least Stars")
min_stars = df["number_of_stars"].min()
repository_with_min_stars = df[df["number_of_stars"] == min_stars]
st.write(repository_with_min_stars)

# 6. Repository Activity Section
st.header("Repository Activity")
# Calculate active days
df["creation_date"] = pd.to_datetime(df["creation_date"])
df["last_updated_date"] = pd.to_datetime(df["last_updated_date"])
df["Active_days"] = (df["last_updated_date"] - df["creation_date"]).dt.days
st.metric("Average Active Days", int(df["Active_days"].mean()))

# 7. Line chart of stars over time
st.line_chart(df.set_index("creation_date")["number_of_stars"])

# 8. Repository Data Table and Download Section
st.header("Repository Data Table")
st.dataframe(df)
st.download_button("Download Data as CSV", df.to_csv(index=False), "repositories.csv")
