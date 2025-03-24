import streamlit as st
import pandas as pd
import os
from functools import reduce
from st_aggrid import AgGrid, GridOptionsBuilder

# ==================================================
# PAGE CONFIG - MUST BE FIRST
# ==================================================
st.set_page_config(page_title="Drug Blender", layout="wide")

# ==================================================
# SESSION STATE PAGE NAVIGATION
# ==================================================
def set_page(page_name: str):
    """Update the current page in session state and rerun."""
    st.session_state["current_page"] = page_name
    st.experimental_rerun()

# Initialize the page in session state if not present
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Data Ingestion"

# Define the pages to display in the sidebar
PAGES = ["Data Ingestion", "Master Document", "Analysis", "About"]

# Create a sidebar radio for navigation
selected_page = st.sidebar.radio("Navigation", PAGES, index=PAGES.index(st.session_state["current_page"]), key="sidebar_nav")
if selected_page != st.session_state["current_page"]:
    st.session_state["current_page"] = selected_page
    st.experimental_rerun()

# ==================================================
# HELPER FUNCTIONS
# ==================================================
def load_file(uploaded_file):
    """
    Reads an uploaded file (CSV, XLSX, or XLS) into a DataFrame,
    dropping completely empty columns.
    """
    _, extension = os.path.splitext(uploaded_file.name.lower())
    if extension == ".csv":
        df = pd.read_csv(uploaded_file)
    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {extension}")
    # Drop columns that are entirely empty
    df = df.loc[:, df.notna().any()]
    return df

def check_expected_key(df, file_name):
    """Ensures the DataFrame has a key column named 'ID'."""
    if "ID" not in df.columns:
        st.error(f"File {file_name} must have a column named 'ID'.")
        st.stop()

def rename_non_key_columns(df, file_name):
    """
    Renames each column except 'ID' to include the file name as a suffix.
    e.g. 'A' -> 'A__{file_name}'
    """
    new_cols = {}
    for col in df.columns:
        if col != "ID":
            new_cols[col] = f"{col}__{file_name}"
    return df.rename(columns=new_cols)

def get_file_columns(df):
    """Return the list of columns (excluding 'ID') that belong to this file."""
    return [col for col in df.columns if col != "ID"]

# ==================================================
# PAGE 1: DATA INGESTION
# ==================================================
def data_ingestion_page():
    st.title("Pharmaceutical Data Dashboard (Drug Blender)")
    st.subheader("Data Ingestion")
    st.write(
        "Upload 1–5 files (CSV, XLSX, or XLS). **Each file must have a key column named 'ID'** "
        "plus one or more additional data columns. We will rename non‑ID columns to include the file name, "
        "then merge all files horizontally (outer join) on 'ID', sorting by 'ID'."
    )

    # Unique key for file_uploader
    uploaded_files = st.file_uploader(
        "Upload 1–5 Files (CSV, XLSX, or XLS)",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        key="file_uploader_ingestion"
    )

    if uploaded_files:
        if len(uploaded_files) > 5:
            st.warning("Please upload a maximum of 5 files.")
        else:
            # Unique key for the "Process Files" button
            if st.button("Process Files", key="process_files_ingestion"):
                try:
                    df_list = []
                    file_columns = {}
                    color_map = {}
                    # Up to 5 distinct colors for the columns
                    color_palette = ["#FFCFCF", "#CFFFCF", "#CFCFFF", "#FFFACF", "#FFCFFF"]

                    for i, file in enumerate(uploaded_files):
                        df = load_file(file)
                        check_expected_key(df, file.name)
                        df = rename_non_key_columns(df, file.name)
                        file_columns[file.name] = get_file_columns(df)
                        df_list.append(df)
                        color_map[file.name] = color_palette[i]
                    
                    # Merge on 'ID' using outer join
                    from functools import reduce
                    master_df = reduce(lambda left, right: pd.merge(left, right, on="ID", how="outer"), df_list)
                    master_df = master_df.sort_values(by="ID").reset_index(drop=True)

                    # Store in session state
                    st.session_state["master_df"] = master_df
                    st.session_state["file_columns"] = file_columns
                    st.session_state["color_map"] = color_map

                    st.success("Files uploaded and merged successfully!")
                    st.write("**Preview of Merged Data (first 15 rows):**")
                    st.dataframe(master_df.head(15))
                    st.write(f"**Final Shape:** {master_df.shape} (rows, columns)")
                    st.write("**Columns:**", list(master_df.columns))
                except Exception as e:
                    st.error(f"Error processing files: {e}")
    else:
        st.info("Upload 1–5 CSV/XLSX/XLS files to get started.")

