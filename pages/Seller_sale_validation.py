from google.cloud import bigquery
import functions_framework
from query_seller_sale import queries
from google.oauth2 import service_account
import json
import requests
import streamlit as st
import pyperclip
from app import send_message_via_webhook, Webhook_urls
import pandas as pd
import io
import time

st.markdown(
        """
        <style>
        div[data-testid="stSidebarHeader"] > img, div[data-testid="collapsedControl"] > img {
            height: 6rem; /* Increased height */
            width: 20rem; /* Adjust width proportionally */
        }
        
        div[data-testid="stSidebarHeader"], div[data-testid="stSidebarHeader"] > *,
        div[data-testid="collapsedControl"], div[data-testid="collapsedControl"] > * {
            display: flex;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
st.logo("alerter_logo2.jpg")


html_title = """
<style>
    .fixed-title {
        font-size: 40px;
        color: #ffffff;
        background-image: linear-gradient(to right, #ff0000, #ffdab9);
        background-clip: text;
        -webkit-background-clip: text;
        text-fill-color: transparent;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
</style>
<h1 class="fixed-title">Seller sale validation</h1>
"""
st.markdown(html_title, unsafe_allow_html=True)
st.write("")

# HTML for button styles and progress bar
html_subject = """
<html>
<head>
<style>
    .button {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 12px;
        background: linear-gradient(to bottom, #f8f9fa, #e0e0e0);
        box-shadow: 
            0 6px 12px rgba(0, 0, 0, 0.3), 
            0 8px 16px rgba(0, 0, 0, 0.2), 
            inset 0 -2px 4px rgba(255, 255, 255, 0.6);
        text-align: center;
        position: relative;
        transform: translateY(4px);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        cursor: pointer;
        user-select: none;
    }
    .button:hover {
        box-shadow: 
            0 8px 16px rgba(0, 0, 0, 0.3), 
            0 12px 24px rgba(0, 0, 0, 0.2);
        transform: translateY(2px);
    }
    .button:active {
        box-shadow: 
            0 4px 8px rgba(0, 0, 0, 0.3), 
            0 6px 12px rgba(0, 0, 0, 0.2);
        transform: translateY(0);
    }
    .progress-bar {
        height: 20px; /* Adjusted thickness */
        width: 100%;
        background: linear-gradient(to bottom, #f8f9fa, #e0e0e0);
        border-radius: 12px;
        position: relative;
        overflow: hidden;
    }
    .progress-bar span {
        display: block;
        height: 100%;
        width: 0%;
        background: linear-gradient(to right, #ff0000, #ff4d4d); /* Red gradient */
        transition: width 0.3s ease;
    }
</style>
</head>
</html>
"""

st.markdown(html_subject, unsafe_allow_html=True)

def check_duplicates(credentials_file):
    """Check for duplicates using BigQuery with the provided credentials file."""
    results = {}
    credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_file))
    scopes = ['https://www.googleapis.com/auth/cloud-platform',
              'https://www.googleapis.com/auth/drive']
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    # Format and execute all queries
    for query_name, query_template in queries.items():
        formatted_query = query_template.format(start_date=start_date_str, end_date=end_date_str)

        # Execute the query
        try:
            query_job = client.query(formatted_query)
            df = query_job.result().to_dataframe()
            results[query_name] = df  # Store the DataFrame in the results dictionary

            # Display the DataFrame in the UI
            subheader_html = f"""
            <div style="background-image: linear-gradient(to right, #800000, #ff0000); 
                        -webkit-background-clip: text; 
                        -webkit-text-fill-color: transparent; 
                        margin: 10px 0;">
                <h4 style="margin: 0; font-size: 20px;">Results for {query_name}</h4> <!-- Change h2 to h4 -->
            </div>
            """

# Render the subheader
            st.markdown(subheader_html, unsafe_allow_html=True)
            st.dataframe(df)  # Display each DataFrame in the Streamlit app

        except Exception as e:
            st.error(f"An error occurred while querying {query_name}: {e}")

    # Check if the expected DataFrames are available for downloading
    if 'query_seller_net_data' in results and 'query_brand_accounting_entries' in results:
        df_net_data = results['query_seller_net_data']
        df_brand_entries = results['query_brand_accounting_entries']

        # Save both DataFrames to an Excel file with different sheets
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_net_data.to_excel(writer, sheet_name='ss_data', index=False)  # Changed to Net Data
            df_brand_entries.to_excel(writer, sheet_name='ss_entry', index=False)  # Changed to Brand Accounting

        excel_buffer.seek(0)

        # Create a CSV output with both DataFrames
        csv_buffer = io.StringIO()
        df_net_data.to_csv(csv_buffer, index=False, header=True)  # Write first DataFrame to CSV
        csv_buffer.write("\n")  # Add a new line to separate the sections
        df_net_data.to_csv(csv_buffer, index=False)
        df_brand_entries.to_csv(csv_buffer, index=False, header=True)  # Write second DataFrame to CSV
        csv_buffer.seek(0)

        # # Buttons to download the Excel and CSV files
        col1, col2 = st.columns(2)
        with col1:
            button_styles = """
                <style>
                div.stButton > button {
                    color: #ffffff; /* Text color */
                    font-size: 30px;
                    background-image: linear-gradient(to right, #800000, #ff0000); /* Maroon to light red gradient */
                    border: none;
                    padding: 10px 20px;
                    cursor: pointer;
                    border-radius: 15px;
                    display: inline-block;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 8px 15px rgba(0, 0, 0, 0.1); /* Box shadow */
                    transition: all 0.3s ease; /* Smooth transition on hover */
                }
                div.stButton > button:hover {
                    background-color: #00ff00; /* Hover background color */
                    color: #ff0000; /* Hover text color */
                    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2), 0 12px 20px rgba(0, 0, 0, 0.2); /* Box shadow on hover */
                }
                </style>
                """
            # Inject styles into the app
            st.markdown(button_styles, unsafe_allow_html=True)

            # Display the download button
            st.download_button(
                label="Download Excel file",
                data=excel_buffer,  # Use the base64 data URL for the file
                file_name="query_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel"  # Optionally specify a key for the button
            )
    return results




# Streamlit UI for uploading credentials
st.markdown(html_subject, unsafe_allow_html=True)

# Upload credentials file
html_subject = """
    <html>
    <head>
    <style>
        .button {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 12px;
            background: linear-gradient(to bottom, #f8f9fa, #e0e0e0);
            box-shadow: 
                0 6px 12px rgba(0, 0, 0, 0.3), 
                0 8px 16px rgba(0, 0, 0, 0.2), 
                inset 0 -2px 4px rgba(255, 255, 255, 0.6);
            text-align: center;
            position: relative;
            transform: translateY(4px);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            cursor: pointer;
            user-select: none;
        }
        .button:hover {
            box-shadow: 
                0 8px 16px rgba(0, 0, 0, 0.3), 
                0 12px 24px rgba(0, 0, 0, 0.2);
            transform: translateY(2px);
        }
        .button:active {
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.3), 
                0 6px 12px rgba(0, 0, 0, 0.2);
            transform: translateY(0);
        }
    </style>
    </head>
    <body>
        <div class="button">
            <h3 style="
                font-size: 20px;
                color: #ffffff;
                background-image: linear-gradient(to right, #800000, #ff0000, #ffdab9);
                background-clip: text;
                -webkit-background-clip: text;
                text-fill-color: transparent;
                -webkit-text-fill-color: transparent;
                margin: 0;
                text-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
            ">Upload the JSON file</h3>
        </div>
    </body>
    </html>
    """


st.markdown(html_subject, unsafe_allow_html=True)
credentials_file = st.file_uploader("", type="json")

st.write("")
col1, col2 = st.columns([0.118, 0.125])
# First column for Start Date
with col1:
    html_subject_start = """
    <html>
    <head>
    <style>
        .button {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 12px;
            background: linear-gradient(to bottom, #f8f9fa, #e0e0e0);
            box-shadow: 
                0 6px 12px rgba(0, 0, 0, 0.3), 
                0 8px 16px rgba(0, 0, 0, 0.2), 
                inset 0 -2px 4px rgba(255, 255, 255, 0.6);
            text-align: center;
            position: relative;
            transform: translateY(4px);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            cursor: pointer;
            user-select: none;
        }
        .button:hover {
            box-shadow: 
                0 8px 16px rgba(0, 0, 0, 0.3), 
                0 12px 24px rgba(0, 0, 0, 0.2);
            transform: translateY(2px);
        }
        .button:active {
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.3), 
                0 6px 12px rgba(0, 0, 0, 0.2);
            transform: translateY(0);
        }
    </style>
    </head>
    <body>
        <div class="button">
            <h3 style="
                font-size: 20px;
                color: #ffffff;
                background-image: linear-gradient(to right, #800000, #ff0000, #ffdab9);
                background-clip: text;
                -webkit-background-clip: text;
                text-fill-color: transparent;
                -webkit-text-fill-color: transparent;
                margin: 0;
                text-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
            ">Start date</h3>
        </div>
    </body>
    </html>
    """

    st.markdown(html_subject_start, unsafe_allow_html=True)
    date_input_key_start = "start_date_input" 
    start_date = st.date_input("", value=None, key=date_input_key_start)

# Second column for End Date
with col2:
    html_subject_end = """
    <html>
    <head>
    <style>
        .button {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 12px;
            background: linear-gradient(to bottom, #f8f9fa, #e0e0e0);
            box-shadow: 
                0 6px 12px rgba(0, 0, 0, 0.3), 
                0 8px 16px rgba(0, 0, 0, 0.2), 
                inset 0 -2px 4px rgba(255, 255, 255, 0.6);
            text-align: center;
            position: relative;
            transform: translateY(4px);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            cursor: pointer;
            user-select: none;
        }
        .button:hover {
            box-shadow: 
                0 8px 16px rgba(0, 0, 0, 0.3), 
                0 12px 24px rgba(0, 0, 0, 0.2);
            transform: translateY(2px);
        }
        .button:active {
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.3), 
                0 6px 12px rgba(0, 0, 0, 0.2);
            transform: translateY(0);
        }
    </style>
    </head>
    <body>
        <div class="button">
            <h3 style="
                font-size: 20px;
                color: #ffffff;
                background-image: linear-gradient(to right, #800000, #ff0000, #ffdab9);
                background-clip: text;
                -webkit-background-clip: text;
                text-fill-color: transparent;
                -webkit-text-fill-color: transparent;
                margin: 0;
                text-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
            ">End date</h3>
        </div>
    </body>
    </html>
    """

    st.markdown(html_subject_end, unsafe_allow_html=True)
    date_input_key_end = "end_date_input"  # Changed key to be unique
    end_date = st.date_input("", value=None, key=date_input_key_end)
if credentials_file is not None:
    if start_date and end_date:  # Ensure dates are selected
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Read the credentials file
        credentials_data = credentials_file.read().decode("utf-8")
        
        # Check for duplicates
        results = check_duplicates(credentials_data)
        
        # Prepare to save results in an Excel file
        if results:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                if 'query_seller_net_data' in results:
                    results['query_seller_net_data'].to_excel(writer, sheet_name='Net Data', index=False)
                if 'query_brand_accounting_entries' in results:
                    results['query_brand_accounting_entries'].to_excel(writer, sheet_name='Brand Accounting', index=False)
        else:
            st.error("No results found.")
    else:
        st.warning("Please select both the start and end dates to proceed.")
