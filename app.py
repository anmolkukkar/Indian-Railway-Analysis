import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title=" Railway Dashboard", layout="wide")
st.title(" Indian Railway Analysis Dashboard")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/trains_cleartrip.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace('.', '', regex=False)
    return df

df = load_data()

# ---------------------------
# SHOW COLUMNS
# ---------------------------
st.subheader(" Columns in dataset:")
st.write(df.columns.tolist())

# ---------------------------
# AUTO DETECT COLUMNS
# ---------------------------
train_col, source_col, dest_col = None, None, None

for col in df.columns:
    if 'train' in col and 'no' in col:
        train_col = col
    if 'start' in col:
        source_col = col
    if 'end' in col:
        dest_col = col

if not train_col or not source_col or not dest_col:
    st.error(" Column detection failed")
    st.stop()

# ---------------------------
# CREATE ROUTE COLUMN (IMPORTANT)
# ---------------------------
df['route'] = df[source_col] + " → " + df[dest_col]

# ---------------------------
# KPI CARDS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(" Total Trains", df[train_col].nunique())
col2.metric(" Sources", df[source_col].nunique())
col3.metric(" Destinations", df[dest_col].nunique())
col4.metric(" Routes", df['route'].nunique())

# ---------------------------
# SIDEBAR FILTER
# ---------------------------
st.sidebar.header(" Filter")

selected_station = st.sidebar.selectbox(
    "Select Source Station",
    ["All"] + list(df[source_col].dropna().unique())
)

if selected_station != "All":
    df = df[df[source_col] == selected_station]

# ---------------------------
# LAYOUT (2 COLUMNS LIKE POWER BI)
# ---------------------------
col_left, col_right = st.columns(2)

# ---------------------------
# 1. BUSIEST STATIONS
# ---------------------------
with col_left:
    st.subheader(" Most Busiest Stations")
    busy = df[source_col].value_counts().head(10).reset_index()
    busy.columns = ['Station', 'Train Count']
    fig1 = px.bar(busy, x='Station', y='Train Count', color='Train Count')
    st.plotly_chart(fig1, use_container_width=True)

# ---------------------------
# 2. TOP ROUTES
# ---------------------------
with col_right:
    st.subheader(" Top Routes")
    routes = df['route'].value_counts().head(10).reset_index()
    routes.columns = ['Route', 'Count']
    fig2 = px.bar(routes, x='Route', y='Count', color='Count')
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# 3. TRAINS PER DESTINATION
# ---------------------------
st.subheader("🚆 Trains per Destination")

dest = df[dest_col].value_counts().head(10).reset_index()
dest.columns = ['Station', 'Count']

fig3 = px.bar(dest, x='Station', y='Count', color='Count')
st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# 4. ROUTE TRAFFIC DENSITY
# ---------------------------
st.subheader("🚦 Route Traffic Density")

route_density = df['route'].value_counts().reset_index()
route_density.columns = ['Route', 'Traffic']

fig4 = px.bar(
    route_density.head(10),
    x='Route',
    y='Traffic',
    color='Traffic'
)

st.plotly_chart(fig4, use_container_width=True)
# ---------------------------
# Unique routes

st.subheader(" Unique Routes per Station")

unique_routes = df.groupby(source_col)['route'].nunique().reset_index()
unique_routes.columns = ['Station', 'Unique Routes']

fig = px.bar(
    unique_routes.sort_values('Unique Routes', ascending=False).head(10),
    x='Station',
    y='Unique Routes'
)

st.plotly_chart(fig)

# ---------------------------
# 5. ROUTE DISTRIBUTION
# ---------------------------
st.subheader(" Route Distribution")
route_counts = df['route'].value_counts().head(5)
fig5 = px.pie(values=route_counts.values, names=route_counts.index)
st.plotly_chart(fig5)

# ---------------------------
# 6. SOURCE vs DESTINATION
# ---------------------------
st.subheader(" Source vs Destination Traffic")

source_counts = df[source_col].value_counts().head(10)
dest_counts = df[dest_col].value_counts().head(10)

compare_df = pd.DataFrame({
    'Source': source_counts,
    'Destination': dest_counts
}).fillna(0)

st.bar_chart(compare_df)

# ---------------------------
# 7. TRAIN NAME PATTERN
# ---------------------------
if 'train_name' in df.columns:
    st.subheader("🔤 Train Name Pattern")
    df['first_letter'] = df['train_name'].str[0]
    letter_count = df['first_letter'].value_counts().reset_index()
    letter_count.columns = ['Letter', 'Count']
    fig6 = px.bar(letter_count, x='Letter', y='Count')
    st.plotly_chart(fig6)


# ---------------------------
# 8. SIMULATED TRAINS PER DAY (SORTED)
# ---------------------------
st.subheader(" Estimated Trains Per Day")

df['day'] = np.random.choice(
    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    size=len(df)
)

# COUNT
day_counts = df['day'].value_counts().reset_index()
day_counts.columns = ['Day', 'Trains']

# ✅ DEFINE CORRECT ORDER
day_order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

# ✅ APPLY ORDER
day_counts['Day'] = pd.Categorical(day_counts['Day'], categories=day_order, ordered=True)
day_counts = day_counts.sort_values('Day')

# PLOT
fig8 = px.bar(day_counts, x='Day', y='Trains')
st.plotly_chart(fig8)
# ---------------------------
# FOOTER
# ---------------------------
st.write("   Railway Analysis Dashboard by Anmol")

