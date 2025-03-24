import streamlit as st
import pandas as pd
import os

# -------------------------
# Helper Functions
# -------------------------

def load_file(uploaded_file):
    """
    Reads an uploaded file (CSV, XLSX, or XLS) into a DataFrame.
    Expects exactly one column: 'unique_id'.
    """
    _, extension = os.path.splitext(uploaded_file.name.lower())
    if extension == ".csv":
        df = pd.read_csv(uploaded_file)
    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {extension}")
    return df

def check_expected_columns(df, file_name):
    """
    Verifies that the DataFrame has exactly the column: {'unique_id'}.
    """
    expected = {"unique_id"}
    if set(df.columns) != expected:
        st.error(f"File {file_name} must have exactly the column: {expected}")
        st.stop()

def color_rows_by_source(row, color_map):
    """
    Returns a list of CSS styles for each cell in the row based on the file indicated in 'source_file'.
    """
    file_name = row["source_file"]
    color = color_map.get(file_name, "#FFFFFF")
    return [f"background-color: {color}"] * len(row)

# -------------------------
# Streamlit Layout
# -------------------------

st.set_page_config(page_title="Drug Blender", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    h1, h2, h3 { color: #003366; }
    .upload-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .legend-box {
        background-color: #fff;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    .legend-item {
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Sidebar Navigation
# -------------------------

app_mode = st.sidebar.radio("Go to", ["Data Ingestion", "Master Document", "About"])

# -------------------------
# 1) DATA INGESTION PAGE
# -------------------------
if app_mode == "Data Ingestion":
    st.title("Pharmaceutical Data Dashboard (Drug Blender)")
    st.subheader("Data Ingestion")
    st.write(
        "Upload 1–5 files (CSV, XLSX, or XLS). Each file must have exactly one column: "
        "`unique_id`. The app will concatenate them, add a `source_file` column, and sort by `unique_id`."
    )

    with st.container():
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload 1–5 Files (CSV, XLSX, or XLS)",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        if len(uploaded_files) > 5:
            st.warning("Please upload a maximum of 5 files.")
        else:
            try:
                df_list = []
                # Define a color palette for up to 5 files
                color_palette = ["#FFCFCF", "#CFFFCF", "#CFCFFF", "#FFFACF", "#FFCFFF"]
                color_map = {}
                
                for i, file in enumerate(uploaded_files):
                    df = load_file(file)
                    
                    # Check that the file has exactly the expected column.
                    check_expected_columns(df, file.name)
                    
                    # Keep only the 'unique_id' column
                    df = df[["unique_id"]]
                    
                    # Add a 'source_file' column
                    df["source_file"] = file.name
                    color_map[file.name] = color_palette[i]
                    
                    df_list.append(df)
                
                # Concatenate (append) all data
                master_df = pd.concat(df_list, ignore_index=True)
                # Sort by unique_id so that all rows for each unique_id appear consecutively
                master_df = master_df.sort_values(by="unique_id", ignore_index=True)
                
                # Store in session_state
                st.session_state["master_df"] = master_df
                st.session_state["color_map"] = color_map
                
                st.success("Files uploaded and combined successfully (2 columns plus source_file).")
                st.write("**Preview of Combined & Sorted Data (first 15 rows):**")
                st.dataframe(master_df.head(15))
                st.write(f"**Final Shape:** {master_df.shape} (rows, columns)")
                st.write("**Columns:**", list(master_df.columns))
                
            except Exception as e:
                st.error(f"An error occurred while processing the files: {e}")
    else:
        st.info("Upload 1–5 CSV/XLSX/XLS files to get started.")

# -------------------------
# 2) MASTER DOCUMENT PAGE
# -------------------------
elif app_mode == "Master Document":
    st.header("Master Document")
    st.write("Below is the combined dataset (2 columns: `unique_id`, `source_file`), sorted by `unique_id`.")

    if "master_df" in st.session_state and "color_map" in st.session_state:
        master_df = st.session_state["master_df"]
        color_map = st.session_state["color_map"]
        
        # --- Legend ---
        st.markdown('<div class="legend-box">', unsafe_allow_html=True)
        st.write("**Legend (File → Color):**")
        for file_name, color in color_map.items():
            st.markdown(
                f'<div class="legend-item">'
                f'<span style="display:inline-block;width:20px;height:20px;background-color:{color};margin-right:10px;"></span>'
                f'{file_name}'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- Color-code rows by source_file ---
        def apply_color(row):
            return [f"background-color: {color_map[row['source_file']]}" for _ in row]
        
        styled_df = master_df.style.apply(apply_color, axis=1)
        
        st.markdown(styled_df.to_html(), unsafe_allow_html=True)
        
        numeric_cols = master_df.select_dtypes(include=["int", "float"]).columns
        if len(numeric_cols) > 0:
            st.subheader("Numeric Column Summaries")
            st.write(master_df.describe())
    else:
        st.warning("No data available. Please upload files in the Data Ingestion section.")

# -------------------------
# 3) ABOUT PAGE
# -------------------------
elif app_mode == "About":
    st.header("About This Dashboard")
    st.write("""
        This **Drug Blender** version ensures exactly 2 columns from your files:
        1. `unique_id`
        
        A third column, `source_file`, is added to track the origin of each row.
        
        **No NaNs** occur because each uploaded file must have exactly the column: {'unique_id'}.
        Rows are simply concatenated and then sorted by `unique_id`.
        
        **Features:**
        - Accepts CSV, XLSX, or XLS files.
        - Color-coded rows (one color per file).
        - A legend mapping file names to colors.
        - Quick summary of numeric columns if present.
        
        Built with Python and Streamlit.
    """)

