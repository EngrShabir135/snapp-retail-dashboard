import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import re


def run():
    
    st.title("📊 Take all data WS and GT")

    # -----------------------
    # Page / theme
    # -----------------------
    st.set_page_config(page_title="Analysis on all", layout="wide")
    st.markdown("""
        <style>
            body { background-color: black; color: green; }
            .stApp { background-color: black; color: green; }
            table { color: green; background-color: black; }
        </style>
    """, unsafe_allow_html=True)
    st.title("🥤 Brand vs Competitor Analyzer")

    # -----------------------
    # Reference Invoice Dictionary (from your table)
    # (kept exactly as you provided)
    # -----------------------
    invoice_reference_raw = {
        "LHE": {
            "300-350ML PET": {"PEPSI": 700, "COKE": 691},
            "500ML PET": {"PEPSI": 1022, "COKE": 869},
            "1Ltr PET": {"PEPSI": 741, "COKE": 823},
            "1.5Ltr PET": {"PEPSI": 856, "COKE": 822},
            "2Ltr PET": {"PEPSI": 938, "COKE": 999},
            "2.25Ltr PET": {"PEPSI": 1191, "COKE": 950},
        },
        "ISB": {
            "300-350ML PET": {"PEPSI": 680, "COKE": 680},
            "500ML PET": {"PEPSI": 1054, "COKE": 1050},
            "1Ltr PET": {"PEPSI": 810, "COKE": 835},
            "1.5Ltr PET": {"PEPSI": 838, "COKE": 874},
            "2Ltr PET": {"PEPSI": 0, "COKE": 999},
            "2.25Ltr PET": {"PEPSI": 1185, "COKE": 0},
        },
        "PSH": {
            "300-350ML PET": {"PEPSI": 690, "COKE": 680},
            "500ML PET": {"PEPSI": 1173, "COKE": 1173},
            "1Ltr PET": {"PEPSI": 785, "COKE": 851},
            "1.5Ltr PET": {"PEPSI": 877, "COKE": 940},
            "2Ltr PET": {"PEPSI": 0, "COKE": 940},
            "2.25Ltr PET": {"PEPSI": 1245, "COKE": 0},
        },
        "FSD": {
            "300-350ML PET": {"PEPSI": 735, "COKE": 680},
            "500ML PET": {"PEPSI": 1050, "COKE": 1050},
            "1Ltr PET": {"PEPSI": 750, "COKE": 800},
            "1.5Ltr PET": {"PEPSI": 830, "COKE": 865},
            "2Ltr PET": {"PEPSI": 0, "COKE": 999},
            "2.25Ltr PET": {"PEPSI": 1187, "COKE": 0},
        },
        "GUJ": {
            "300-350ML PET": {"PEPSI": 717, "COKE": 691},
            "500ML PET": {"PEPSI": 1052, "COKE": 1052},
            "1Ltr PET": {"PEPSI": 780, "COKE": 828},
            "1.5Ltr PET": {"PEPSI": 840, "COKE": 873},
            "2Ltr PET": {"PEPSI": 938, "COKE": 1035},
            "2.25Ltr PET": {"PEPSI": 0, "COKE": 0},
        },
        "MUL": {
            "300-350ML PET": {"PEPSI": 720, "COKE": 713},
            "500ML PET": {"PEPSI": 1050, "COKE": 1050},
            "1Ltr PET": {"PEPSI": 780, "COKE": 828},
            "1.5Ltr PET": {"PEPSI": 860, "COKE": 840},
            "2Ltr PET": {"PEPSI": 1125, "COKE": 1028},
            "2.25Ltr PET": {"PEPSI": 0, "COKE": 0},
        },
        "KHI": {
            "300-350ML PET": {"PEPSI": 782, "COKE": 713},
            "500ML PET": {"PEPSI": 1087, "COKE": 1087},
            "1Ltr PET": {"PEPSI": 782, "COKE": 845},
            "1.5Ltr PET": {"PEPSI": 1079, "COKE": 873},
            "2Ltr PET": {"PEPSI": 1071, "COKE": 1196},
            "2.25Ltr PET": {"PEPSI": 1304, "COKE": 1152},
        },
        "SUK": {
            "300-350ML PET": {"PEPSI": 715, "COKE": 680},
            "500ML PET": {"PEPSI": 1050, "COKE": 1050},
            "1Ltr PET": {"PEPSI": 800, "COKE": 847},
            "1.5Ltr PET": {"PEPSI": 889, "COKE": 865},
            "2Ltr PET": {"PEPSI": 1017, "COKE": 1017},
            "2.25Ltr PET": {"PEPSI": 1250, "COKE": 0},
        },
    }

    city_pairs = [("KHI", "HYD"), ("MUL", "BHP"), ("SUK", "RYK"), ("GJW", "SKT")]

    alias_map = {
        "GJW": "GUJ",
        "LHR": "LHE",
    }

    # -----------------------
    # Canonical SKUs used in your app (keep same order)
    # -----------------------
    skus_required = [
        "SSRB",
        "300-350 ML PET",
        "500ml PET",
        "1Ltr PET",
        "1.5Ltr PET",
        "2Ltr PET",
        "2.25Ltr PET"
    ]

    pet_skus_to_fill = [
        "300-350 ML PET",
        "500ml PET",
        "1Ltr PET",
        "1.5Ltr PET",
        "2Ltr PET",
        "2.25Ltr PET"
    ]

    def normalize_text(s):
        if pd.isna(s):
            return ""
        s = str(s).lower()
        s = re.sub(r'[^a-z0-9]', '', s)
        return s

    norm_to_canonical = {normalize_text(s): s for s in skus_required}

    invoice_reference = {}
    for city, sku_map in invoice_reference_raw.items():
        invoice_reference.setdefault(city, {})
        for sku_key, brand_map in sku_map.items():
            norm = normalize_text(sku_key)
            canonical = norm_to_canonical.get(norm)
            if not canonical:
                continue
            invoice_reference[city].setdefault(canonical, {})
            for br, val in brand_map.items():
                invoice_reference[city][canonical][str(br).upper()] = val

    def find_invoice_city_key(region):
        if pd.isna(region):
            return None
        region = str(region).strip()
        if region in invoice_reference:
            return region
        if region in alias_map and alias_map[region] in invoice_reference:
            return alias_map[region]
        for a, b in city_pairs:
            if region == a and b in invoice_reference:
                return b
            if region == b and a in invoice_reference:
                return a
        if region.upper() in invoice_reference:
            return region.upper()
        return None

    # -----------------------
    # Upload dataset
    # -----------------------
    uploaded_file = st.file_uploader("Upload file", type=["xlsx", "csv"], key="alldata_file")
    if not uploaded_file:
        st.info("Please upload a dataset to begin.")
        st.stop()

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ Dataset uploaded successfully!")

    def find_col(df, target_name):
        for col in df.columns:
            if str(col).strip().lower() == target_name.strip().lower():
                return col
        return None

    invoice_col = find_col(df, "invoice") or "Invoice"

    df["_NORM_SKU"] = df.get("SKUS", "").fillna("").apply(normalize_text)
    df["_BR_UP"] = df.get("BRAND", "").fillna("").astype(str).str.upper()
    df["_REGION"] = df.get("REGION", "").fillna("")

    region_order = [
        "National", "FSD", "GJW", "SKT", "ISB", "KHI", "HYD", "LHR", "MUL",
        "BWP", "PSH", "SUK", "RYK"
    ]

    # -----------------------
    # User filters UI
    # -----------------------
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        channel = st.selectbox("Select Channel", sorted(df["CHANNEL"].dropna().unique()))
    with col2:
        year = st.selectbox("Select Year", sorted(df["YEAR"].dropna().unique()))
    with col3:
        month = st.selectbox("Select Month", sorted(df["MON"].dropna().unique()))
    with col4:
        week = st.multiselect("Select Week(s)", sorted(df["WEEK"].dropna().unique()), default=[sorted(df["WEEK"].dropna().unique())[0]])
    with col5:
        period = st.multiselect("Select Period(s)", sorted(df["PERIOD"].dropna().unique()), default=[sorted(df["PERIOD"].dropna().unique())[0]])

    cat_filter = st.selectbox("Select Category (CAT)", ["All"] + sorted(df["CAT"].dropna().unique().tolist()))

    metric_map = {
        "NTP": find_col(df, "NTP/6P") or "NTP/6P",
        "Promo": find_col(df, "PROMO") or "PROMO",
        "TP": find_col(df, "REG TP") or "REG TP",
        "CP": find_col(df, "CP") or "CP",
        "Invoice": invoice_col
    }

    colm1, colm2, colm3, colm4 = st.columns(4)
    with colm1:
        metric = st.selectbox("Select Metric", list(metric_map.keys()))
    with colm2:
        agg_type = st.radio("Choose Aggregation", ["Average", "Minimum", "Maximum"])
    with colm3:
        if cat_filter != "All":
            brand_list = df[df["CAT"] == cat_filter]["BRAND"].dropna().unique()
        else:
            brand_list = df["BRAND"].dropna().unique()
        brand = st.selectbox("Select Brand", sorted(brand_list))
    with colm4:
        if cat_filter != "All":
            competitor_list = df[df["CAT"] == cat_filter]["BRAND"].dropna().unique()
        else:
            competitor_list = df["BRAND"].dropna().unique()
        competitor = st.selectbox("Select Competitor", sorted(competitor_list))

    if brand == competitor:
        st.warning("⚠️ Both Brand and Competitor are the same. Showing only the selected brand table.")
        same_brand_mode = True
    else:
        same_brand_mode = False

    brands_to_keep = [b for b in [brand, competitor] if pd.notna(b)]
    df_filtered = df[
        (df["CHANNEL"] == channel) &
        (df["YEAR"] == year) &
        (df["MON"] == month) &
        (df["WEEK"].isin(week)) &
        (df["PERIOD"].isin(period)) &
        (df["BRAND"].isin(brands_to_keep))
    ].copy()

    if cat_filter != "All":
        df_filtered = df_filtered[df_filtered["CAT"] == cat_filter].copy()

    df_filtered["_NORM_SKU"] = df_filtered.get("SKUS", "").fillna("").apply(normalize_text)
    df_filtered["_BR_UP"] = df_filtered.get("BRAND", "").fillna("").astype(str).str.upper()
    df_filtered["_REGION"] = df_filtered.get("REGION", "").fillna("")

    # -----------------------
    # Fill missing PET SKU rows from invoice_reference (kept as you wrote)
    # -----------------------
    brands_in_scope = [b.upper() for b in {brand, competitor} if isinstance(b, str) and b.strip() != ""]
    brands_in_scope = [b for b in brands_in_scope if b in {"PEPSI", "COKE"}]

    if brands_in_scope:
        added_rows = []
        added_count = 0
        target_regions = [r for r in region_order if str(r).upper() != "NATIONAL"]

        for region in target_regions:
            for b in brands_in_scope:
                for pet_sku in pet_skus_to_fill:
                    norm_pet_sku = normalize_text(pet_sku)
                    exists_mask = (
                        (df_filtered["_REGION"] == region) &
                        (df_filtered["_BR_UP"] == b) &
                        (df_filtered["_NORM_SKU"] == norm_pet_sku)
                    )
                    if exists_mask.any():
                        continue
                    inv_city = find_invoice_city_key(region)
                    if inv_city is None and region in alias_map:
                        inv_city = alias_map.get(region)
                    if inv_city is None:
                        for a, bpair in city_pairs:
                            if region == a and bpair in invoice_reference:
                                inv_city = bpair
                                break
                            if region == bpair and a in invoice_reference:
                                inv_city = a
                                break
                    if inv_city is None:
                        continue

                    city_map = invoice_reference.get(inv_city, {})
                    sku_map = city_map.get(pet_sku)
                    if sku_map is None:
                        found_val = None
                        for sk_key, brands_map in city_map.items():
                            if normalize_text(sk_key) == norm_pet_sku:
                                found_val = brands_map.get(b)
                                break
                        if found_val is None:
                            continue
                        invoice_val = found_val
                    else:
                        invoice_val = sku_map.get(b)

                    if invoice_val is None:
                        continue
                    try:
                        invoice_val_num = float(invoice_val)
                    except Exception:
                        continue
                    if np.isnan(invoice_val_num) or invoice_val_num == 0:
                        continue

                    new_row = {col: np.nan for col in df.columns}
                    new_row["CHANNEL"] = channel
                    new_row["YEAR"] = year
                    new_row["MON"] = month
                    new_row["WEEK"] = week[0] if isinstance(week, (list, tuple)) and len(week) > 0 else np.nan
                    new_row["PERIOD"] = period[0] if isinstance(period, (list, tuple)) and len(period) > 0 else np.nan
                    new_row["REGION"] = region
                    new_row["BRAND"] = b
                    new_row["SKUS"] = pet_sku
                    new_row[invoice_col] = invoice_val_num
                    new_row["_NORM_SKU"] = normalize_text(pet_sku)
                    new_row["_BR_UP"] = str(b).upper()
                    new_row["_REGION"] = region

                    added_rows.append(new_row)
                    added_count += 1

        if added_rows:
            df_new = pd.DataFrame(added_rows)
            for c in df_new.columns:
                if c not in df_filtered.columns:
                    df_filtered[c] = np.nan
            df_filtered = pd.concat([df_filtered, df_new[df_filtered.columns]], ignore_index=True, sort=False)
        if added_count:
            st.info(f"ℹ️ Inserted {added_count} invoice row(s) from reference table for missing PET SKUs (Pepsi/Coke).")

    # -----------------------
    # Prepare metric column & aggregate
    # -----------------------
    metric_col = metric_map.get(metric, metric_map["Invoice"])
    if metric_col not in df_filtered.columns:
        df_filtered[metric_col] = np.nan

    if agg_type == "Average":
        result = df_filtered.groupby(["REGION", "BRAND", "SKUS"])[metric_col].mean().reset_index()
    elif agg_type == "Minimum":
        result = df_filtered.groupby(["REGION", "BRAND", "SKUS"])[metric_col].min().reset_index()
    else:
        result = df_filtered.groupby(["REGION", "BRAND", "SKUS"])[metric_col].max().reset_index()

    def shorten(name):
        if not isinstance(name, str):
            return str(name)[:3]
        parts = [w for w in name.split() if w]
        return "".join([w[:3] for w in parts][:2])

    brand_map = {}
    brand_map[brand] = shorten(str(brand))
    if not same_brand_mode:
        brand_map[competitor] = shorten(str(competitor))

    # -----------------------
    # Build comparison pivot table
    # -----------------------
    if same_brand_mode:
        comparison = result[result["BRAND"] == brand].pivot_table(index="REGION", columns="SKUS", values=metric_col, aggfunc="first").reset_index()
        cols = ["REGION"] + [sku for sku in skus_required if sku in comparison.columns]
        comparison = comparison[cols]
    else:
        comparison = result.pivot_table(index="REGION", columns=["SKUS", "BRAND"], values=metric_col, aggfunc="first")
        # flatten into safe column names using brand_map.get()
        flat_cols = []
        for sku, br in comparison.columns:
            short_br = brand_map.get(br, shorten(br))
            flat_cols.append(f"{sku}_{short_br}")
        comparison.columns = flat_cols
        comparison = comparison.reset_index()
        cols = ["REGION"]
        for sku in skus_required:
            for b in [brand, competitor]:
                col_name = f"{sku}_{brand_map.get(b, shorten(b))}"
                if col_name in comparison.columns:
                    cols.append(col_name)
        cols_final = [c for c in cols if c in comparison.columns] if cols else comparison.columns.tolist()
        comparison = comparison[cols_final]

    try:
        comparison["REGION"] = pd.Categorical(comparison["REGION"], categories=region_order, ordered=True)
        comparison = comparison.sort_values("REGION").reset_index(drop=True)
    except Exception:
        comparison = comparison.sort_values("REGION").reset_index(drop=True)

    st.subheader(f"{metric} ({agg_type}) - by Region & SKUS")
    st.dataframe(comparison)

    # -----------------------
    # Download main table
    # -----------------------
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        comparison.to_excel(writer, index=False, sheet_name="Main_Table")
    st.download_button(
        label="📥 Download Main Table as Excel",
        data=buffer.getvalue(),
        file_name="main_table.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # -----------------------
    # Visualization Section (kept as in your code)
    # -----------------------
    st.markdown("---")
    st.subheader("📊 Data Visualizations")

    viz_data = result.copy()

    if len(viz_data) > 0:
        st.write("### Brand vs Competitor Comparison by Region")
        if same_brand_mode:
            viz_data_filtered = viz_data[viz_data["BRAND"] == brand]
        else:
            viz_data_filtered = viz_data[viz_data["BRAND"].isin([brand, competitor])]

        if len(viz_data_filtered) > 0:
            viz_data_filtered["Brand_SKU"] = viz_data_filtered["BRAND"] + " - " + viz_data_filtered["SKUS"]
            fig_bar = px.bar(
                viz_data_filtered,
                x="REGION",
                y=metric_col,
                color="Brand_SKU",
                barmode="group",
                title=f"{metric} Comparison by Region and SKU",
                labels={metric_col: metric, "REGION": "Region", "Brand_SKU": "Brand - SKU"}
            )
            fig_bar.update_layout(
                plot_bgcolor='black',
                paper_bgcolor='black',
                font_color='green',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.write("### Heatmap: Metric Values Across Regions and SKUs")
        if not same_brand_mode:
            heatmap_data = viz_data_filtered.pivot_table(
                index="REGION",
                columns=["BRAND", "SKUS"],
                values=metric_col,
                aggfunc='first'
            ).fillna(0)
            if not heatmap_data.empty:
                fig_heatmap = px.imshow(
                    heatmap_data,
                    title=f"Heatmap of {metric} Values",
                    color_continuous_scale="Viridis",
                    aspect="auto"
                )
                fig_heatmap.update_layout(
                    plot_bgcolor='black',
                    paper_bgcolor='black',
                    font_color='green'
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

        st.write("### Metric Trend Across SKUs")
        sku_avg = viz_data_filtered.groupby(["BRAND", "SKUS"])[metric_col].mean().reset_index()
        if len(sku_avg) > 0:
            fig_line = px.line(
                sku_avg,
                x="SKUS",
                y=metric_col,
                color="BRAND",
                markers=True,
                title=f"Average {metric} across SKUs",
                labels={metric_col: f"Average {metric}", "SKUS": "SKU"}
            )
            fig_line.update_layout(
                plot_bgcolor='black',
                paper_bgcolor='black',
                font_color='green',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_line, use_container_width=True)

        st.write("### Regional Performance Comparison")
        regional_avg = viz_data_filtered.groupby(["REGION", "BRAND"])[metric_col].mean().reset_index()
        if len(regional_avg) > 0:
            fig_regional = px.bar(
                regional_avg,
                x="REGION",
                y=metric_col,
                color="BRAND",
                barmode="group",
                title=f"Average {metric} by Region",
                labels={metric_col: f"Average {metric}", "REGION": "Region"}
            )
            fig_regional.update_layout(
                plot_bgcolor='black',
                paper_bgcolor='black',
                font_color='green',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_regional, use_container_width=True)

        st.write("### SKU Performance Comparison")
        sku_performance = viz_data_filtered.groupby(["SKUS", "BRAND"])[metric_col].mean().reset_index()
        if len(sku_performance) > 0:
            fig_sku = px.bar(
                sku_performance,
                x="SKUS",
                y=metric_col,
                color="BRAND",
                barmode="group",
                title=f"Average {metric} by SKU",
                labels={metric_col: f"Average {metric}", "SKUS": "SKU"}
            )
            fig_sku.update_layout(
                plot_bgcolor='black',
                paper_bgcolor='black',
                font_color='green',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_sku, use_container_width=True)

    else:
        st.info("No data available for visualization with current filters.")

    # -----------------------
    st.subheader("🥤 CSD Table (PEP vs KO by COMPANY)")

    # Select companies
    companies = sorted(df_filtered["COMPANY"].dropna().unique())
    pep_company = st.selectbox("Select PEP Company", companies, index=0 if "PEP" in companies else 0)
    ko_company = st.selectbox("Select KO Company", companies, index=0 if "KO" in companies else 0)

    # Select brands for each company
    pep_brands = st.multiselect(
        "Select Brands for PEP",
        sorted(df_filtered.loc[df_filtered["COMPANY"] == pep_company, "BRAND"].unique())
    )
    ko_brands = st.multiselect(
        "Select Brands for KO",
        sorted(df_filtered.loc[df_filtered["COMPANY"] == ko_company, "BRAND"].unique())
    )

    if pep_brands and ko_brands:
        # Filter for selected brands
        csd_df = df_filtered[df_filtered["BRAND"].isin(pep_brands + ko_brands)].copy()

        # Map to superbrand
        csd_df["_SUPERBRAND"] = np.where(csd_df["BRAND"].isin(pep_brands), "PEP", "KO")

        # Aggregate: REGION × SUPERBRAND × SKUS
        agg_df = csd_df.groupby(["REGION", "_SUPERBRAND", "SKUS"])[metric_col].mean().reset_index()

        # Pivot to get side by side PEP vs KO
        pep_table = agg_df[agg_df["_SUPERBRAND"] == "PEP"].pivot(index="REGION", columns="SKUS", values=metric_col)
        ko_table = agg_df[agg_df["_SUPERBRAND"] == "KO"].pivot(index="REGION", columns="SKUS", values=metric_col)

        # Align indexes and fill missing values with other company's values for same SKU
        all_regions = sorted(set(pep_table.index).union(ko_table.index))
        all_skus = sorted(set(pep_table.columns).union(ko_table.columns))

        pep_table = pep_table.reindex(index=all_regions, columns=all_skus)
        ko_table = ko_table.reindex(index=all_regions, columns=all_skus)

        pep_table = pep_table.fillna(method="ffill", axis=1).fillna(method="bfill", axis=1)
        ko_table = ko_table.fillna(method="ffill", axis=1).fillna(method="bfill", axis=1)

        # Compute comparison % (PEP vs KO)
        compare_table = (pep_table / ko_table) * 100
        compare_table = compare_table.round(0).astype("Int64")

        # Merge into one styled DataFrame
        final_table = pd.DataFrame(index=all_regions)
        for sku in all_skus:
            final_table[(sku, "PEP")] = pep_table[sku]
            final_table[(sku, "KO")] = ko_table[sku]
            final_table[(sku, "PEP vs KO %")] = compare_table[sku]

        # Flatten MultiIndex for export
        final_table.columns = [f"{sku}_{col}" for sku, col in final_table.columns]
        final_table = final_table.reset_index().rename(columns={"index": "REGION"})

        # Display
        st.dataframe(final_table)

        # Excel download
        output_csd = BytesIO()
        with pd.ExcelWriter(output_csd, engine="xlsxwriter") as writer:
            final_table.to_excel(writer, index=False, sheet_name="CSD Table")
        st.download_button(
            label="⬇️ Download CSD Table (Excel)",
            data=output_csd.getvalue(),
            file_name="csd_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Please select at least one brand for both PEP and KO to see the CSD table.")


