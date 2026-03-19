import streamlit as st
import pandas as pd
import plotly.express as px

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Car Sharing Dashboard",
    page_icon="🚗",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
    <style>
        .stApp {
            background-color: #f7f8fc;
            color: #2d2d2d;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e8e8f0;
        }

        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e8e8f0;
            border-radius: 12px;
            padding: 16px;
        }

        [data-testid="stMetricLabel"] {
            color: #9a9ab0 !important;
            font-size: 13px !important;
        }

        [data-testid="stMetricValue"] {
            color: #2d2d2d !important;
            font-size: 26px !important;
            font-weight: 700 !important;
        }

        h1, h2, h3 {
            color: #2d2d2d !important;
            font-weight: 600 !important;
        }

        hr {
            border-color: #e8e8f0;
        }

        .stMultiSelect span {
            background-color: #b8c0ff !important;
            color: #2d2d2d !important;
        }

        /* Make dataframe look cleaner */
        .stDataFrame {
            border-radius: 12px;
            border: 1px solid #e8e8f0;
        }
    </style>
""", unsafe_allow_html=True)

# ── Color palette (pastel) ────────────────────────────────────
COLORS = [
    "#b8c0ff", "#ffc8dd", "#caffbf", "#ffd6a5", "#a0c4ff", "#bdb2ff",
    "#ffadad", "#fdffb6", "#c8b6ff", "#b9fbc0", "#fde4cf", "#f1c0e8",
    "#a2d2ff", "#cdb4db", "#bee1e6", "#f0efeb", "#dfe7fd"
]
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

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.markdown("## 🚗 Filters")
st.sidebar.markdown("---")

car_brands = st.sidebar.multiselect(
    "Car Brand",
    options=sorted(df["brand"].unique()),
    default=sorted(df["brand"].unique())
)

cities = st.sidebar.multiselect(
    "City",
    options=sorted(df["city_id_customer"].unique()),
    default=sorted(df["city_id_customer"].unique())
)

min_date = df['pickup_time'].dt.date.min()
max_date = df['pickup_time'].dt.date.max()
date_range = st.sidebar.date_input(
    "Date Range",
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

# ── Header ────────────────────────────────────────────────────
st.markdown("## 🚗 Car Sharing Dashboard")
st.markdown("<p style='color:#9a9ab0; margin-top:-15px;'>Operational analytics for our car sharing service</p>", unsafe_allow_html=True)

st.divider()

# ── KPI Metrics ───────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🛣️ Total Trips", f"{len(filtered_df):,}")
with col2:
    st.metric("👥 Unique Customers", f"{filtered_df['customer_id'].nunique():,}")
with col3:
    total_distance = filtered_df['distance'].sum() / 1000
    st.metric("📍 Total Distance", f"{total_distance:.1f}K km")
with col4:
    avg_revenue = filtered_df['revenue'].mean()
    st.metric("💶 Avg Revenue / Trip", f"€{avg_revenue:.2f}")

st.divider()

# ── Performance over time ─────────────────────────────────────
st.markdown("### 📈 Performance Over Time")
col_left, col_right = st.columns(2)

with col_left:
    trips_over_time = (
        filtered_df
        .assign(date=filtered_df['pickup_time'].dt.date)
        .groupby("date")
        .size()
        .reset_index(name="Trips")
    )
    fig = px.line(
        trips_over_time, x="date", y="Trips",
        title="Trips Over Time",
        color_discrete_sequence=["#b8c0ff"]
    )
    fig.update_traces(fill='tozeroy', fillcolor='rgba(184,192,255,0.15)')
    st.plotly_chart(style_chart(fig), use_container_width=True)

with col_right:
    revenue_over_time = (
        filtered_df
        .assign(date=filtered_df['pickup_time'].dt.date)
        .groupby("date")["revenue"]
        .sum()
        .reset_index()
    )
    fig = px.line(
        revenue_over_time, x="date", y="revenue",
        title="Revenue Over Time (€)",
        color_discrete_sequence=["#ffc8dd"]
    )
    fig.update_traces(fill='tozeroy', fillcolor='rgba(255,200,221,0.15)')
    st.plotly_chart(style_chart(fig), use_container_width=True)

st.divider()

# ── Brand breakdown ───────────────────────────────────────────
st.markdown("### 🚘 Brand Breakdown")
col_a, col_b = st.columns(2)

with col_a:
    brand_counts = (
        filtered_df['brand']
        .value_counts()
        .reset_index()
    )
    brand_counts.columns = ['Brand', 'Trips']
    fig = px.bar(
        brand_counts, x="Brand", y="Trips",
        title="Trips by Car Brand",
        color="Brand",
        color_discrete_sequence=COLORS
    )
    st.plotly_chart(style_chart(fig), use_container_width=True)

with col_b:
    fig = px.pie(
        brand_counts, names="Brand", values="Trips",
        title="Market Share by Brand",
        color_discrete_sequence=COLORS,
        hole=0.5
    )
    fig.update_layout(
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font_color=FONT_COLOR,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Ratings & Revenue ─────────────────────────────────────────
st.markdown("### ⭐ Ratings & Revenue")
col_c, col_d = st.columns(2)

with col_c:
    avg_rating = (
        filtered_df.groupby("brand")["rating"]
        .mean()
        .reset_index()
        .sort_values("rating", ascending=False)
    )
    fig = px.bar(
        avg_rating, x="brand", y="rating",
        title="Average Rating by Brand",
        color="brand",
        color_discrete_sequence=COLORS
    )
    fig.update_yaxes(range=[0, 5])
    st.plotly_chart(style_chart(fig), use_container_width=True)

with col_d:
    avg_rev = (
        filtered_df.groupby("model")["revenue"]
        .mean()
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    fig = px.bar(
        avg_rev, x="revenue", y="model",
        title="Top 10 Models by Avg Revenue",
        orientation="h",
        color="model",
        color_discrete_sequence=COLORS
    )
    st.plotly_chart(style_chart(fig), use_container_width=True)

st.divider()

# ── Raw data ──────────────────────────────────────────────────
with st.expander("🔎 View Raw Data"):
    st.dataframe(
        filtered_df[['pickup_time', 'brand', 'model', 'distance', 'revenue', 'rating', 'name']],
        use_container_width=True
    )