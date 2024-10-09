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
st.sidebar.header(":violet[Filter Options]")
# Filter by programming language
languages = st.sidebar.multiselect("Programming Languages", df["programming_language"].unique())
# Search for repository by name
repo_search = st.sidebar.multiselect("Search by Repository Name", df["repository_name"].unique())
# Filter by owner
owners = st.sidebar.multiselect("Select by Repository Owners", df["owner"].head(10))
# Filter by license type
license_type = st.sidebar.multiselect("Select License Type", df["license_type"].unique())

# Filter by topic
if languages:
    df = df[df["programming_language"].isin(languages)]
if repo_search:
    df = df[df["repository_name"].isin(repo_search)]
if owners:
    df = df[df["owner"].isin(owners)]
if license_type:
    df = df[df["license_type"].isin(license_type)]

# Main App Title
st.title(":red[GitHub Repositories Analysis]")

# Calculate average stars and handle NaN values
average_stars = df["number_of_stars"].mean()
# 1. General Statistics Section
st.header(":green[General Statistics]")
st.metric("**Total Repositories**", df.shape[0])
st.metric("**Average Stars**", int(df["number_of_stars"].mean()))
st.metric("**Average Forks**", int(df["number_of_forks"].mean()))

# Show the selected repositories' URLs
if repo_search:
    st.header(":green[Selected Repository URL]")
    for selected_repo in repo_search:
        repo_info = df[df["repository_name"] == selected_repo]
        if not repo_info.empty:
            repo_url = repo_info["url"].values[0]
            st.markdown(f"<span style='color: red; font-weight: bold;'>{selected_repo}</span>: [Link]({repo_url})", unsafe_allow_html=True)
            #st.markdown(f"**{selected_repo}**: [Link]({repo_url})")
            
# 2. Popular Programming Languages Section
st.header(":green[Popular Programming Languages]")
language_counts = df['programming_language'].value_counts().head()
st.bar_chart(language_counts)

# 3. Top Repository Owners Section
st.header(":green[Top Repository Owners]")
top_owners = df["owner"].value_counts().head()
st.bar_chart(top_owners)

# 4. Most and Least Starred Repositories
st.header(":green[Repository with Maximum Stars]")
max_stars = df["number_of_stars"].max()
repository_with_max_stars = df[df["number_of_stars"] == max_stars]
st.write(repository_with_max_stars)

# 5. Repository with least Stars
st.header(":green[Repository with least Stars]")
min_stars = df["number_of_stars"].min()
repository_with_min_stars = df[df["number_of_stars"] == min_stars]
st.write(repository_with_min_stars)

# 6. Repository Activity Section
st.header(":green[Repository Activity]")
# Calculating active days
df["creation_date"] = pd.to_datetime(df["creation_date"])
df["last_updated_date"] = pd.to_datetime(df["last_updated_date"])
df["Active_days"] = (df["last_updated_date"] - df["creation_date"]).dt.days
st.metric("Average Active Days", int(df["Active_days"].mean()))

# Group by creation date to get total stars and forks over time
trends_df = df.groupby(df["creation_date"].dt.to_period("M")).agg(
    total_stars=('number_of_stars', 'sum'),
    total_forks=('number_of_forks', 'sum')
).reset_index()
# Convert the period back to datetime for plotting
trends_df['creation_date'] = trends_df['creation_date'].dt.to_timestamp()

# 7. Line chart of stars and forks over time
st.header(":green[Trends Over Time]")
st.line_chart(trends_df.set_index("creation_date")[["total_stars", "total_forks"]])

# 8. Star Growth Rate Analysis
st.header(":green[Top Repositories by Star Growth Rate]")
df["age_in_days"] = (pd.Timestamp.now() - df["creation_date"]).dt.days
df["star_growth_rate"] = df["number_of_stars"] / df["age_in_days"]
st.write(df.sort_values(by="star_growth_rate", ascending=False)[["repository_name", "star_growth_rate"]].head())

# 9. Fork-to-Star Ratio
st.header(":green[Repositories with Highest Fork-to-Star Ratio]")
df["fork_to_star_ratio"] = df["number_of_forks"] / df["number_of_stars"]
st.write(df.sort_values(by="fork_to_star_ratio", ascending=False)[["repository_name", "fork_to_star_ratio"]].head())

# 10. Open Issues vs. Last Update
st.header(":green[Repositories with High Open Issues]")
dormant_repos = df[df["last_updated_date"] < pd.Timestamp.now() - pd.Timedelta(days=365)]
st.write(dormant_repos.sort_values(by="number_of_open_issues", ascending=False)[["repository_name", "number_of_open_issues", "last_updated_date"]].head(5))

# 11.  with Highest Issue-to-Star Ratio
st.header(":green[Repositories with Highest Issue-to-Star Ratio]")
df["issue_to_star_ratio"] = df["number_of_open_issues"] / df["number_of_stars"]
st.write(df.sort_values(by="issue_to_star_ratio", ascending=False)[["repository_name","programming_language","issue_to_star_ratio"]].head(5))

# 12. Repositories with Longest Time Since Last Update
st.header(":green[Repositories with Longest Time Since Last Update]")
st.write(df.sort_values(by="last_updated_date", ascending=True)[["repository_name","programming_language", "last_updated_date"]].head(5))

# 13. Repository Data Table and Download Section
st.header(":green[Repository Data Table]")
st.dataframe(df)
st.download_button("Download Data as CSV", df.to_csv(index=False), "repositories.csv")