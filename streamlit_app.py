import streamlit as st
import pandas as pd

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

# --- Vertical Navigation on the Left ---
# Data Ingestion is set as the first/landing page by placing it at index 0
app_mode = st.sidebar.radio("Go to", ["Data Ingestion", "Data Summary", "About"])

# --- Data Ingestion Page (Landing Page) ---
if app_mode == "Data Ingestion":
    st.title("Pharmaceutical Data Dashboard")
    st.subheader("Data Ingestion")
    st.write("Upload between 1 and 5 CSV files. Each file should share a common key (e.g., `product_id`) so they can be merged together.")
    
    # Container for styled file uploader
    with st.container():
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload CSV Files (1–5)",
            type=["csv"],
            accept_multiple_files=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        # Check file count
        if len(uploaded_files) > 5:
            st.warning("Please upload a maximum of 5 CSV files.")
        else:
            try:
                # Read each uploaded CSV into a DataFrame
                df_list = [pd.read_csv(file) for file in uploaded_files]
                
                # Merge dataframes sequentially on the common key 'product_id'
                merged_df = df_list[0]
                for df in df_list[1:]:
                    merged_df = pd.merge(merged_df, df, on='product_id', how='outer')
                
                # Store merged data for later use
                st.session_state['merged_df'] = merged_df
                
                st.success("Files uploaded and merged successfully!")
                st.dataframe(merged_df.head())
            except Exception as e:
                st.error(f"An error occurred while processing the files: {e}")
    else:
        st.info("Please upload at least one CSV file to get started.")

# --- Data Summary Page ---
elif app_mode == "Data Summary":
    st.header("Data Summary")
    if 'merged_df' in st.session_state:
        merged_df = st.session_state['merged_df']
        st.dataframe(merged_df)
        
        # If there's a numeric column (e.g., 'value'), display its sum
        if 'value' in merged_df.columns:
            total_value = merged_df['value'].sum()
            st.metric("Total Value", f"{total_value:,}")
        else:
            st.info("Column 'value' not found in the merged dataset.")
        
        st.subheader("Summary Statistics")
        st.write(merged_df.describe())
    else:
        st.warning("No data available. Please upload files in the Data Ingestion section.")

# --- About Page ---
elif app_mode == "About":
    st.header("About This Dashboard")
    st.write("""
        This dashboard integrates multiple CSV data sources into one unified view—a single source of truth—for your pharmaceutical product.
        Built with Python and Streamlit, it allows you to upload up to 5 files, merge them based on a common key (e.g., `product_id`),
        and view comprehensive summaries and metrics.
    """)
    st.write("Developed using Python and Streamlit.")
