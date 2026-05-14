import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import os

st.set_page_config(
    page_title="AI-Powered Product Feedback Insights",
    layout="wide"
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("data/product_info_2.csv")
df = df.dropna(subset=["rating", "reviews", "price_usd", "primary_category"])


def label_sentiment(rating):
    if rating >= 4:
        return "Positive"
    elif rating >= 3:
        return "Neutral"
    else:
        return "Negative"


def generate_ai_feedback(row):
    if row["rating"] < 2.5:
        return "Critical issue: investigate product quality, pricing, or customer satisfaction."
    elif row["rating"] < 3:
        return "Low rating: monitor closely and review customer complaints."
    elif row["rating"] >= 4.5 and row["reviews"] >= 100:
        return "Excellent performance: consider marketing and promotion."
    elif row["rating"] >= 4:
        return "Strong performance: maintain strategy and monitor trends."
    else:
        return "Average performance: evaluate improvement opportunities."


def generate_data_summary(data):
    if len(data) == 0:
        return "No products match the selected filters."

    top_categories = data["primary_category"].value_counts().head(5).to_dict()
    sentiment_distribution = data["sentiment"].value_counts().to_dict()

    top_products = (
        data.sort_values(by=["rating", "reviews"], ascending=False)
        [["product_name", "brand_name", "primary_category", "rating", "reviews", "price_usd"]]
        .head(8)
        .to_dict(orient="records")
    )

    low_products = (
        data.sort_values(by=["rating", "reviews"], ascending=[True, False])
        [["product_name", "brand_name", "primary_category", "rating", "reviews", "price_usd"]]
        .head(8)
        .to_dict(orient="records")
    )

    return f"""
    Total products: {len(data)}
    Average rating: {round(data["rating"].mean(), 2)}
    Total reviews: {int(data["reviews"].sum())}
    Average price: {round(data["price_usd"].mean(), 2)}

    Sentiment distribution:
    {sentiment_distribution}

    Top product categories:
    {top_categories}

    Top-performing products:
    {top_products}

    Low-performing products:
    {low_products}
    """


def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI product management assistant. "
                    "Answer only based on the product data provided. "
                    "Do not invent information. "
                    "Give clear, practical, and actionable recommendations. "
                    "Answer in the same language as the user."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


df["sentiment"] = df["rating"].apply(label_sentiment)
df["ai_feedback"] = df.apply(generate_ai_feedback, axis=1)


st.markdown("""
<style>
.stApp {
    background-color: #f7f8fc;
}

section[data-testid="stSidebar"] {
    background-color: #071427;
}

section[data-testid="stSidebar"] * {
    color: white;
}

.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #071427;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 15px;
    color: #2563eb;
    margin-bottom: 25px;
}

.card {
    padding: 22px;
    border-radius: 14px;
    background-color: white;
    box-shadow: 0px 4px 14px rgba(0, 0, 0, 0.08);
    border: 1px solid #eef2f7;
}

.metric-label {
    font-size: 14px;
    color: #64748b;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #071427;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #071427;
    margin-top: 30px;
    margin-bottom: 10px;
}

.ai-box {
    padding: 22px;
    border-radius: 14px;
    background-color: #ffffff;
    border-left: 5px solid #2563eb;
    box-shadow: 0px 4px 14px rgba(0, 0, 0, 0.08);
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)


st.sidebar.title("Smart Feedback Insights")
st.sidebar.write("AI-powered cosmetics product feedback analytics")

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
    '<div class="main-title">AI-Powered Product Feedback Insights</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Smart analytics dashboard for cosmetics product management</div>',
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
    avg_rating_display = 0 if len(filtered_df) == 0 else filtered_df["rating"].mean()
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Average Rating</div>
        <div class="metric-value">{avg_rating_display:.2f}</div>
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
    needs_review = len(filtered_df[filtered_df["sentiment"] == "Negative"])
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Products Needing Review</div>
        <div class="metric-value">{needs_review:,}</div>
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
        hole=0.55,
        color="sentiment",
        color_discrete_map={
            "Positive": "#22c55e",
            "Neutral": "#facc15",
            "Negative": "#ef4444"
        }
    )

    fig.update_layout(
        paper_bgcolor="#f7f8fc",
        plot_bgcolor="#f7f8fc"
    )

    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("Top Product Categories")

    category_counts = (
        filtered_df["primary_category"]
        .value_counts()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    category_counts.columns = ["category", "count"]

    fig2 = px.bar(
        category_counts,
        x="category",
        y="count",
        color="count",
        color_continuous_scale="Blues"
    )

    fig2.update_layout(
        xaxis_title="Product Category",
        yaxis_title="Number of Products",
        paper_bgcolor="#f7f8fc",
        plot_bgcolor="#f7f8fc"
    )

    st.plotly_chart(fig2, use_container_width=True)


st.subheader("Rating Distribution")

rating_counts = (
    filtered_df["rating"]
    .round(1)
    .value_counts()
    .sort_index()
    .reset_index()
)

rating_counts.columns = ["rating", "count"]

fig3 = px.bar(
    rating_counts,
    x="rating",
    y="count",
    color="count",
    color_continuous_scale="Purples"
)

fig3.update_layout(
    xaxis_title="Rating",
    yaxis_title="Number of Products",
    paper_bgcolor="#f7f8fc",
    plot_bgcolor="#f7f8fc"
)

st.plotly_chart(fig3, use_container_width=True)


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


st.markdown('<div class="section-title">AI Insights & Recommendations</div>', unsafe_allow_html=True)

recommended_df = filtered_df.sort_values(by="rating", ascending=False)

st.dataframe(
    recommended_df[
        ["product_name", "rating", "ai_feedback"]
    ].head(15),
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


st.markdown('<div class="section-title">AI Product Management Assistant</div>', unsafe_allow_html=True)

st.markdown("""
<div class="ai-box">
This assistant helps Product Managers turn product feedback data into practical decisions.
It can generate recommendations or answer questions based on the current dashboard filters.
</div>
""", unsafe_allow_html=True)

data_summary = generate_data_summary(filtered_df)

if st.button("Generate Product Management Recommendations"):
    if len(filtered_df) == 0:
        st.warning("No products match the selected filters.")
    else:
        with st.spinner("Generating AI recommendations..."):
            prompt = f"""
            Based on the product data summary below, provide product management recommendations.

            DATA SUMMARY:
            {data_summary}

            Please include:
            1. Main product management priorities
            2. Risks or problem areas
            3. Opportunities for growth
            4. Suggested next actions

            Keep the answer clear, practical, and useful for a Product Manager.
            """

            ai_result = ask_openai(prompt)
            st.success("AI recommendations generated.")
            st.write(ai_result)


st.subheader("Suggested Questions")

suggested_questions = [
    "Which products should a Product Manager prioritize?",
    "Which product category needs more attention?",
    "What are the main risks in this dataset?",
    "What actions should a Product Manager take next?",
    "Which products have strong performance and should be promoted?",
    "What should be investigated in low-performing products?"
]

selected_question = st.selectbox(
    "Choose a suggested question",
    [""] + suggested_questions
)

custom_question = st.text_input(
    "Or ask your own question about the product data"
)

if st.button("Ask AI"):
    final_question = custom_question if custom_question else selected_question

    if not final_question:
        st.warning("Please select a suggested question or type your own question.")
    elif len(filtered_df) == 0:
        st.warning("No products match the selected filters.")
    else:
        with st.spinner("AI is analyzing the product data..."):
            prompt = f"""
            Use only the product data summary below to answer the question.

            DATA SUMMARY:
            {data_summary}

            QUESTION:
            {final_question}

            If the data does not provide enough information, say that clearly.
            Give a practical answer from a Product Management perspective.
            """

            answer = ask_openai(prompt)
            st.write(answer)