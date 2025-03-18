import streamlit as st
import pandas as pd

# --- Custom CSS for beautification ---
st.markdown("""
    <style>
    /* General background and typography */
    .main { background-color: #f5f5f5; }
    h1, h2, h3 { color: #003366; }
    /* Sidebar styling */
    .css-1d391kg { background-color: #003366; color: white; }
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

# --- App Title and Navigation ---
st.title("Pharmaceutical Data Dashboard")
st.subheader("A unified view for your data sources")

# Sidebar Navigation for multipage functionality
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose the page", 
                                ["Home", "Data Ingestion", "Data Summary", "About"])

# --- Home Page ---
if app_mode == "Home":
    st.write("Welcome to the Pharmaceutical Data Dashboard!")
    st.write("This tool lets you upload multiple CSV files, merge them on common keys (e.g., product_id), and summarize your data all in one place.")
    st.image("https://via.placeholder.com/600x200.png?text=Pharmaceutical+Dashboard", use_column_width=True)

# --- Data Ingestion Page ---
elif app_mode == "Data Ingestion":
    st.header("Data Ingestion")
    st.write("Upload your CSV data sources below. For demonstration, we expect a common key like `product_id` to merge the datasets.")
    
    # Use a container with custom styling
    with st.container():
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_file1 = st.file_uploader("Upload Data Source 1 (CSV)", type=["csv"])
        uploaded_file2 = st.file_uploader("Upload Data Source 2 (CSV)", type=["csv"])
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file1 is not None and uploaded_file2 is not None:
        try:
            df1 = pd.read_csv(uploaded_file1)
            df2 = pd.read_csv(uploaded_file2)
            # Merge the two dataframes on a common key, e.g., 'product_id'
            merged_df = pd.merge(df1, df2, on='product_id', how='outer')
            st.session_state['merged_df'] = merged_df  # store merged data for later use
            st.success("Data loaded and merged successfully!")
            st.dataframe(merged_df.head())
        except Exception as e:
            st.error(f"Error processing data: {e}")
    else:
        st.info("Please upload both data sources to proceed.")

# --- Data Summary Page ---
elif app_mode == "Data Summary":
    st.header("Data Summary")
    if 'merged_df' in st.session_state:
        merged_df = st.session_state['merged_df']
        st.dataframe(merged_df)
        
        # Example: Sum total of a numeric column, e.g., 'value'
        if 'value' in merged_df.columns:
            total_value = merged_df['value'].sum()
            st.metric("Total Value", f"{total_value:,}")
        else:
            st.info("Column 'value' not found. Please ensure your data has the correct numeric field.")
        
        st.subheader("Summary Statistics")
        st.write(merged_df.describe())
    else:
        st.warning("No data found. Please upload data in the 'Data Ingestion' section.")

# --- About Page ---
elif app_mode == "About":
    st.header("About This Dashboard")
    st.write("""
        This dashboard is designed to integrate multiple data sources into a single, unified view—a 'source of truth'—for a pharmaceutical product.
        Built with Streamlit, it allows you to upload CSV files, merge them based on a common key (e.g., product_id), and display interactive summaries and visualizations.
        
        **Key Features:**
        - **Data Ingestion:** Easily upload multiple data sources.
        - **Data Integration:** Merge datasets on common identifiers.
        - **Data Visualization:** Summarize and analyze data interactively.
        
        Developed with compliance and ease-of-use in mind, this tool can be further customized to meet industry-specific requirements.
    """)
    st.write("Developed using Python and Streamlit.")
