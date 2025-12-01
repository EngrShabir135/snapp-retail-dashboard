import streamlit as st
import pandas as pd
import numpy as np
import io
import appalldata, appdkoboimages, appntppk, about, appreadbooks

# -------------------------
# NTP Analysis Function (Fixed)
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
        try:
            # Load dataset
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        
            st.success("✅ File uploaded successfully!")
            
            # Check required columns
            required_cols = ["CHANNEL", "CAT", "REGION", "SKUS", "BRAND"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                st.info("Please make sure your file has these columns: CHANNEL, CAT, REGION, SKUS, BRAND")
                return
            
            # Check if NTP/Case column exists
            ntp_col = "NTP/Case"
            if ntp_col not in df.columns:
                st.warning(f"⚠️ Column '{ntp_col}' not found. Using first available numeric column.")
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    ntp_col = numeric_cols[0]
                    st.info(f"Using column '{ntp_col}' for analysis")
                else:
                    st.error("❌ No numeric columns found in the dataset")
                    return

            # --- Sidebar filters ---
            st.sidebar.header("🔎 Filters")
            
            # Safely get unique values
            channel_options = df["CHANNEL"].dropna().unique() if "CHANNEL" in df.columns else []
            cat_options = df["CAT"].dropna().unique() if "CAT" in df.columns else []
            region_options = df["REGION"].dropna().unique() if "REGION" in df.columns else []
            
            if len(channel_options) == 0 or len(cat_options) == 0 or len(region_options) == 0:
                st.warning("⚠️ Some filter options are empty. Check your data columns.")
                return

            channel = st.sidebar.selectbox("Select Channel", options=channel_options)
            cat = st.sidebar.selectbox("Select Category", options=cat_options)
            region = st.sidebar.selectbox("Select Region", options=region_options)

            # --- Filter dataset ---
            filtered = df[
                (df["CHANNEL"] == channel) &
                (df["CAT"] == cat) &
                (df["REGION"] == region)
            ]

            if filtered.empty:
                st.warning("⚠️ No data available for this selection.")
                return

            # --- Pivot table ---
            pivot = pd.pivot_table(
                filtered,
                index="SKUS",
                columns="BRAND",
                values=ntp_col,
                aggfunc="mean"
            )

            # --- Reindex SKUs based on template ---
            sku_list = SKU_TEMPLATE.get(cat, sorted(filtered["SKUS"].dropna().unique()))
            pivot = pivot.reindex(sku_list)

            pivot = pivot.reset_index().rename(columns={"index": "SKU"})

            st.subheader(f"📌 NTP Table for {cat} in {region} - Channel: {channel}")
            st.dataframe(pivot, use_container_width=True)

            # --- Download option ---
            @st.cache_data
            def convert_excel(df):
                output = io.BytesIO()
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
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please check your file format and try again.")

# -------------------------
# Brand Comparison Portal Function (Fixed)
# -------------------------
def run_brand_comparison():
    st.title("📊 Brand vs Competitor Analysis")
    
    # --- File uploader ---
    uploaded_file = st.file_uploader("Upload Dataset (Excel/CSV)", type=["xlsx", "csv"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("✅ File uploaded successfully!")
            
            # Check required columns
            required_cols = ["REGION", "CATEGORY", "Brand", "SKUS"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                st.info("Please make sure your file has these columns: REGION, CATEGORY, Brand, SKUS")
                return

            # Check for metric column
            metric_column = "Average of NTP"
            if metric_column not in df.columns:
                st.warning(f"⚠️ Column '{metric_column}' not found. Available columns:")
                st.write(df.columns.tolist())
                
                # Let user select metric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    selected_metric = st.selectbox("Select metric column to use:", numeric_cols)
                    metric_column = selected_metric
                else:
                    st.error("❌ No numeric columns found in the dataset")
                    return

            # --- Region filter ---
            region_list = df["REGION"].dropna().unique().tolist()
            if not region_list:
                st.error("❌ No regions found in the dataset")
                return
                
            selected_region = st.selectbox("Select Region", region_list)
            df_region = df[df["REGION"] == selected_region]

            # --- Category filter ---
            category_list = df_region["CATEGORY"].dropna().unique().tolist()
            if not category_list:
                st.error("❌ No categories found for the selected region")
                return
                
            selected_category = st.selectbox("Select Category", category_list)
            df_cat = df_region[df_region["CATEGORY"] == selected_category]

            # --- Brand filter ---
            brand_list = df_cat["Brand"].dropna().unique().tolist()
            if not brand_list:
                st.error("❌ No brands found for the selected category and region")
                return
                
            selected_brands = st.multiselect("Select Brands for Comparison", brand_list)

            if not selected_brands:
                st.info("👈 Please select at least one brand to continue")
                return

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
            st.subheader(f"📌 {metric_column} by SKU & Brand in {selected_region} ({selected_category})")
            
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
                download_df.to_excel(writer, sheet_name='Analysis_Table', index=True)
                
                workbook = writer.book
                worksheet = writer.sheets['Analysis_Table']
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                for col_num, value in enumerate(download_df.columns.values):
                    worksheet.write(0, col_num + 1, value, header_format)
                
                worksheet.write(0, 0, "SKU", header_format)

            excel_data = excel_buffer.getvalue()
            
            # Download button
            st.download_button(
                label="⬇️ Download Analysis Table as Excel",
                data=excel_data,
                file_name=f"Analysis_Table_{selected_region}_{selected_category}.xlsx",
                mime="application/vnd.ms-excel"
            )
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

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
        padding: 10px 15px;
        color: black !important;
        font-weight: bold;
        border-radius: 8px;
        margin: 4px 6px;
        cursor: pointer;
        transition: 0.3s;
        border: none;
        font-size: 13px;
        white-space: nowrap;
        min-width: 100px;
        text-align: center;
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
    
    /* Error message styling */
    .stAlert {
        background-color: rgba(220, 53, 69, 0.1);
        border: 1px solid #dc3545;
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

# Create navbar with columns
st.markdown('<div class="navbar">', unsafe_allow_html=True)
navbar_cols = st.columns(8)

pages = [
    ("🏠 Home", "Home", navbar_cols[0]),
    ("📊 NTP PK", "NTP PK", navbar_cols[1]),
    ("📈 All Data", "All Data", navbar_cols[2]),
    ("🔍 NTP Analysis", "NTP Analysis", navbar_cols[3]),
    ("🆚 Brand Compare", "Brand Compare", navbar_cols[4]),
    ("🖼️ KoBo Images", "KoBo Images", navbar_cols[5]),
    ("📚 Read Books", "Read Books", navbar_cols[6]),
    ("🤖 About Me", "About Me", navbar_cols[7]),
]

for page_name, page_key, col in pages:
    with col:
        if st.button(page_name, key=f"btn_{page_key}"):
            set_page(page_key)
        if selected_page == page_key:
            st.markdown(f'<style>#btn_{page_key}{{background:white !important;color:black !important;}}</style>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Render Pages
# -------------------------
try:
    if selected_page == "Home":
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
            # Use a placeholder or remove if logo.png doesn't exist
            try:
                st.image("logo.png", use_container_width=True)
            except:
                st.info("📷 Logo image not found. You can add logo.png to your project folder.")

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
        try:
            appntppk.run()
        except Exception as e:
            st.error(f"Error loading NTP PK: {str(e)}")
            st.info("Make sure appntppk.py exists in your project folder")

    elif selected_page == "All Data":
        try:
            appalldata.run()
        except Exception as e:
            st.error(f"Error loading All Data: {str(e)}")
            st.info("Make sure appalldata.py exists in your project folder")

    elif selected_page == "NTP Analysis":
        run_ntp_analysis()

    elif selected_page == "Brand Compare":
        run_brand_comparison()

    elif selected_page == "KoBo Images":
        try:
            appdkoboimages.run()
        except Exception as e:
            st.error(f"Error loading KoBo Images: {str(e)}")
            st.info("Make sure appdkoboimages.py exists in your project folder")

    elif selected_page == "Read Books":
        try:
            appreadbooks.run()
        except Exception as e:
            st.error(f"Error loading Read Books: {str(e)}")
            st.info("Make sure appreadbooks.py exists in your project folder")

    elif selected_page == "About Me":
        try:
            about.main()
        except Exception as e:
            st.error(f"Error loading About Me: {str(e)}")
            st.info("Make sure about.py exists in your project folder")

except Exception as e:
    st.error(f"❌ Application Error: {str(e)}")
    st.info("""
    **Troubleshooting Steps:**
    1. Make sure all required .py files exist in your project folder
    2. Check if your dataset has the correct column names
    3. Try uploading a different file format (CSV instead of Excel or vice versa)
    4. Check the error message above for more details
    """)
