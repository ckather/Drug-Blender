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

# --- Navigation using tabs ---
tabs = st.tabs(["Home", "Data Ingestion", "Data Summary", "About"])

# --- Home Tab ---
with tabs[0]:
    st.title("Pharmaceutical Data Dashboard")
    st.subheader("Welcome to the Unified Data View")
    st.write("This dashboard provides a single source of truth by integrating multiple data sources for your pharmaceutical product.")
    st.image("https://via.placeholder.com/600x200.png?text=Pharmaceutical+Dashboard", use_column_width=True)

# --- Data Ingestion Tab ---
with tabs[1]:
    st.header("Data Ingestion")
    st.write("Upload at least 5 CSV files. Each file should share a common key (e.g., `product_id`) so they can be merged together.")
    
    # Container for styled file uploader
    with st.container():
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        if len(uploaded_files) < 5:
            st.warning("Please upload at least 5 CSV files.")
        else:
            try:
                # Read each uploaded CSV into a DataFrame
                df_list = [pd.read_csv(file) for file in uploaded_files]
                # Merge dataframes sequentially on the common key 'product_id'
                merged_df = df_list[0]
                for df in df_list[1:]:
                    merged_df = pd.merge(merged_df, df, on='product_id', how='outer')
                st.session_state['merged_df'] = merged_df  # Save for later use
                st.success("Data loaded and merged successfully!")
                st.dataframe(merged_df.head())
            except Exception as e:
                st.error(f"Error processing data: {e}")
    else:
        st.info("Please upload your CSV files to begin.")

# --- Data Summary Tab ---
with tabs[2]:
    st.header("Data Summary")
    if 'merged_df' in st.session_state:
        merged_df = st.session_state['merged_df']
        st.dataframe(merged_df)
        
        # If there's a numeric column (e.g., 'value'), display its sum
        if 'value' in merged_df.columns:
            total_value = merged_df['value'].sum()
            st.metric("Total Value", f"{total_value:,}")
        else:
            st.info("Column 'value' not found. Ensure your data includes the correct numeric field.")
        
        st.subheader("Summary Statistics")
        st.write(merged_df.describe())
    else:
        st.warning("No data found. Please upload data in the 'Data Ingestion' tab.")

# --- About Tab ---
with tabs[3]:
    st.header("About This Dashboard")
    st.write("""
        This dashboard is designed to integrate multiple data sources into a single, unified view—a 'source of truth'—for a pharmaceutical product.
        Using Python and Streamlit, it allows you to upload at least 5 CSV files, merge them on a common key (e.g., `product_id`), and visualize the aggregated data.
        
        **Key Features:**
        - **Data Ingestion:** Upload multiple CSV files.
        - **Data Integration:** Merge datasets based on a common identifier.
        - **Data Visualization:** Explore summaries and metrics interactively.
        
        Developed with compliance and user-friendliness in mind.
    """)
    st.write("Developed using Python and Streamlit.")
