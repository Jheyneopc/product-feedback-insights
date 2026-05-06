import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Smart Feedback Insights",
    layout="wide"
)

df = pd.read_csv("data/product_info_2.csv")

df = df.dropna(subset=["rating", "reviews", "price_usd", "primary_category"])


def label_sentiment(rating):
    if rating >= 4:
        return "Positive"
    elif rating >= 3:
        return "Neutral"
    else:
        return "Negative"


def generate_recommendation(row):
    if row["rating"] >= 4.5 and row["reviews"] > 100:
        return "High performance: consider promoting this product"
    elif row["rating"] >= 3:
        return "Moderate performance: monitor feedback"
    else:
        return "Low performance: investigate issues"


def generate_ai_feedback(row):
    if row["rating"] < 2.5:
        return "Critical performance issue. Immediate action required on product quality or pricing."
    elif row["rating"] < 3:
        return "Low rating detected. Monitor closely and investigate customer complaints."
    elif row["rating"] >= 4.5 and row["reviews"] >= 100:
        return "Excellent performance. Consider scaling marketing and promotions."
    elif row["rating"] >= 4:
        return "Strong product performance. Maintain strategy and monitor trends."
    else:
        return "Average performance. Evaluate customer feedback for improvement opportunities."


df["sentiment"] = df["rating"].apply(label_sentiment)
df["recommendation"] = df.apply(generate_recommendation, axis=1)
df["ai_feedback"] = df.apply(generate_ai_feedback, axis=1)

st.markdown("""
<style>
.main {
    background-color: #fbf8ff;
}

.big-title {
    font-size: 38px;
    font-weight: 800;
    color: #32235c;
}

.subtitle {
    font-size: 18px;
    color: #d9468c;
    margin-bottom: 25px;
}

.card {
    padding: 20px;
    border-radius: 18px;
    background-color: white;
    box-shadow: 0px 4px 14px rgba(80, 50, 120, 0.12);
    border: 1px solid #eee4ff;
}

.metric-label {
    font-size: 15px;
    color: #6b5b85;
}

.metric-value {
    font-size: 32px;
    font-weight: 800;
    color: #32235c;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #32235c;
    margin-top: 30px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Smart Feedback Insights")
st.sidebar.write("Cosmetics Product Feedback Analytics")

categories = ["All"] + sorted(df["primary_category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Filter by Product Category", categories)

sentiments = ["All", "Positive", "Neutral", "Negative"]
selected_sentiment = st.sidebar.selectbox("Filter by Sentiment", sentiments)

min_rating = st.sidebar.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.1)

filtered_df = df.copy()

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["primary_category"] == selected_category]

if selected_sentiment != "All":
    filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]

filtered_df = filtered_df[filtered_df["rating"] >= min_rating]

st.markdown(
    '<div class="big-title">Smart Feedback Insights for Product Management</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Cosmetics product feedback analytics dashboard</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Total Products</div>
        <div class="metric-value">{len(filtered_df):,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Average Rating</div>
        <div class="metric-value">{filtered_df["rating"].mean():.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Total Reviews</div>
        <div class="metric-value">{int(filtered_df["reviews"].sum()):,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Selected Products</div>
        <div class="metric-value">{len(filtered_df):,}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title">Dashboard Overview</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Sentiment Distribution")

    sentiment_counts = filtered_df["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]

    fig = px.pie(
        sentiment_counts,
        names="sentiment",
        values="count",
        hole=0.5
    )

    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("Top Product Categories")

    st.bar_chart(
        filtered_df["primary_category"]
        .value_counts()
        .sort_values(ascending=False)
        .head(10)
    )

st.subheader("Rating Distribution")

st.bar_chart(
    filtered_df["rating"]
    .round(1)
    .value_counts()
    .sort_index()
)

st.markdown('<div class="section-title">Reviews Explorer</div>', unsafe_allow_html=True)

st.dataframe(
    filtered_df[[
        "product_name",
        "brand_name",
        "primary_category",
        "rating",
        "reviews",
        "price_usd",
        "sentiment"
    ]].head(20),
    use_container_width=True
)

st.markdown('<div class="section-title">AI-Style Recommendations</div>', unsafe_allow_html=True)

recommended_df = filtered_df.sort_values(by="rating", ascending=False)

rec_col1, rec_col2 = st.columns(2)

with rec_col1:
    st.subheader("Recommended Actions")

    st.dataframe(
        recommended_df[[
            "product_name",
            "rating",
            "reviews",
            "recommendation"
        ]].head(15),
        use_container_width=True
    )

with rec_col2:
    st.subheader("AI Feedback")

    st.dataframe(
        recommended_df[[
            "product_name",
            "rating",
            "ai_feedback"
        ]].head(15),
        use_container_width=True
    )

st.markdown('<div class="section-title">Low-Performing Products</div>', unsafe_allow_html=True)

low_df = filtered_df[filtered_df["sentiment"] == "Negative"].sort_values(
    by="rating",
    ascending=True
)

st.dataframe(
    low_df[[
        "product_name",
        "brand_name",
        "rating",
        "reviews",
        "recommendation",
        "ai_feedback"
    ]].head(10),
    use_container_width=True
)

st.markdown('<div class="section-title">Key Insights</div>', unsafe_allow_html=True)

if len(filtered_df) > 0:
    top_category = filtered_df["primary_category"].value_counts().idxmax()
    avg_rating = round(filtered_df["rating"].mean(), 2)

    positive_percentage = round(
        (len(filtered_df[filtered_df["sentiment"] == "Positive"]) / len(filtered_df)) * 100,
        2
    )

    st.info(f"The dominant product category is {top_category}.")
    st.info(f"The average product rating is {avg_rating}.")
    st.info(f"{positive_percentage}% of the selected products are classified as positive.")
    st.info("Low-performing products should be reviewed to identify possible quality, pricing, or customer satisfaction issues.")
else:
    st.warning("No products match the selected filters.")