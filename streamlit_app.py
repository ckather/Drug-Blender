import streamlit as st
import pandas as pd
import os
from functools import reduce

# =================================
# PAGE NAVIGATION MANAGEMENT
# =================================
def go_to_page(page_name: str):
    st.session_state["page"] = page_name

# Initialize the session state for the page
if "page" not in st.session_state:
    st.session_state["page"] = "Data Ingestion"

# =================================
# HELPER FUNCTIONS
# =================================

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

# =================================
# PAGE 1: DATA INGESTION
# =================================
def data_ingestion_page():
    st.title("Pharmaceutical Data Dashboard (Drug Blender)")
    st.subheader("Data Ingestion")
    st.write(
        "Upload 1–5 files (CSV, XLSX, or XLS). **Each file must have a key column named 'ID'** "
        "plus one or more additional data columns. The app will rename non‑ID columns to include the file name, "
        "merge all files horizontally on 'ID' (outer join), sort by 'ID', and display one row per ID."
    )

    uploaded_files = st.file_uploader(
        "Upload 1–5 Files (CSV, XLSX, or XLS)",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 5:
            st.warning("Please upload a maximum of 5 files.")
        else:
            if st.button("Process Files"):
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

                    # Once processed, show a "Continue" button
                    if st.button("Continue → Master Document"):
                        go_to_page("Master Document")

                except Exception as e:
                    st.error(f"An error occurred while processing the files: {e}")

# =================================
# PAGE 2: MASTER DOCUMENT
# =================================
def master_document_page():
    st.header("Master Document")
    st.write("Below is the merged dataset with one row per ID. All data from each file appear side‑by‑side.")

    if ("master_df" in st.session_state and 
        "file_columns" in st.session_state and 
        "color_map" in st.session_state):
        
        master_df = st.session_state["master_df"]
        file_columns = st.session_state["file_columns"]
        color_map = st.session_state["color_map"]
        
        # --- Legend ---
        st.markdown("### Legend (File → Color)")
        for file_name, color in color_map.items():
            st.markdown(
                f'<div style="display:inline-block;width:20px;height:20px;background-color:{color};margin-right:10px;"></div>'
                f'{file_name}',
                unsafe_allow_html=True
            )
        
        # --- Style the merged DataFrame ---
        styled_df = style_merged_df(master_df, file_columns, color_map)
        st.write(styled_df.render(), unsafe_allow_html=True)
        
        # Download button for merged data
        csv_data = master_df.to_csv(index=False)
        st.download_button(
            label="Download Merged Data as CSV",
            data=csv_data,
            file_name="merged_data.csv",
            mime="text/csv"
        )

        if st.button("Continue → Analysis"):
            go_to_page("Analysis")
    else:
        st.warning("No data available. Please go back to the Data Ingestion page.")

# =================================
# PAGE 3: ANALYSIS
# =================================
def analysis_page():
    st.header("Analysis & Insights")
    st.write("This page provides a high-level analysis of the merged data.")
    
    if "master_df" in st.session_state:
        master_df = st.session_state["master_df"]
        
        # Example: Basic numeric stats
        numeric_cols = master_df.select_dtypes(include=["int", "float"]).columns
        if len(numeric_cols) > 0:
            st.subheader("Numeric Column Summaries")
            st.write(master_df[numeric_cols].describe())
        else:
            st.info("No numeric columns found to summarize.")
        
        # Example: Count how many rows have missing data
        missing_counts = master_df.isna().sum()
        if missing_counts.sum() > 0:
            st.subheader("Missing Data Overview")
            st.write(missing_counts[missing_counts > 0])
        else:
            st.write("No missing data found.")
        
        # Example: High-level text-based insights (very basic placeholder)
        total_rows = len(master_df)
        total_cols = len(master_df.columns)
        st.write(f"**Total Rows:** {total_rows}")
        st.write(f"**Total Columns:** {total_cols}")
        
        st.write("""
            ### Additional Insights (Placeholder)
            - You could add domain-specific analysis here, 
              like detecting outliers or grouping by certain columns.
        """)
        
    else:
        st.warning("No data available. Please upload files and create a master document first.")

# =================================
# PAGE 4: ABOUT
# =================================
def about_page():
    st.header("About This Dashboard")
    st.write("""
        **Drug Blender** merges multiple CSV/Excel files horizontally by a shared 'ID' column, 
        color-codes the columns based on file origin, and offers a quick analysis page.
        
        **Features**:
        - 1–5 input files, each with key column 'ID' and additional data columns
        - Merged into one row per 'ID' (outer join)
        - Downloadable final CSV
        - Basic numeric and missing-data analysis
    """)

# =================================
# MAIN APP LOGIC
# =================================
def main():
    st.set_page_config(page_title="Drug Blender Workflow", layout="wide")

    page = st.session_state["page"]
    
    if page == "Data Ingestion":
        data_ingestion_page()
    elif page == "Master Document":
        master_document_page()
    elif page == "Analysis":
        analysis_page()
    else:
        about_page()

if __name__ == "__main__":
    main()

