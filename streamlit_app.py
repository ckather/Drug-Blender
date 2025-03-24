import streamlit as st
import pandas as pd
import os
from functools import reduce

# =================================
# PAGE NAVIGATION VIA SIDEBAR
# =================================
def set_page(page_name: str):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()  # Force a rerun to update the page

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Data Ingestion"

# List of pages in the sidebar
PAGES = ["Data Ingestion", "Master Document", "Analysis", "About"]

# Create the sidebar radio for navigation
selected_page = st.sidebar.radio("Navigation", PAGES, index=PAGES.index(st.session_state["current_page"]))
if selected_page != st.session_state["current_page"]:
    st.session_state["current_page"] = selected_page
    st.experimental_rerun()

# =================================
# HELPER FUNCTIONS
# =================================

def load_file(uploaded_file):
    """Reads an uploaded file (CSV, XLSX, or XLS) into a DataFrame, dropping empty columns."""
    _, extension = os.path.splitext(uploaded_file.name.lower())
    if extension == ".csv":
        df = pd.read_csv(uploaded_file)
    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {extension}")
    df = df.loc[:, df.notna().any()]
    return df

def check_expected_key(df, file_name):
    """Verifies that the DataFrame has the key column 'ID'."""
    expected = {"ID"}
    if not expected.issubset(df.columns):
        st.error(f"File {file_name} must have the column: {expected}")
        st.stop()

def rename_non_key_columns(df, file_name):
    """
    Renames each column except 'ID' to include the file name as a suffix.
    For example, if columns are ["ID", "A", "B"], they become:
    ["ID", "A__{file_name}", "B__{file_name}"]
    """
    new_cols = {}
    for col in df.columns:
        if col != "ID":
            new_cols[col] = f"{col}__{file_name}"
    return df.rename(columns=new_cols)

def get_file_columns(df):
    """Returns the non-'ID' columns in the DataFrame."""
    return [col for col in df.columns if col != "ID"]

def style_merged_df(df, file_columns, color_map):
    """
    Applies background colors to columns based on the file they came from.
    """
    styled = df.style
    for file_name, cols in file_columns.items():
        color = color_map[file_name]
        styled = styled.set_properties(subset=cols, **{'background-color': color})
    return styled

# =================================
# PAGE IMPLEMENTATIONS
# =================================

def data_ingestion_page():
    st.title("Pharmaceutical Data Dashboard (Drug Blender)")
    st.subheader("Data Ingestion")
    st.write(
        "Upload 1–5 files (CSV, XLSX, or XLS). **Each file must have a key column named 'ID'** "
        "plus one or more additional data columns. We'll rename non‑ID columns to include the file name, "
        "merge all files horizontally (outer join) on 'ID', sort by 'ID', and display one row per ID."
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
                    file_columns = {}
                    color_map = {}
                    color_palette = ["#FFCFCF", "#CFFFCF", "#CFCFFF", "#FFFACF", "#FFCFFF"]

                    for i, file in enumerate(uploaded_files):
                        df = load_file(file)
                        check_expected_key(df, file.name)
                        df = rename_non_key_columns(df, file.name)
                        file_columns[file.name] = get_file_columns(df)
                        df_list.append(df)
                        color_map[file.name] = color_palette[i]
                    
                    master_df = reduce(lambda left, right: pd.merge(left, right, on="ID", how="outer"), df_list)
                    master_df = master_df.sort_values(by="ID").reset_index(drop=True)

                    st.session_state["master_df"] = master_df
                    st.session_state["file_columns"] = file_columns
                    st.session_state["color_map"] = color_map

                    st.success("Files uploaded and merged successfully!")
                    st.write("**Preview of Merged Data (first 15 rows):**")
                    st.dataframe(master_df.head(15))
                    st.write(f"**Final Shape:** {master_df.shape} (rows, columns)")
                    st.write("**Columns:**", list(master_df.columns))

                    if st.button("Continue → Master Document"):
                        set_page("Master Document")

                except Exception as e:
                    st.error(f"Error processing files: {e}")
    else:
        st.info("Upload 1–5 CSV/XLSX/XLS files to get started.")

def master_document_page():
    st.header("Master Document")
    st.write("Below is the merged dataset with one row per ID. All data from each file appear side‑by‑side.")

    if ("master_df" in st.session_state and 
        "file_columns" in st.session_state and 
        "color_map" in st.session_state):
        
        master_df = st.session_state["master_df"]
        file_columns = st.session_state["file_columns"]
        color_map = st.session_state["color_map"]

        st.markdown("### Legend (File → Color):")
        for fname, color in color_map.items():
            st.markdown(
                f'<div style="display:inline-block;width:20px;height:20px;background-color:{color};margin-right:10px;"></div>{fname}',
                unsafe_allow_html=True
            )

        styled_df = style_merged_df(master_df, file_columns, color_map)
        st.write(styled_df.render(), unsafe_allow_html=True)

        csv_data = master_df.to_csv(index=False)
        st.download_button(
            label="Download Merged Data as CSV",
            data=csv_data,
            file_name="merged_data.csv",
            mime="text/csv"
        )

        if st.button("Continue → Analysis"):
            set_page("Analysis")
    else:
        st.warning("No merged data found. Please go to Data Ingestion first.")

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

def about_page():
    st.header("About This Dashboard")
    st.write("""
        **Drug Blender** merges multiple CSV/Excel files horizontally by a shared 'ID' column, 
        renames non‑ID columns to include the file name, and color-codes columns based on file origin. 
        It offers a workflow with Data Ingestion, Master Document, and Analysis pages.
        
        **Features:**
        - Upload 1–5 files (CSV, XLSX, or XLS), each with key column 'ID' plus additional data.
        - Merged into one row per 'ID' (outer join) with side‑by‑side columns.
        - Downloadable merged CSV.
        - Basic numeric and missing-data analysis.
        - Navigation via sidebar and “Continue” buttons.
    """)

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

