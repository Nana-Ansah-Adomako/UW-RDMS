import streamlit as st
import pandas as pd
import altair as alt

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Patients Outcome Dashboard",
    page_icon="🏥",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0f1e2b;
    color: #e8f0f7;
}
section[data-testid="stSidebar"] {
    background: #0a1520 !important;
    border-right: 1px solid #1e3448;
}
section[data-testid="stSidebar"] * {
    color: #c9daea !important;
}
.metric-card {
    background: #162535;
    border: 1px solid #1e3a50;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.metric-card .value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #4fc3f7;
    line-height: 1;
}
.metric-card .label {
    font-size: 0.78rem;
    color: #7fa8c4;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}
h1 {
    font-family: 'DM Serif Display', serif !important;
    color: #e8f0f7 !important;
}
h2, h3 {
    font-family: 'DM Serif Display', serif !important;
    color: #b8d8f0 !important;
}
hr { border-color: #1e3448; }
.stFileUploader label { color: #a0c4e0 !important; }
.vega-embed { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 🏥 Patient Outcomes Dashboard")
st.markdown("Upload your patient dataset to explore treatment and diagnosis insights.")
st.markdown("---")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Data Source")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    st.markdown("---")
    st.markdown("**Required columns**")
    st.markdown("""
- `treatment_group`
- `died_within_1_year`
- `race`
- `age_at_diagnosis`
""")

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file) -> pd.DataFrame:
    return pd.read_csv(file)

if uploaded_file is None:
    st.info("👈 Upload a CSV file in the sidebar to get started.")
    st.stop()

df = load_data(uploaded_file)

required_cols = {"treatment_group", "died_within_1_year", "race", "age_at_diagnosis"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"CSV is missing required columns: {', '.join(missing)}")
    st.stop()

# ── Summary metrics ────────────────────────────────────────────────────────────
total_patients   = len(df)
died_within_1yr  = (df["died_within_1_year"] == "Yes").sum()
pct_died         = f"{died_within_1yr / total_patients * 100:.1f}%" if total_patients else "–"
n_treatment_grps = df["treatment_group"].nunique()
n_races          = df["race"].nunique()

col1, col2, col3, col4 = st.columns(4)
for col, val, lbl in zip(
    [col1, col2, col3, col4],
    [f"{total_patients:,}", f"{died_within_1yr:,}", pct_died, str(n_treatment_grps)],
    ["Total Patients", "Died Within 1 Year", "Mortality Rate", "Treatment Groups"],
):
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="value">{val}</div>'
            f'<div class="label">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Altair dark theme helper ───────────────────────────────────────────────────
CHART_BG   = "#162535"
GRID_COLOR = "#1e3a50"
TEXT_COLOR = "#b8d8f0"
BAR_COLOR  = "#4fc3f7"
BAR_COLOR2 = "#26c6da"

def chart_config(chart):
    return chart.configure_view(
        strokeOpacity=0,
        fill=CHART_BG,
    ).configure_axis(
        gridColor=GRID_COLOR,
        domainColor=GRID_COLOR,
        tickColor=GRID_COLOR,
        labelColor=TEXT_COLOR,
        titleColor=TEXT_COLOR,
        labelFont="DM Sans",
        titleFont="DM Sans",
    ).configure_title(
        color=TEXT_COLOR,
        font="DM Serif Display",
        fontSize=16,
    ).configure_legend(
        labelColor=TEXT_COLOR,
        titleColor=TEXT_COLOR,
        labelFont="DM Sans",
        titleFont="DM Sans",
    )

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 Filters")
    all_groups = sorted(df["treatment_group"].dropna().unique().tolist())
    selected_groups = st.multiselect(
        "Treatment Groups",
        options=all_groups,
        default=all_groups,
    )
    all_races = sorted(df["race"].dropna().unique().tolist())
    selected_races = st.multiselect(
        "Race",
        options=all_races,
        default=all_races,
    )

df_filtered = df[
    df["treatment_group"].isin(selected_groups) &
    df["race"].isin(selected_races)
].copy()

if df_filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — Donut (left)  |  Mortality Bar (right)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 📊 Treatment Group Overview")
col_left, col_right = st.columns([1, 1.4])

# ── Chart 1: Donut — patient share by treatment group ─────────────────────────
with col_left:
    st.markdown("#### Patient Distribution by Treatment Group")

    treatment_counts = (
        df_filtered["treatment_group"]
        .value_counts()
        .reset_index()
    )
    treatment_counts.columns = ["treatment_group", "count"]
    treatment_counts["pct"] = (
        treatment_counts["count"] / treatment_counts["count"].sum() * 100
    ).round(1)
    treatment_counts["label"] = treatment_counts["pct"].astype(str) + "%"

    base = alt.Chart(treatment_counts).encode(
        theta=alt.Theta("count:Q", stack=True),
        order=alt.Order("count:Q", sort="descending"),
    )

    donut = base.mark_arc(innerRadius=60, outerRadius=120).encode(
        color=alt.Color(
            "treatment_group:N",
            title="Treatment Group",
            scale=alt.Scale(scheme="blues"),
        ),
        tooltip=[
            alt.Tooltip("treatment_group:N", title="Group"),
            alt.Tooltip("count:Q",           title="Patients"),
            alt.Tooltip("label:N",           title="Share"),
        ],
    )

    # text_labels = base.mark_text(radius=185, fontSize=11).encode(
    #     text=alt.Text("label:N"),
    #     color=alt.value(TEXT_COLOR),
    # )

    donut_chart = chart_config(
        (donut).properties(
            title="Treatment Group Share",
            width=300,
            height=360,
        )
    )
    st.altair_chart(donut_chart, use_container_width=True)

# ── Chart 2: Bar — deaths within 1 year by treatment group ────────────────────
with col_right:
    st.markdown("#### Patients Who Died Within 1 Year")

    df_died = df_filtered[df_filtered["died_within_1_year"] == "Yes"].copy()

    chart_mortality = chart_config(
        alt.Chart(df_died).mark_bar(
            color=BAR_COLOR,
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
        ).encode(
            x=alt.X("treatment_group:N", title="Treatment Group",
                     sort="-y", axis=alt.Axis(labelAngle=-30)),
            y=alt.Y("count():Q", title="Number of Patients"),
            tooltip=[
                alt.Tooltip("treatment_group:N", title="Group"),
                alt.Tooltip("count():Q",          title="Deaths"),
            ],
        ).properties(
            title="Deaths Within 1 Year — by Treatment Group",
            width="container",
            height=360,
        )
    )
    st.altair_chart(chart_mortality, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — Age at Diagnosis histogram  (full width)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("## 🧬 Age at Diagnosis Distribution")
st.caption("Filter by race using the dropdown below.")

race_options = sorted(df_filtered["race"].dropna().unique().tolist())
selected_race = st.selectbox("Select Race", options=["All"] + race_options)

df_hist = df_filtered.copy()
if selected_race != "All":
    df_hist = df_hist[df_hist["race"] == selected_race]

chart_age = chart_config(
    alt.Chart(df_hist).mark_bar(
        color=BAR_COLOR2,
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3,
    ).encode(
        x=alt.X("age_at_diagnosis:Q",
                 bin=alt.Bin(maxbins=25),
                 title="Age at Diagnosis"),
        y=alt.Y("count():Q", title="Number of Patients"),
        tooltip=[
            alt.Tooltip("age_at_diagnosis:Q", title="Age", bin=True),
            alt.Tooltip("count():Q",           title="Count"),
        ],
    ).properties(
        title=f"Age at Diagnosis — {selected_race if selected_race != 'All' else 'All Races'}",
        width="container",
        height=380,
    )
)
st.altair_chart(chart_age, use_container_width=True)

# ── Raw data preview ───────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🗂 Preview Raw Data"):
    st.dataframe(
        df_filtered.head(200),
        use_container_width=True,
        height=300,
    )
    st.caption(f"Showing up to 200 of {len(df_filtered):,} filtered rows.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#3d637e; font-size:0.8rem;'>"
    "Patient Outcomes Dashboard · Built with Streamlit & Altair"
    "</p>",
    unsafe_allow_html=True,
)