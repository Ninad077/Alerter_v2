import streamlit as st
import pandas as pd
import os
from google.oauth2.service_account import Credentials  # Correct import for service account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.cloud import bigquery
import io

# Google Drive API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

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
st.logo("alerter_logo.jpg")

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
<h1 class="fixed-title">TDS validation</h1>
"""
st.markdown(html_title, unsafe_allow_html=True)
st.write("")

# File upload UI
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
            ">Download the template file</h3>
        </div>
    </body>
    </html>
    """

st.markdown(html_subject, unsafe_allow_html=True)

st.write("")
st.write("")
template_data = pd.read_csv('template.csv')
template_df = pd.DataFrame(template_data)
st.write(template_df)

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    template_df.to_excel(writer, index=False, sheet_name='Template')
output.seek(0)

st.download_button(
    label="Download Template",
    data=output,
    file_name="template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

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
            ">Upload service a/c credentials</h3>
        </div>
    </body>
    </html>
    """

st.markdown(html_subject, unsafe_allow_html=True)

# User uploads credentials JSON file
uploaded_credentials = st.file_uploader("", type=["json"])


# Upload to BQ
def upload_to_bigquery(df, table_id):
    try:
        # Initialize BigQuery client
        client = bigquery.Client(credentials=bigquery_creds)

        # Convert the DataFrame to a list of dictionaries
        records = df.to_dict(orient='records')

        # Prepare the table schema if needed (optional)
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",  # Use WRITE_TRUNCATE to overwrite, WRITE_APPEND to append
        )

        # Load the data to BigQuery
        load_job = client.load_table_from_json(records, table_id, job_config=job_config)
        load_job.result()  # Wait for the job to complete

        st.success("Data uploaded successfully to BigQuery")

    except Exception as e:
        st.error(f"An error occurred while uploading to BigQuery: {e}")


#Upload to Gdrive
def upload_to_drive(file_path, folder_id, creds_path):
    try:
        creds = authenticate_google_drive(creds_path)  # Pass the creds_path to authenticate
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
        media = MediaFileUpload(file_path, mimetype='application/vnd.ms-excel' if file_path.endswith('.xlsx') else 'text/csv')
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        # st.success("File uploaded successfully to Google Drive")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error("Ensure the folder ID is correct and the service account has permission to access the folder.")


# Function to authenticate Google Drive API using uploaded credentials
def authenticate_google_drive(credentials_file):
    creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    return creds

# Function to authenticate BigQuery using uploaded credentials
def authenticate_bigquery(credentials_file):
    return Credentials.from_service_account_file(credentials_file)

# Handle file upload
if uploaded_credentials is not None:
    # Save uploaded credentials temporarily
    creds_path = os.path.join('temp', uploaded_credentials.name)
    os.makedirs('temp', exist_ok=True)
    with open(creds_path, 'wb') as f:
        f.write(uploaded_credentials.getbuffer())

    # Google Drive authentication
    creds = authenticate_google_drive(creds_path)
    # BigQuery authentication
    bigquery_creds = authenticate_bigquery(creds_path)

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
            ">Upload the TDS file</h3>
        </div>
    </body>
    </html>
    """

    st.markdown(html_subject, unsafe_allow_html=True)

    # Proceed with uploading files to Google Drive or BigQuery
    uploaded_file = st.file_uploader("", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        file_path = os.path.join('temp', uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Process the uploaded file
        if uploaded_file.type == 'application/vnd.ms-excel' or uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        st.dataframe(df)  # Display the file contents

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
        st.markdown(button_styles, unsafe_allow_html=True)
        if st.button("Upload to BigQuery"):
            table_id = 'fynd-db.finance_dwh.tds_seller_deductions'
            upload_to_bigquery(df, table_id)
            # Specify your Google Drive folder ID here
            folder_id = '1HOQsH67YUi3LochstFHnpapsH06MW0Te'
            upload_to_drive(file_path, folder_id, creds_path)

else:
    st.write("")
