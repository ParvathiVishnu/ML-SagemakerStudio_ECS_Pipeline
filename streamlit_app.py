import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# --- Database credentials (secure these in production!)
DB_HOST = "bluesky-sentiment-db-1.c1uywao6o3gp.ap-south-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "admin_1"
DB_PASS = "database"

st.set_page_config(page_title="Bluesky Sentiment Dashboard", layout="wide")
st.title("🌤️ Bluesky Sentiment Dashboard")
st.caption("Visualizing real sentiment predictions from RDS")

# --- Sidebar Filters
with st.sidebar:
    st.header("🔎 Filters")
    sentiment_filter = st.multiselect(
        "Sentiment", options=["positive", "neutral", "negative"],
        default=["positive", "neutral", "negative"]
    )
    
    time_range = st.selectbox("Time Window", ["All time", "Today", "Last 7 days", "Last 30 days"])

# --- SQL Query Builder
def build_query():
    base = "SELECT post_text, sentiment, confidence_score, created_at FROM posts WHERE TRUE"
    filters, params = [], []

    if sentiment_filter:
        filters.append("sentiment IN %s")
        params.append(tuple(sentiment_filter))

    if sentiment_filter:
        filters.append("sentiment IN %s")
        params.append(tuple(sentiment_filter))

    if time_range == "Today":
        filters.append("created_at >= %s")
        params.append(datetime.now().date())
    elif time_range == "Last 7 days":
        filters.append("created_at >= %s")
        params.append(datetime.now().date() - timedelta(days=7))
    elif time_range == "Last 30 days":
        filters.append("created_at >= %s")
        params.append(datetime.now().date() - timedelta(days=30))

    if filters:
        base += " AND " + " AND ".join(filters)

    base += " ORDER BY created_at DESC LIMIT 2000"
    return base, params

# --- Load data
try:
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    query, params = build_query()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
except Exception as e:
    st.error(f"❌ Failed to connect to RDS: {e}")
    df = pd.DataFrame()

# --- Format and display
if not df.empty:
    st.success(f"📬 Showing {len(df)} results")

    # Clean & format columns
    df["confidence_score"] = (df["confidence_score"] * 100).round(1)
    df["confidence_label"] = df["confidence_score"].astype(str) + "%"

    emoji = {"positive": "😊", "neutral": "😐", "negative": "😠"}
    df["sentiment_label"] = df["sentiment"].map(lambda x: f"{emoji.get(x, '')} {x.capitalize()}")

    display_df = df[["post_text", "sentiment_label", "confidence_label", "created_at"]]
    display_df.columns = ["Post", "Sentiment", "Confidence", "Created At"]

    def highlight_sentiment(val):
        base = val.split()[1].lower()
        color_map = {"positive": "#6ee7b7", "neutral": "#fde68a", "negative": "#f87171"}
        return f"background-color: {color_map.get(base, '')}"

    st.dataframe(
        display_df.style.applymap(highlight_sentiment, subset=["Sentiment"]),
        use_container_width=True,
        height=450
    )

    # --- Charts
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Sentiment Counts")
        fig, ax = plt.subplots()
        sns.countplot(data=df, x="sentiment", palette={
            "positive": "#6ee7b7",
            "neutral": "#fde68a",
            "negative": "#f87171"
        }, order=["positive", "neutral", "negative"])
        ax.set_xlabel("")
        ax.set_ylabel("Post Count")
        st.pyplot(fig)

    with col2:
        st.subheader("🥧 Sentiment Share")
        pie_data = df["sentiment"].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%",
                colors=[{"positive": "#6ee7b7", "neutral": "#fde68a", "negative": "#f87171"}[k] for k in pie_data.index])
        ax2.axis("equal")
        st.pyplot(fig2)

   
else:
    st.info("No matching posts found for current filters.")



