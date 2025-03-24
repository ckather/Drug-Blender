import streamlit as st
import pandas as pd
import os
from functools import reduce

# -------------------------
# Helper Functions
# -------------------------

def load_file(uploaded_file):
    """
    Reads an uploaded file (CSV, XLSX, or XLS) into a DataFrame.
    Drops any completely empty columns.
    """
    _, extension = os.path.splitext(uploaded_file.name.lower())
    if extension == ".csv":
        df = pd.read_csv(uploaded_file)
    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {extension}")
    # Drop empty columns
    df = df.loc[:, df.notna().any()]
    return df

def check_expected_key(df, file_name):
    """
    Verifies that the DataFrame has the key column "ID".
    """
    expected = {"ID"}
    if expected.issubset(set(df.columns)) is False:
        st.error(f"File {file_name} must have the column: {expected}")
        st.stop()

def rename_non_key_columns(df, file_name):
    """
    Renames each column except 'ID' to include the file name as a suffix.
    For example, if a file has columns ["ID", "A", "B"], they become:
    ["ID", "A__{file_name}", "B__{file_name}"]
    """
    new_cols = {}
    for col in df.columns:
        if col != "ID":
            new_cols[col] = f"{col}__{file_name}"
    return df.rename(columns=new_cols)

def get_file_columns(df):
    """
    Returns a list of data columns (i.e. non-"ID" columns) in the DataFrame.
    """
    return [col for col in df.columns if col != "ID"]

def style_merged_df(df, file_columns, color_map):
    """
    Styles the merged DataFrame so that each column is colored based on which file it came from.
    """
    styled = df.style  # Start with a Styler object

    # For each file, set background color for the columns that originated from that file
    for file_name, columns in file_columns.items():
        color = color_map[file_name]
        styled = styled.set_properties(subset=columns, **{'background-color': color})

    return styled

# -------------------------
# Streamlit Layout
# -------------------------

st.set_page_config(page_title="Drug Blender (Merged by ID)", layout="wide")

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
        "Upload 1–5 files (CSV, XLSX, or XLS). **Each file must have a key column named 'ID'** plus one or more additional data columns. "
        "The app will rename the non‑ID columns to include the file name, merge all files horizontally (outer join) on 'ID', sort by 'ID', "
        "and display one row per ID with all data side‑by‑side."
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
                file_columns = {}  # Mapping: file name -> list of renamed data columns
                # Define a color palette for up to 5 files
                color_palette = ["#FFCFCF", "#CFFFCF", "#CFCFFF", "#FFFACF", "#FFCFFF"]
                color_map = {}
                
                for i, file in enumerate(uploaded_files):
                    df = load_file(file)
                    # Check that the file has the key column "ID"
                    check_expected_key(df, file.name)
                    # Rename non-ID columns to include the file name
                    df = rename_non_key_columns(df, file.name)
                    # Record the data columns for this file (all columns except "ID")
                    file_columns[file.name] = get_file_columns(df)
                    
                    df_list.append(df)
                    color_map[file.name] = color_palette[i]
                
                # Merge all DataFrames on "ID" using outer join.
                master_df = reduce(lambda left, right: pd.merge(left, right, on="ID", how="outer"), df_list)
                master_df = master_df.sort_values(by="ID").reset_index(drop=True)
                
                st.session_state["master_df"] = master_df
                st.session_state["file_columns"] = file_columns
                st.session_state["color_map"] = color_map
                
                st.success("Files uploaded and merged successfully.")
                st.write("**Preview of Merged Data (first 15 rows):**")
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
    st.write("Below is the merged dataset with one row per ID. All data from each file appear side‑by‑side.")

    if "master_df" in st.session_state and "file_columns" in st.session_state and "color_map" in st.session_state:
        master_df = st.session_state["master_df"]
        file_columns = st.session_state["file_columns"]
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
        
        # --- Style the merged DataFrame ---
        styled_df = style_merged_df(master_df, file_columns, color_map)
        st.write(styled_df.render(), unsafe_allow_html=True)
        
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
        This **Drug Blender** version expects each uploaded file to have a key column named 'ID' 
        plus one or more additional data columns. The non‑ID columns are renamed to include the file name, 
        and then all files are merged (outer join) horizontally on 'ID' so that each ID appears once with all data side‑by‑side.
        
        **Features:**
        - Accepts CSV, XLSX, or XLS files.
        - Merges files by 'ID' so each ID appears in one row.
        - Renames non‑ID columns to include the file name.
        - Color-codes columns based on the source file, with a legend.
        - Provides a quick numeric summary if applicable.
        
        Built with Python and Streamlit.
    """)

