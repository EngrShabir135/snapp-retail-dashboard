"""
Streamlit app: Kobo image downloader with Username/Password authentication (using Basic Auth)

Enhanced Features:
- Upload an Excel/CSV file containing Kobo Toolbox image URLs.
- Must contain a "City" column.
- First fixed columns (start, end, Auditor Name, City, Survey Date, Bill Date, Shop Name) are skipped.
- Each remaining brand URL column (e.g., PEPSI BILL PICTURE_URL, COKE BILL PICTURE_URL) is auto-detected.
- Creates folders as: images_downloaded/BrandName/CityName/
- File names: City_BrPrefix_bill_xxx.ext (e.g., Karachi_PE_bill_1.jpg).
- Uses Basic Auth for all requests.
- Downloads images with retries and detects file type.
- Shows progress, allows downloading a ZIP of all images, and logs failed links.
"""

import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
import os
import mimetypes
import time
from io import BytesIO
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import filetype


def run():
    st.title("📊 Download images from KOBO")
    st.write("This app downloads images from KOBO for both GT and WS")

    # ------- Helper functions -------

    def sanitize_name(s):
        """Clean folder/file names."""
        return "".join(c for c in str(s) if c.isalnum() or c in (' ','_','-')).strip().replace(" ", "_")


    def detect_extension(content, content_type, url):
        """Detect proper file extension."""
        kind = filetype.guess(content)
        if kind:
            return kind.extension
        if content_type:
            guessed = mimetypes.guess_extension(content_type.split(';')[0].strip())
            if guessed:
                return guessed.lstrip('.')
        path = urlparse(url).path
        ext2 = os.path.splitext(path)[1]
        if ext2 and len(ext2) <= 6:
            return ext2.lstrip('.')
        return 'jpg'


    def download_one(session, url, dest_name, folder, timeout=20, max_retries=2):
        """Download a single file with retries."""
        last_exc = None
        for attempt in range(max_retries+1):
            try:
                resp = session.get(url, stream=True, timeout=timeout)
                if resp.status_code == 200:
                    content = resp.content
                    content_type = resp.headers.get('Content-Type', '')
                    ext = detect_extension(content, content_type, url)
                    final_name = f"{dest_name}.{ext}"
                    final_path = os.path.join(folder, final_name)
                    with open(final_path, 'wb') as f:
                        f.write(content)
                    return True, final_name, None
                else:
                    last_exc = f'HTTP {resp.status_code}'
            except Exception as e:
                last_exc = str(e)
            time.sleep(0.5 * (attempt+1))
        return False, None, last_exc


    def extract_brand_name(col):
        """Extract brand name from column header."""
        clean = col.replace("_", " ").strip()
        parts = clean.split()
        if parts:
            return parts[0].capitalize()  # e.g., 'PEPSI BILL PICTURE_URL' → 'Pepsi'
        return "Unknown"


    # ------- Streamlit app -------


    st.write('Upload an Excel/CSV file that contains Kobo Toolbox image links. '
            'The app will organize downloads by Brand → City.')

    # Username and Password
    username = st.text_input('Kobo Username', '')
    password = st.text_input('Kobo Password', type='password')

    concurrency = st.slider('Concurrent downloads', min_value=1, max_value=10, value=3)
    timeout = st.number_input('Request timeout (seconds)', value=20, min_value=5, max_value=120)
    max_retries = st.number_input('Max retries per URL', value=2, min_value=0, max_value=5)

    uploaded_file = st.file_uploader('Upload Excel or CSV file with links (must include "City" column)', type=['xlsx','xls','csv'])

    if uploaded_file is not None and username and password:
        try:
            if uploaded_file.name.endswith(('.xls','.xlsx')):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f'Error reading file: {e}')
            st.stop()

        st.markdown('**Preview of file**')
        st.dataframe(df.head(50))

        if "City" not in df.columns:
            st.error("Error: No 'City' column found in file. Please check header names.")
            st.stop()

        folder_name = st.text_input('Grand folder to save images', value='images_downloaded')
        start_index = st.number_input('Start numbering from', min_value=1, value=1)

        if st.button('Start download'):
            with st.spinner("Downloading..."):
                try:
                    session = requests.Session()
                    session.auth = HTTPBasicAuth(username, password)
                    os.makedirs(folder_name, exist_ok=True)

                    results = []
                    counter = start_index - 1

                    # Skip first fixed columns
                    fixed_cols = ["start", "end", "Auditor Name", "City", "Survey Date", "Bill Date", "Shop Name"]

                    url_cols = [col for col in df.columns if col not in fixed_cols]

                    future_to_row = {}
                    with ThreadPoolExecutor(max_workers=concurrency) as executor:
                        for col in url_cols:
                            if not df[col].astype(str).str.startswith(("http://","https://")).any():
                                continue

                            brand_name = sanitize_name(extract_brand_name(col))
                            brand_prefix = brand_name[:2].upper()

                            for _, row in df.iterrows():
                                city = sanitize_name(row["City"])
                                url = str(row[col]).strip()
                                if not (url.startswith("http://") or url.startswith("https://")):
                                    continue

                                counter += 1
                                city_folder = os.path.join(folder_name, brand_name, city)
                                os.makedirs(city_folder, exist_ok=True)

                                dest_name = f"{city}_{brand_prefix}_bill_{counter}"
                                future = executor.submit(download_one, session, url, dest_name, city_folder, timeout, max_retries)
                                future_to_row[future] = (url, brand_name, city)

                        progress_bar = st.progress(0)
                        done = 0
                        total = len(future_to_row)
                        log_lines = []

                        for future in as_completed(future_to_row):
                            url, brand, city = future_to_row[future]
                            success, final_name, error = future.result()
                            done += 1
                            progress_bar.progress(done/total)
                            if success:
                                log_lines.append(f'✅ {brand}/{city}: {url} -> {final_name}')
                                results.append((url, os.path.join(brand, city, final_name), True, None))
                            else:
                                log_lines.append(f'❌ {brand}/{city}: {url} -> {error}')
                                results.append((url, None, False, error))
                            if done % 10 == 0:
                                st.text("\n".join(log_lines[-20:]))

                    # Summary
                    succ = sum(1 for r in results if r[2])
                    fail = sum(1 for r in results if not r[2])
                    st.success(f"Download complete ✅ Successful: {succ}, Failed: {fail}")

                    if succ > 0:
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for _, fname, ok, _ in results:
                                if ok and fname:
                                    fpath = os.path.join(folder_name, fname)
                                    if os.path.exists(fpath):
                                        zipf.write(fpath, fname)
                        zip_buffer.seek(0)
                        st.download_button('Download ZIP of images', data=zip_buffer, file_name=f'{folder_name}.zip')

                    if fail > 0:
                        failed_links = [url for url, _, ok, _ in results if not ok]
                        fail_df = pd.DataFrame(failed_links, columns=['failed_url'])
                        csv_buffer = BytesIO()
                        fail_df.to_csv(csv_buffer, index=False)
                        st.download_button('Download failed links CSV', data=csv_buffer.getvalue(), file_name='failed_links.csv', mime='text/csv')

                except Exception as e:
                    st.error(f"Error: {e}")

    else:
        st.info('Upload a file and enter your Kobo username & password to begin.')