# ==================================================
# PAGE 2: MASTER DOCUMENT
# ==================================================
def master_document_page():
    st.header("Master Document")
    st.write("Below is the merged dataset with one row per ID. All data from each file appear side‑by‑side, "
             "with each file’s columns color-coded. You can drag and reorder columns interactively.")

    if ("master_df" in st.session_state and 
        "file_columns" in st.session_state and 
        "color_map" in st.session_state):

        master_df = st.session_state["master_df"]
        file_columns = st.session_state["file_columns"]
        color_map = st.session_state["color_map"]

        # Legend
        st.markdown("### Legend (File → Color):")
        for fname, color in color_map.items():
            st.markdown(
                f'<div style="display:inline-block;width:20px;height:20px;'
                f'background-color:{color};margin-right:10px;"></div>{fname}',
                unsafe_allow_html=True
            )

        # Build column definitions for AgGrid with color-coded cellStyle
        from st_aggrid import AgGrid, GridOptionsBuilder

        col_defs = []
        for col in master_df.columns:
            col_def = {"field": col}
            if col == "ID":
                # Optionally pin ID to the left
                col_def["pinned"] = "left"
            else:
                # Determine which file contributed this column
                for fname, cols in file_columns.items():
                    if col in cols:
                        col_def["cellStyle"] = {
                            "backgroundColor": color_map[fname],  # JS-style camelCase
                            "color": "#000000"                    # ensure text is visible
                        }
                        break
            col_defs.append(col_def)

        # Build AgGrid options
        gb = GridOptionsBuilder.from_dataframe(master_df)
        gb.configure_grid_options(enableColReorder=True)
        gridOptions = gb.build()
        gridOptions["columnDefs"] = col_defs

        # Display the AgGrid
        AgGrid(
            master_df,
            gridOptions=gridOptions,
            height=500,
            width='100%',
            reload_data=True,
            enable_enterprise_modules=False,
            allow_unsafe_jscode=True,
            theme='streamlit'
        )

        # Download button for merged data
        csv_data = master_df.to_csv(index=False)
        st.download_button(
            label="Download Merged Data as CSV",
            data=csv_data,
            file_name="merged_data.csv",
            mime="text/csv",
            key="download_merged_data_btn"
        )
    else:
        st.warning("No merged data found. Please go to Data Ingestion first.")

# ==================================================
# PAGE 3: ANALYSIS
# ==================================================
def analysis_page():
    st.header("Analysis & Insights")
    st.write("This page provides a high-level analysis of the merged data.")

    if "master_df" in st.session_state:
        master_df = st.session_state["master_df"]

        numeric_cols = master_df.select_dtypes(include=["int", "float"]).columns
        if len(numeric_cols) > 0:
            st.subheader("Numeric Column Summaries")
            st.write(master_df[numeric_cols].describe())
        else:
            st.info("No numeric columns found to summarize.")

        missing_counts = master_df.isna().sum()
        if missing_counts.sum() > 0:
            st.subheader("Missing Data Overview")
            st.write(missing_counts[missing_counts > 0])
        else:
            st.write("No missing data found.")

        total_rows = len(master_df)
        total_cols = len(master_df.columns)
        st.write(f"**Total Rows:** {total_rows}")
        st.write(f"**Total Columns:** {total_cols}")

        st.write("""
            ### Additional Insights (Placeholder)
            - Domain-specific analysis can be added here.
            - Consider visualizations like histograms or correlation matrices.
        """)
    else:
        st.warning("No data found. Please upload files and create a master document first.")

# ==================================================
# PAGE 4: ABOUT
# ==================================================
def about_page():
    st.header("About This Dashboard")
    st.write("""
        **Drug Blender** merges multiple CSV/Excel files horizontally by a shared 'ID' column,
        renames non‑ID columns to include the file name, and color-codes columns based on file origin.
        It offers:
        
        - Data Ingestion (upload/merge)
        - Master Document (color-coded, draggable columns in AgGrid)
        - Analysis (numeric summaries, missing data, placeholders for domain-specific insights)
        - About (general info)
        
        **Installation**:
        - `pip install streamlit-aggrid`
        - or add `streamlit-aggrid` to your `requirements.txt`.
        
        **Usage**:
        - Run `streamlit run app.py`
        - Navigate between pages using the sidebar.
    """)

# ==================================================
# MAIN APP LOGIC
# ==================================================
def main():
    current_page = st.session_state["current_page"]
    if current_page == "Data Ingestion":
        data_ingestion_page()
    elif current_page == "Master Document":
        master_document_page()
    elif current_page == "Analysis":
        analysis_page()
    else:
        about_page()

if __name__ == "__main__":
    main()
