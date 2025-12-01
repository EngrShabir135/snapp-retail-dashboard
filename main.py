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
# Brand Comparison Portal Function
# -------------------------
def run_brand_comparison():
    import numpy as np
    import io
    
    st.title("📊 Brand vs Competitor Analysis")
    
    # --- File uploader ---
    uploaded_file = st.file_uploader("Upload Dataset (Excel/CSV)", type=["xlsx", "csv"])
    
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully!")

        # --- Region filter ---
        region_list = df["REGION"].dropna().unique().tolist()
        selected_region = st.selectbox("Select Region", region_list)
        df_region = df[df["REGION"] == selected_region]

        # --- Category filter ---
        category_list = df_region["CATEGORY"].dropna().unique().tolist()
        selected_category = st.selectbox("Select Category", category_list)
        df_cat = df_region[df_region["CATEGORY"] == selected_category]

        # --- Brand filter ---
        brand_list = df_cat["Brand"].dropna().unique().tolist()
        selected_brands = st.multiselect("Select Brands for Comparison", brand_list)

        # --- Metric selection ---
        st.info("📊 Using 'Average of NTP' as the metric")
        metric_column = "Average of NTP"

        # --- SKU list logic ---
        energy_brands = ["Sting", "Roar", "RedBull", "Storm"]
        juice_brands = ["Slice", "Nesfruta", "Cappy"]
        water_brands = ["Aquafina", "Cola Next Water", "Dasani", "Gourmet Water", "Nestle", "Sparklett"]

        if any(b in selected_brands for b in energy_brands):
            sku_list = ["250ml Can", "300ml PET", "300ml/345ml/350ml PET", "500ml PET", "SSRB"]
        elif any(b in selected_brands for b in juice_brands):
            sku_list = ["1Ltr PET", "200ml TP", "350ml TP"]
        elif any(b in selected_brands for b in water_brands):
            sku_list = ["1.5Ltr PET", "500ml PET", "600ml PET"]
        else:
            sku_list = [
                "1.5Ltr PET", "1Ltr PET", "2.25Ltr PET", "250ml Can", "2Ltr PET",
                "300ml/345ml/350ml PET", "500ml PET", "SSRB"
            ]

        # --- Calculations ---
        if selected_brands:
            result = pd.DataFrame(index=sku_list)

            for brand in selected_brands:
                brand_df = df_cat[df_cat["Brand"] == brand]
                brand_values = []
                
                for sku in sku_list:
                    sku_data = brand_df[brand_df["SKUS"] == sku][metric_column]
                    
                    if len(sku_data) > 0:
                        value = sku_data.mean()
                    else:
                        value = np.nan
                    
                    brand_values.append(value)
                
                result[brand] = brand_values

            # --- Show table ---
            st.subheader(f"📌 Average NTP by SKU & Brand in {selected_region} ({selected_category})")
            
            # Display table with blank cells for missing values
            display_df = result.replace(np.nan, "")
            st.dataframe(display_df)

            # --- Download button for clean Excel ---
            st.markdown("---")
            
            # Prepare data for download (blank cells for missing values)
            download_df = result.replace(np.nan, "")
            
            # Create Excel file with clean formatting
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                download_df.to_excel(writer, sheet_name='Average_NTP', index=True)
                
                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Average_NTP']
                
                # Add formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Write header
                for col_num, value in enumerate(download_df.columns.values):
                    worksheet.write(0, col_num + 1, value, header_format)
                
                # Write index header
                worksheet.write(0, 0, "SKU", header_format)

            excel_data = excel_buffer.getvalue()
            
            # Download button
            st.download_button(
                label="⬇️ Download Average NTP Table as Excel",
                data=excel_data,
                file_name=f"Average_NTP_by_SKU_Brand_{selected_region}_{selected_category}.xlsx",
                mime="application/vnd.ms-excel"
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
        padding: 10px 20px;
        color: black !important;
        font-weight: bold;
        border-radius: 8px;
        margin: 6px 8px;
        cursor: pointer;
        transition: 0.3s;
        border: none;
        font-size: 14px;
        white-space: nowrap;
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
    
    /* Quotes styling */
    .quote-card {
        background: rgba(255, 255, 255, 0.15);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        font-style: italic;
        font-size: 18px;
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

# ✅ Updated Navbar - now has 8 buttons (added Brand Comparison)
st.markdown('<div class="navbar">', unsafe_allow_html=True)
cols = st.columns(8)

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
    if st.button("🔍 NTP Analysis", key="ntp_analysis_btn"):
        set_page("NTP Analysis")
    if selected_page == "NTP Analysis":
        st.markdown('<style>#ntp_analysis_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[4]:
    if st.button("🆚 Brand Compare", key="brand_compare_btn"):  # ✅ New Brand Comparison Button
        set_page("Brand Compare")
    if selected_page == "Brand Compare":
        st.markdown('<style>#brand_compare_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[5]:
    if st.button("🖼️ KoBo Images", key="kobo_btn"):
        set_page("KoBo Images")
    if selected_page == "KoBo Images":
        st.markdown('<style>#kobo_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[6]:
    if st.button("📚 Read Books", key="books_btn"):
        set_page("Read Books")
    if selected_page == "Read Books":
        st.markdown('<style>#books_btn{background:white !important;color:black !important;}</style>', unsafe_allow_html=True)

with cols[7]:
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

elif selected_page == "NTP Analysis":
    run_ntp_analysis()

elif selected_page == "Brand Compare":  # ✅ New Brand Comparison Page
    run_brand_comparison()

elif selected_page == "KoBo Images":
    appdkoboimages.run()

elif selected_page == "Read Books":
    appreadbooks.run()

elif selected_page == "About Me":
    about.main()
