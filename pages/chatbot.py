import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trip Data Chatbot", page_icon="🤖")

# ── Load and merge all data ───────────────────────────────────
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

st.title("🤖 Trip Data Chatbot")
st.write("Ask me about trips, revenue, distances, car brands or ratings!")

# ── Initialize chat history ───────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display past messages ─────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ── Handle user input ─────────────────────────────────────────
user_query = st.chat_input("Type your question...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    query = user_query.lower()
    response = "Sorry, I didn't understand that. Try asking about: total revenue, total trips, average distance, top car brand, average rating, or unique customers."

    if "total revenue" in query:
        total = df["revenue"].sum()
        response = f"The total revenue across all trips is **{total:,.2f} €**."

    elif "total trips" in query or "how many trips" in query:
        response = f"There are **{len(df):,} trips** recorded in the dataset."

    elif "average distance" in query or "avg distance" in query:
        avg = df["distance"].mean()
        response = f"The average trip distance is **{avg:.2f} km**."

    elif "average revenue" in query or "avg revenue" in query:
        avg = df["revenue"].mean()
        response = f"The average revenue per trip is **{avg:.2f} €**."

    elif "top car brand" in query or "most popular brand" in query:
        top_brand = df["brand"].value_counts().idxmax()
        count = df["brand"].value_counts().max()
        response = f"The most used car brand is **{top_brand}** with **{count:,}** trips."

    elif "average rating" in query or "avg rating" in query:
        avg = df["rating"].mean()
        response = f"The average trip rating is **{avg:.2f} / 5**."

    elif "unique customers" in query or "how many customers" in query:
        unique = df["customer_id"].nunique()
        response = f"There are **{unique:,}** unique customers in the dataset."

    elif "total distance" in query:
        total = df["distance"].sum()
        response = f"The total distance across all trips is **{total:,.2f} km**."

    elif "best rated brand" in query:
        best = df.groupby("brand")["rating"].mean().idxmax()
        score = df.groupby("brand")["rating"].mean().max()
        response = f"The best rated car brand is **{best}** with an average rating of **{score:.2f} / 5**."

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)