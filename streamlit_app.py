import streamlit as st
import pandas as pd
import os
import numpy as np

# ===============================
# Part 1: Generate Sample CSV Files
# ===============================
def generate_sample_csv_files():
    # Define file names and their specific extra columns (besides the unique ID)
    samples = {
        "sample1.csv": {"A": lambda i: np.random.randint(0, 100), "B": lambda i: np.random.choice(["X", "Y", "Z"])},
        "sample2.csv": {"C": lambda i: np.random.rand(), "D": lambda i: np.random.choice(["Red", "Green", "Blue"])},
        "sample3.csv": {"E": lambda i: np.random.randint(100, 200), "F": lambda i: np.random.choice(["M", "F"])},
        "sample4.csv": {"G": lambda i: np.random.choice(["Yes", "No"]), "H": lambda i: np.random.rand() * 50},
    }
    
    for filename, col_funcs in samples.items():
        if not os.path.exists(filename):
            data = {"unique_id": list(range(1, 101))}  # unique IDs 1 to 100
            # Add extra columns with generated data
            for col, func in col_funcs.items():
                data[col] = [func(i) for i in range(1, 101)]
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            print(f"Generated {filename}")

# Generate sample CSV files if they don't exist
generate_sample_csv_files()

# ===============================
# Part 2: Streamlit Drug Blender App
# ===============================

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
        "Upload between 1 and 5 CSV or Excel files. Each file should have a unique identifier (e.g., a unique number in 'unique_id') and different additional columns. "
        "When combined, rows from each file will be highlighted in a unique color."
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
                
                # Save the master DataFrame and the color map in session state.
                st.session_state["master_df"] = master_df
                st.session_state["color_map"] = color_map
                
                st.success("Files uploaded and combined successfully!")
                st.write("**Preview of Combined Data:**")
                st.dataframe(master_df.head())
            except Exception as e:
                st.error(f"An error occurred while processing the files: {e}")
    else:
        st.info("Please upload at least one file to get started.\n\n(You can use the generated CSV files: sample1.csv, sample2.csv, sample3.csv, sample4.csv.)")

# ---------------------------
# 2) MASTER DOCUMENT PAGE
# ---------------------------
elif app_mode == "Master Document":
    st.header("Master Document")
    st.write("Below is the combined dataset with each file’s rows highlighted in a unique color. A legend of colors to file names is provided below.")

    if "master_df" in st.session_state and "color_map" in st.session_state:
        master_df = st.session_state["master_df"]
        color_map = st.session_state["color_map"]
        
        # Display the legend: file names with their associated colors.
        st.markdown('<div class="legend-box">', unsafe_allow_html=True)
        st.write("**Legend:**")
        for file_name, color in color_map.items():
            st.markdown(f'<div class="legend-item"><span style="display:inline-block;width:20px;height:20px;background-color:{color};margin-right:10px;"></span>{file_name}</div>', unsafe_allow_html=True)
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
        
        **Key Features:**
        - Upload between 1 and 5 files.
        - Combine them into a single table with each file’s rows uniquely highlighted.
        - A legend is provided on the Master Document page to map colors to file names.
        - Easily view summary statistics for numeric data.
        
        Built with Python and Streamlit.
    """)

