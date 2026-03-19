import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Car Sharing Dashboard",
    page_icon="🚗",
    layout="wide"
)

# ── Load and merge all data ───────────────────────────────────
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    customers = pd.read_csv("datasets/customers.csv")
    ratings = pd.read_csv("datasets/ratings.csv")

    # Merge trips with cars to get brand, model, etc.
    df = trips.merge(cars, left_on="car_id", right_on="id", suffixes=("", "_car"))

    # Merge with customers to get city, name, etc.
    df = df.merge(customers, left_on="customer_id", right_on="id", suffixes=("", "_customer"))

    # Merge with ratings
    df = df.merge(ratings, left_on="id", right_on="trip_id", how="left")

    # Convert dates
    df['pickup_time'] = pd.to_datetime(df['pickup_time'])

    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("Filters")

car_brands = st.sidebar.multiselect(
    "Select Car Brand(s)",
    options=sorted(df["brand"].unique()),
    default=sorted(df["brand"].unique())
)

cities = st.sidebar.multiselect(
    "Select City/Cities",
    options=sorted(df["city_id_customer"].unique()),
    default=sorted(df["city_id_customer"].unique())
)

min_date = df['pickup_time'].dt.date.min()
max_date = df['pickup_time'].dt.date.max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# ── Apply filters ─────────────────────────────────────────────
filtered_df = df[
    (df["brand"].isin(car_brands)) &
    (df["city_id_customer"].isin(cities))
]

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['pickup_time'].dt.date >= start_date) &
        (filtered_df['pickup_time'].dt.date <= end_date)
    ]

# ── Title ─────────────────────────────────────────────────────
st.title("Car Sharing Analytics Dashboard")
st.markdown("Explore operational data from our car sharing service.")

# ── KPI Metrics ───────────────────────────────────────────────
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Trips", f"{len(filtered_df):,}")
with col2:
    st.metric("Unique Customers", f"{filtered_df['customer_id'].nunique():,}")
with col3:
    total_distance = filtered_df['distance'].sum() / 1000
    st.metric("Total Distance", f"{total_distance:.2f} K km")
with col4:
    avg_revenue = filtered_df['revenue'].mean()
    st.metric("Avg Revenue / Trip", f"{avg_revenue:.2f} €")

st.divider()

# ── Charts row 1 ──────────────────────────────────────────────
st.subheader("Trips & Revenue Over Time")
col_left, col_right = st.columns(2)

with col_left:
    trips_over_time = (
        filtered_df
        .assign(date=filtered_df['pickup_time'].dt.date)
        .groupby("date")
        .size()
        .rename("Number of Trips")
    )
    st.line_chart(trips_over_time)

with col_right:
    revenue_over_time = (
        filtered_df
        .assign(date=filtered_df['pickup_time'].dt.date)
        .groupby("date")["revenue"]
        .sum()
        .rename("Total Revenue (€)")
    )
    st.line_chart(revenue_over_time)

st.divider()

# ── Charts row 2 ──────────────────────────────────────────────
st.subheader("Trips by Car Brand & Average Rating")
col_a, col_b = st.columns(2)

with col_a:
    st.write("**Trips by Car Brand**")
    brand_counts = filtered_df['brand'].value_counts()
    st.bar_chart(brand_counts)

with col_b:
    st.write("**Average Rating by Car Brand**")
    avg_rating = filtered_df.groupby("brand")["rating"].mean().sort_values(ascending=False)
    st.bar_chart(avg_rating)

st.divider()

# ── Revenue by car model ──────────────────────────────────────
st.subheader("Average Revenue by Car Model")
avg_rev_model = (
    filtered_df
    .groupby("model")["revenue"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(avg_rev_model)

st.divider()

# ── Raw data ──────────────────────────────────────────────────
with st.expander("View Raw Data"):
    st.dataframe(
        filtered_df[['pickup_time', 'brand', 'model', 'distance', 'revenue', 'rating', 'name']],
        use_container_width=True
    )