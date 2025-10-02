import streamlit as st
import pandas as pd
import appalldata, appdkoboimages, appntppk, about, appreadbooks

# -------------------------
# NTP Analysis Function
# -------------------------
def run_ntp_analysis():
    st.title("📊 NTP Analysis Dashboard")
    
    # --- Define fixed SKU lists per CAT ---
    SKU_TEMPLATE = {
        "COLA": [
            "1.5Ltr PET", "1Ltr PET", "2.25Ltr PET", "250ml Can", "2Ltr PET",
            "300-350 ML PET", "500ml PET", "SSRB"
        ],
        "LLM": [
            "1.5Ltr PET", "1Ltr PET", "2.25Ltr PET", "250ml Can", "2Ltr PET",
            "300-350 ML PET", "500ml PET", "SSRB"
        ],
        "ORANGE": [
            "1.5Ltr PET", "1Ltr PET", "2.25Ltr PET", "250ml Can", "2Ltr PET",
            "300-350 ML PET", "500ml PET", "SSRB"
        ],
        "CITRUS": [
            "1.5Ltr PET", "1Ltr PET", "2.25Ltr PET", "250ml Can", "2Ltr PET",
            "300-350 ML PET", "500ml PET", "SSRB"
        ],
        "ENERGY": [
            "250ml Can", "300ml PET", "300-350 ML PET", "500ml PET", "SSRB"
        ],
        "WATER": [
            "1.5Ltr PET", "500ml PET", "600ml PET"
        ],
        "JNSD": [
            "1Ltr PET", "200ml TP", "350ml TP"
        ]
    }
    
    # --- File uploader ---
    uploaded_file = st.file_uploader("Upload your dataset (Excel or CSV)", type=["xlsx", "xls", "csv"])
    
    if uploaded_file:
        # Load dataset
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    
        st.success("✅ File uploaded successfully!")
    
        # --- Sidebar filters ---
        st.sidebar.header("🔎 Filters")
    
        channel = st.sidebar.selectbox("Select Channel", options=df["CHANNEL"].unique())
        cat = st.sidebar.selectbox("Select Category", options=df["CAT"].unique())
        region = st.sidebar.selectbox("Select Region", options=df["REGION"].unique())
    
        # --- Filter dataset ---
        filtered = df[
            (df["CHANNEL"] == channel) &
            (df["CAT"] == cat) &
            (df["REGION"] == region)
        ]
    
        if filtered.empty:
            st.warning("⚠️ No data available for this selection.")
        else:
            # --- Pivot table like screenshot ---
            pivot = pd.pivot_table(
                filtered,
                index="SKUS",
                columns="BRAND",
                values="NTP/Case",
                aggfunc="mean"
            )
    
            # --- Reindex SKUs based on template ---
            sku_list = SKU_TEMPLATE.get(cat, sorted(filtered["SKUS"].unique()))
            pivot = pivot.reindex(sku_list)
    
            pivot = pivot.reset_index().rename(columns={"index": "SKU"})
    
            st.subheader(f"📌 NTP Table for {cat} in {region} - Channel: {channel}")
            st.dataframe(pivot, use_container_width=True)
    
            # --- Download option ---
            @st.cache_data
            def convert_excel(df):
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="NTP_Table")
                return output.getvalue()
    
            excel_data = convert_excel(pivot)
    
            st.download_button(
                label="📥 Download Table as Excel",
                data=excel_data,
                file_name=f"NTP_Table_{cat}_{region}_{channel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="Snapp Retail Dashboard", layout="wide")

# -------------------------
# Custom CSS for Website Look with Animated Background
# -------------------------
st.markdown("""
    <style>
    /* Animated gradient background */
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #f1c40f, #e74c3c, #f39c12, #e67e22);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: white;
    }

    /* Navbar container */
    .navbar {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        background: linear-gradient(90deg, #f1c40f, #e74c3c);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }
    .nav-button {
        padding: 10px 25px;
        color: black !important;
        font-weight: bold;
        border-radius: 8px;
        margin: 6px 10px;
        cursor: pointer;
        transition: 0.3s;
        border: none;
    }
    .nav-button:hover {
        background-color: white;
        color: black !important;
        transform: scale(1.05);
    }
    .active {
        background-color: white !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Navbar with session_state
# -------------------------
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "Home"

def set_page(page):
    st.session_state["selected_page"] = page

selected_page = st.session_state["selected_page"]

# ✅ Updated Navbar - now has 7 buttons (added NTP Analysis)
st.markdown('<div class="navbar">', unsafe_allow_html=True)
cols = st.columns(7)

with cols[0]:
    if st.button("🏠 Home", key="home_btn"):
        set_page("Home")
    if selected_page == "Home":
        st.markdown('<style>#home_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[1]:
    if st.button("📊 NTP PK", key="ntp_btn"):
        set_page("NTP PK")
    if selected_page == "NTP PK":
        st.markdown('<style>#ntp_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[2]:
    if st.button("📈 All Data", key="all_btn"):
        set_page("All Data")
    if selected_page == "All Data":
        st.markdown('<style>#all_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[3]:
    if st.button("🔍 NTP Analysis", key="ntp_analysis_btn"):  # ✅ New Button
        set_page("NTP Analysis")
    if selected_page == "NTP Analysis":
        st.markdown('<style>#ntp_analysis_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[4]:
    if st.button("🖼️ KoBo Images", key="kobo_btn"):
        set_page("KoBo Images")
    if selected_page == "KoBo Images":
        st.markdown('<style>#kobo_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[5]:
    if st.button("📚 Read Books", key="books_btn"):
        set_page("Read Books")
    if selected_page == "Read Books":
        st.markdown('<style>#books_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[6]:
    if st.button("🤖 About Me", key="about_btn"):
        set_page("About Me")
    if selected_page == "About Me":
        st.markdown('<style>#about_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Render Pages
# -------------------------
if selected_page == "Home":
    st.image("logo.png", width=180)
    st.title("✨ Welcome to Snapp Retail Dashboard")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("About Snapp Retail")
        st.write("""
        Snapp Retail is a leading company revolutionizing retail execution 
        and visibility across markets. With cutting-edge digital tools, 
        Snapp Retail empowers brands and distributors to make data-driven 
        decisions, optimize sales, and achieve operational excellence.
        """)

        st.subheader("About Me")
        st.write("""
        Hi 👋, I am **Muhammad Shabir**, a Computer Systems Engineer 
        specializing in **Machine Learning, Deep Learning, NLP, and Data Science**.  
        I create smart dashboards, AI-driven analytics, and data products 
        that help businesses grow.
        """)

    with col2:
        st.image("logo.png", use_container_width=True)

    st.markdown("---")
    st.markdown("### 💡 Motivational Quotes")

    quotes = [
        "“Success is not final, failure is not fatal: It is the courage to continue that counts.” – Winston Churchill",
        "“The best way to get started is to quit talking and begin doing.” – Walt Disney",
        "“Don't let yesterday take up too much of today.” – Will Rogers",
        "“It always seems impossible until it's done.” – Nelson Mandela",
    ]
    for q in quotes:
        st.markdown(f'<div class="quote-card">{q}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 Use the navigation bar above to explore different apps.")

elif selected_page == "NTP PK":
    appntppk.run()

elif selected_page == "All Data":
    appalldata.run()

elif selected_page == "NTP Analysis":  # ✅ New Section
    run_ntp_analysis()

elif selected_page == "KoBo Images":
    appdkoboimages.run()

elif selected_page == "Read Books":
    appreadbooks.run()

elif selected_page == "About Me":
    about.main()

