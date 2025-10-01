import streamlit as st
import pandas as pd

def run():
    st.title("📊 NTP PEP vs KO App")
    st.write("This app performs to find NTP using file Raw data from date to date.")

    # --- Page config ---
    st.set_page_config(page_title="Brand vs Competitor Analysis", layout="wide")

    # --- Custom CSS for black/green theme ---
    st.markdown("""
        <style>
            body {
                background-color: black;
                color: green;
            }
            .stApp {
                background-color: black;
                color: green;
            }
            table {
                color: green;
                background-color: black;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🥤 Brand vs Competitor Analyzer")

    # --- Upload dataset ---
    uploaded_file = st.file_uploader("Upload your dataset (Excel/CSV)", type=["xlsx", "csv"])

    if uploaded_file:
        # Load file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ Dataset uploaded successfully!")

        # --- Fixed SKUS list ---
        skus_required = [
            "SSRB",
            "300ml/345ml/350ml PET",
            "500ml PET",
            "1Ltr PET",
            "1.5Ltr PET",
            "2Ltr PET",
            "2.25Ltr PET"
        ]

        # --- Region order ---
        region_order = [
            "National",
            "Faisalabad",
            "Gujranwala",
            "Sialkot",
            "Islamabad",
            "Karachi",
            "Hyderabad",
            "Lahore",
            "Multan",
            "Bahawalpur",
            "Peshawar",
            "Sukkur",
            "Rahim Yar Khan"
        ]

        # --- User options ---
        col1, col2 = st.columns(2)

        with col1:
            brand = st.selectbox("Select Brand", df["Brand"].unique())
        with col2:
            competitor = st.selectbox("Select Competitor", df["Brand"].unique())

        metric = st.selectbox("Select Metric", ["NTP", "TP", "CONSUMER PRICE", "Disc per case"])
        agg_type = st.radio("Choose Aggregation", ["Average", "Minimum", "Maximum"])

        # --- Filter dataset ---
        df_filtered = df[df["Brand"].isin([brand, competitor]) & df["SKUS"].isin(skus_required)]

        # --- Group and aggregate ---
        if agg_type == "Average":
            result = df_filtered.groupby(["REGION", "Brand", "SKUS"])[metric].mean().reset_index()
        elif agg_type == "Minimum":
            result = df_filtered.groupby(["REGION", "Brand", "SKUS"])[metric].min().reset_index()
        else:  # Maximum
            result = df_filtered.groupby(["REGION", "Brand", "SKUS"])[metric].max().reset_index()

        # --- Create short brand codes ---
        def shorten(name):
            return "".join([w[:3] for w in name.split()][:2])  # first 2–3 words, 3 letters each
        brand_map = {brand: shorten(brand), competitor: shorten(competitor)}

        # --- Pivot: REGION as rows, SKUS+Brand as columns ---
        comparison = result.pivot_table(
            index="REGION",
            columns=["SKUS", "Brand"],
            values=metric,
            aggfunc="first"
        )

        # --- Flatten column MultiIndex into "SKU_BrandCode" ---
        comparison.columns = [f"{sku}_{brand_map[b]}" for sku, b in comparison.columns]

        # --- Reset index and enforce region order ---
        comparison = comparison.reset_index()
        comparison["REGION"] = pd.Categorical(comparison["REGION"], categories=region_order, ordered=True)
        comparison = comparison.sort_values("REGION").reset_index(drop=True)

        # --- Reorder columns (ensure no duplicates) ---
        ordered_cols = ["REGION"]
        for sku in skus_required:
            for b in [brand, competitor]:
                col_name = f"{sku}_{brand_map[b]}"
                if col_name in comparison.columns and col_name not in ordered_cols:  
                    ordered_cols.append(col_name)

        comparison = comparison[ordered_cols]

        # --- Deduplicate columns just in case ---
        comparison = comparison.loc[:, ~comparison.columns.duplicated()]

        # --- Show table ---
        st.subheader(f"{metric} - {agg_type} by Region & SKUs")
        st.dataframe(comparison)

        # --- Download as Excel ---
        def to_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Results")
            return output.getvalue()

        excel_data = to_excel(comparison)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="brand_vs_competitor_skus.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Please upload a dataset to begin.")