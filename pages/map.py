import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trips Map", page_icon="🗺️", layout="wide")

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
    <style>
        .stApp { background-color: #f7f8fc; color: #2d2d2d; }
        [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e8e8f0; }
        h1, h2, h3 { color: #2d2d2d !important; font-weight: 600 !important; }
        hr { border-color: #e8e8f0; }
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e8e8f0;
            border-radius: 12px;
            padding: 16px;
        }
        [data-testid="stMetricLabel"] { color: #9a9ab0 !important; font-size: 13px !important; }
        [data-testid="stMetricValue"] { color: #2d2d2d !important; font-size: 26px !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

COLORS = ["#b8c0ff", "#ffc8dd", "#caffbf", "#ffd6a5", "#a0c4ff", "#bdb2ff"]

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    df = trips.merge(cars, left_on="car_id", right_on="id", suffixes=("", "_car"))
    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────
st.markdown("## 🗺️ Trip Locations")
st.markdown("<p style='color:#9a9ab0; margin-top:-15px;'>Where are our trips starting and ending?</p>", unsafe_allow_html=True)
st.divider()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.markdown("## 🗺️ Filters")
st.sidebar.markdown("---")

brands = st.sidebar.multiselect(
    "Car Brand",
    options=sorted(df["brand"].unique()),
    default=sorted(df["brand"].unique())
)

map_type = st.sidebar.radio(
    "Show locations",
    options=["Pickup", "Dropoff", "Both"]
)

filtered_df = df[df["brand"].isin(brands)]

# ── Metrics ───────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🛣️ Trips Shown", f"{len(filtered_df):,}")
with col2:
    st.metric("🚗 Brands Selected", len(brands))
with col3:
    avg_dist = filtered_df["distance"].mean()
    st.metric("📍 Avg Distance", f"{avg_dist:.2f} km")

st.divider()

# ── Map ───────────────────────────────────────────────────────
if map_type == "Pickup" or map_type == "Both":
    st.markdown("### 📍 Pickup Locations")
    pickup_map = filtered_df[['pickup_lat', 'pickup_lon']].rename(
        columns={'pickup_lat': 'lat', 'pickup_lon': 'lon'}
    ).dropna()
    st.map(pickup_map, color="#b8c0ff", size=15)

if map_type == "Dropoff" or map_type == "Both":
    st.markdown("### 🏁 Dropoff Locations")
    dropoff_map = filtered_df[['dropoff_lat', 'dropoff_lon']].rename(
        columns={'dropoff_lat': 'lat', 'dropoff_lon': 'lon'}
    ).dropna()
    st.map(dropoff_map, color="#ffc8dd", size=15)

st.divider()

# ── Trips per brand bar chart ─────────────────────────────────
st.markdown("### 🚘 Trips by Brand in Selected Area")
brand_counts = (
    filtered_df["brand"]
    .value_counts()
    .reset_index()
)
brand_counts.columns = ["Brand", "Trips"]

fig = px.bar(
    brand_counts, x="Brand", y="Trips",
    color="Brand",
    color_discrete_sequence=COLORS,
    title="Trips by Car Brand"
)
fig.update_layout(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font_color="#2d2d2d",
    showlegend=False,
    margin=dict(l=20, r=20, t=40, b=20)
)
fig.update_xaxes(gridcolor="#f0f0f5", zeroline=False)
fig.update_yaxes(gridcolor="#f0f0f5", zeroline=False)
st.plotly_chart(fig, use_container_width=True)