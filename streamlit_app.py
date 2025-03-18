import streamlit as st
import pandas as pd
import os

# --- Helper function to read a file based on extension ---
def load_file(uploaded_file):
    """
    Reads an uploaded file into a Pandas DataFrame based on its extension.
    Supported extensions: .csv, .xlsx, .xls
    """
    # Extract file extension
    _, extension = os.path.splitext(uploaded_file.name.lower())
    
    if extension == ".csv":
        return pd.read_csv(uploaded_file)
    elif extension in [".xlsx", ".xls"]:
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

# --- Helper function to color rows based on file source ---
def color_rows_by_source(row, color_map):
    """Return a list of CSS styles for each cell in a row based on the 'source_file' column."""
    file_name = row["source_file"]
    color = color_map.get(file_name, "#FFFFFF")  # default to white if not found
    return [f"background-color: {color}"] * len(row)

# --- Custom CSS for beautification ---
st.markdown("""
    <style>
    /* General background and typography */
    .main { background-color: #f5f5f5; }
    h1, h2, h3 { color: #003366; }
    /* Card-like styling for file upload area */
    .upload-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Navigation ---
app_mode = st.sidebar.radio("Go to", ["Data Ingestion", "Master Document", "About"])

# ---------------------------
# 1) DATA INGESTION PAGE
# ---------------------------
if app_mode == "Data Ingestion":
    st.title("Pharmaceutical Data Dashboard")
    st.subheader("Data Ingestion")
    st.write("Upload between 1 and 5 files (CSV or Excel). Each file will be appended into a **Master Document** with color-coded rows.")

    # File uploader
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
                
                # We’ll define a color palette for up to 5 files
                color_palette = ["#FFCFCF", "#CFFFCF", "#CFCFFF", "#FFFACF", "#FFCFFF"]
                
                # Build a color map (file_name -> color)
                color_map = {}
                
                for i, file in enumerate(uploaded_files):
                    # Load each file
                    df = load_file(file)
                    
                    # Add a column to track the source file
                    df["source_file"] = file.name
                    
                    # Assign a color to this file (by index)
                    color_map[file.name] = color_palette[i]
                    
                    df_list.append(df)
                
                # Concatenate all dataframes (a "stack" of rows)
                master_df = pd.concat(df_list, ignore_index=True)
                
                # Store both the master_df and color_map for use in the Master Document tab
                st.session_state["master_df"] = master_df
                st.session_state["color_map"] = color_map
                
                st.success("Files uploaded and combined successfully!")
                st.write("**Preview of Combined Data:**")
                st.dataframe(master_df.head())
            
            except Exception as e:
                st.error(f"An error occurred while processing the files: {e}")
    else:
        st.info("Please upload at least one file to get started.")

# ---------------------------
# 2) MASTER DOCUMENT PAGE
# ---------------------------
elif app_mode == "Master Document":
    st.header("Master Document")
    st.write("Below is the combined dataset with each file’s rows highlighted in a unique color.")
    
    if "master_df" in st.session_state and "color_map" in st.session_state:
        master_df = st.session_state["master_df"]
        color_map = st.session_state["color_map"]
        
        # Create a styled DataFrame that highlights rows by source file
        styled_df = master_df.style.apply(
            lambda row: color_rows_by_source(row, color_map), 
            axis=1
        )
        
        # Display the styled DataFrame. Note that st.dataframe() won't preserve styling,
        # so we use st.write() to render the HTML.
        st.write(styled_df)
        
        # Optional: Show some summary stats
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
        This dashboard integrates multiple CSV or Excel files into one **Master Document**, color-coding rows based on the file of origin.
        
        **Key Features**  
        - Upload between 1 and 5 CSV/Excel files  
        - Combine them into a single table with each file’s rows highlighted  
        - Preview and analyze the merged data in real-time  

        Built with Python and Streamlit.
    """)
