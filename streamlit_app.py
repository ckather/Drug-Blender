import streamlit as st
import pandas as pd
import os

# --- Helper function to read a file based on its extension ---
def load_file(uploaded_file):
    """
    Reads an uploaded file into a Pandas DataFrame based on its extension.
    Supported extensions: .csv, .xlsx, .xls
    """
    _, extension = os.path.splitext(uploaded_file.name.lower())
    if extension == ".csv":
        return pd.read_csv(uploaded_file)
    elif extension in [".xlsx", ".xls"]:
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

# --- Helper function to assign a background color to a row based on its source ---
def color_rows_by_source(row, color_map):
    file_name = row["source_file"]
    color = color_map.get(file_name, "#FFFFFF")
    return [f"background-color: {color}"] * len(row)

# --- Custom CSS for beautification ---
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

# --- Sidebar Navigation ---
app_mode = st.sidebar.radio("Go to", ["Data Ingestion", "Master Document", "About"])

# ---------------------------
# 1) DATA INGESTION PAGE
# ---------------------------
if app_mode == "Data Ingestion":
    st.title("Pharmaceutical Data Dashboard (Drug Blender)")
    st.subheader("Data Ingestion")
    st.write(
        "Upload between 1 and 5 CSV or Excel files. Each file should have a `unique_id` column, "
        "plus additional columns. Rows will be combined and then **sorted by `unique_id`**, so you can see "
        "all rows for ID=1 together, then ID=2, etc."
    )

    with st.container():
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel Files (1–5)",
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
                # Define a palette of colors for up to 5 files.
                color_palette = ["#FFCFCF", "#CFFFCF", "#CFCFFF", "#FFFACF", "#FFCFFF"]
                color_map = {}
                
                for i, file in enumerate(uploaded_files):
                    df = load_file(file)
                    # Add a new column to record the source file.
                    df["source_file"] = file.name
                    color_map[file.name] = color_palette[i]
                    df_list.append(df)
                
                # Merge the files by concatenating them (stacking rows).
                master_df = pd.concat(df_list, ignore_index=True)
                
                # --- SORT by unique_id so all rows for each ID appear together ---
                if "unique_id" in master_df.columns:
                    master_df = master_df.sort_values(by="unique_id").reset_index(drop=True)
                else:
                    st.warning("No column named 'unique_id' found. Sorting may not work as intended.")
                
                # Save the master DataFrame and the color map in session state.
                st.session_state["master_df"] = master_df
                st.session_state["color_map"] = color_map
                
                st.success("Files uploaded, combined, and sorted successfully!")
                st.write("**Preview of Combined & Sorted Data:**")
                st.dataframe(master_df.head(20))  # Show a larger preview if you like
            except Exception as e:
                st.error(f"An error occurred while processing the files: {e}")
    else:
        st.info("Please upload at least one file to get started.")

# ---------------------------
# 2) MASTER DOCUMENT PAGE
# ---------------------------
elif app_mode == "Master Document":
    st.header("Master Document")
    st.write("Below is the combined dataset, sorted by `unique_id`, with each file’s rows highlighted in a unique color.")

    if "master_df" in st.session_state and "color_map" in st.session_state:
        master_df = st.session_state["master_df"]
        color_map = st.session_state["color_map"]
        
        # Display the legend: file names with their associated colors.
        st.markdown('<div class="legend-box">', unsafe_allow_html=True)
        st.write("**Legend:**")
        for file_name, color in color_map.items():
            st.markdown(
                f'<div class="legend-item">'
                f'<span style="display:inline-block;width:20px;height:20px;background-color:{color};'
                f'margin-right:10px;"></span>{file_name}</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Style the DataFrame to apply color-coding to each row.
        styled_df = master_df.style.apply(lambda row: color_rows_by_source(row, color_map), axis=1)
        
        # Render the styled DataFrame as HTML.
        st.markdown(styled_df.render(), unsafe_allow_html=True)
        
        # Optionally, display summary statistics for numeric columns.
        numeric_cols = master_df.select_dtypes(include=["int", "float"]).columns
        if len(numeric_cols) > 0:
            st.subheader("Numeric Column Summaries")
            st.write(master_df.describe())
        else:
            st.info("No numeric columns found to summarize.")
    else:
        st.warning("No data available. Please upload files in the Data Ingestion section.")

# ---------------------------
# 3) ABOUT PAGE
# ---------------------------
elif app_mode == "About":
    st.header("About This Dashboard")
    st.write("""
        This dashboard, affectionately known as the **Drug Blender**, integrates multiple CSV or Excel files into a single, unified master document.
        Each file’s data is color-coded so you can easily see which file each row came from.
        
        **Key Features**:
        - Upload between 1 and 5 files.
        - Combine them into a single table, then **sort by `unique_id`** so rows for the same ID appear together.
        - A legend maps each file to its unique highlight color.
        - Easily view summary statistics for numeric data.
        
        Built with Python and Streamlit.
    """)
