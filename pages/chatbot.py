import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trip Data Chatbot", page_icon="🤖", layout="wide")

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
    <style>
        .stApp { background-color: #f7f8fc; color: #2d2d2d; }
        [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e8e8f0; }
        h1, h2, h3 { color: #2d2d2d !important; font-weight: 600 !important; }
        hr { border-color: #e8e8f0; }

        /* Suggestion buttons */
        .stButton button {
            background-color: #ffffff;
            border: 1px solid #e8e8f0;
            border-radius: 20px;
            color: #2d2d2d;
            font-size: 13px;
            padding: 6px 16px;
            transition: all 0.2s;
        }
        .stButton button:hover {
            background-color: #b8c0ff;
            border-color: #b8c0ff;
            color: #2d2d2d;
        }
    </style>
""", unsafe_allow_html=True)

COLORS = ["#b8c0ff", "#ffc8dd", "#caffbf", "#ffd6a5", "#a0c4ff", "#bdb2ff"]
CHART_BG = "#ffffff"
PAPER_BG = "#ffffff"
FONT_COLOR = "#2d2d2d"
GRID_COLOR = "#f0f0f5"

def style_chart(fig):
    fig.update_layout(
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font_color=FONT_COLOR,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
    return fig

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    customers = pd.read_csv("datasets/customers.csv")
    ratings = pd.read_csv("datasets/ratings.csv")
    df = trips.merge(cars, left_on="car_id", right_on="id", suffixes=("", "_car"))
    df = df.merge(customers, left_on="customer_id", right_on="id", suffixes=("", "_customer"))
    df = df.merge(ratings, left_on="id", right_on="trip_id", how="left")
    df['pickup_time'] = pd.to_datetime(df['pickup_time'])
    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────
st.markdown("## 🤖 Trip Data Chatbot")
st.markdown("<p style='color:#9a9ab0; margin-top:-15px;'>Ask me anything about the car sharing data</p>", unsafe_allow_html=True)
st.divider()

# ── Suggested questions ───────────────────────────────────────
st.markdown("<p style='color:#9a9ab0; font-size:13px;'>💡 Try one of these</p>", unsafe_allow_html=True)

suggestions = [
    "How many trips in total?",
    "What is the total revenue?",
    "Show revenue by brand",
    "Show trips over time",
    "What is the average rating?",
    "Show top 10 models by revenue",
    "What is the average distance?",
    "How many unique customers?",
]

# ── Initialize chat history ───────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ── Suggestion buttons ────────────────────────────────────────
cols = st.columns(4)
for i, suggestion in enumerate(suggestions):
    with cols[i % 4]:
        if st.button(suggestion, key=f"btn_{i}"):
            st.session_state.pending_query = suggestion

st.divider()

# ── Display past messages ─────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "chart" in message:
            st.plotly_chart(message["chart"], use_container_width=True)

# ── Process query ─────────────────────────────────────────────
def process_query(user_query):
    query = user_query.lower()
    response = "Sorry, I didn't understand that. Try one of the suggested questions above!"
    chart = None

    if "how many trips" in query or "total trips" in query:
        response = f"There are **{len(df):,} trips** recorded in the dataset."

    elif "total revenue" in query:
        total = df["revenue"].sum()
        response = f"The total revenue across all trips is **€{total:,.2f}**."

    elif "revenue by brand" in query or "show revenue by brand" in query:
        response = "Here's the average revenue per trip by car brand:"
        rev_brand = (
            df.groupby("brand")["revenue"]
            .mean()
            .reset_index()
            .sort_values("revenue", ascending=False)
        )
        fig = px.bar(
            rev_brand, x="brand", y="revenue",
            color="brand",
            color_discrete_sequence=COLORS,
            title="Avg Revenue by Brand (€)"
        )
        chart = style_chart(fig)

    elif "trips over time" in query or "show trips over time" in query:
        response = "Here's how the number of trips evolved over time:"
        trips_time = (
            df.assign(date=df['pickup_time'].dt.date)
            .groupby("date")
            .size()
            .reset_index(name="Trips")
        )
        fig = px.line(
            trips_time, x="date", y="Trips",
            color_discrete_sequence=["#b8c0ff"],
            title="Trips Over Time"
        )
        fig.update_traces(fill='tozeroy', fillcolor='rgba(184,192,255,0.15)')
        chart = style_chart(fig)

    elif "average rating" in query or "avg rating" in query:
        avg = df["rating"].mean()
        response = f"The average trip rating is **{avg:.2f} / 5** ⭐"

    elif "top 10 models" in query or "top models" in query:
        response = "Here are the top 10 car models by average revenue:"
        top_models = (
            df.groupby("model")["revenue"]
            .mean()
            .reset_index()
            .sort_values("revenue", ascending=False)
            .head(10)
        )
        fig = px.bar(
            top_models, x="revenue", y="model",
            orientation="h",
            color="model",
            color_discrete_sequence=COLORS,
            title="Top 10 Models by Avg Revenue (€)"
        )
        chart = style_chart(fig)

    elif "average distance" in query or "avg distance" in query:
        avg = df["distance"].mean()
        response = f"The average trip distance is **{avg:.2f} km**."

    elif "unique customers" in query or "how many customers" in query:
        unique = df["customer_id"].nunique()
        response = f"There are **{unique:,}** unique customers in the dataset."

    return response, chart

# ── Handle button click or typed input ────────────────────────
user_query = st.chat_input("Or type your question here...")

active_query = st.session_state.pending_query or user_query
st.session_state.pending_query = None

if active_query:
    st.session_state.messages.append({"role": "user", "content": active_query})
    with st.chat_message("user"):
        st.write(active_query)

    response, chart = process_query(active_query)

    message = {"role": "assistant", "content": response}
    if chart:
        message["chart"] = chart

    st.session_state.messages.append(message)
    with st.chat_message("assistant"):
        st.write(response)
        if chart:
            st.plotly_chart(chart, use_container_width=True)