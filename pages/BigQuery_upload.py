import os
import pandas as pd
import streamlit as st
from google.cloud import bigquery

def preprocess_csv(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Define columns to be converted
    date_columns = ['Order_Date', 'State_Date', 'Entry_Month']

    if 'bag_id_cn' in df.columns:
        df['bag_id_cn'] = df['bag_id_cn'].replace({'\..*': ''}, regex=True).astype('Int64')

    # Convert specified columns from DD/MM/YY to 'YYYY-MM-DD 00:00:00 UTC'
    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], format='%d/%m/%y', errors='coerce').dt.strftime('%Y-%m-%d 00:00:00 UTC')

    # Save the preprocessed CSV
    preprocessed_file_path = 'preprocessed_' + os.path.basename(file_path)
    df.to_csv(preprocessed_file_path, index=False)
    
    return preprocessed_file_path

def upload_to_bigquery(credentials_path, csv_file_path, project_name, table_id):
    try:
        # Set up the BigQuery client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        client = bigquery.Client(project=project_name)

        # Retrieve the existing table schema
        table = client.get_table(table_id)
        schema = table.schema
        
        # Prepare the BigQuery job configuration with the existing schema
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,  # Assuming the first row is the header
            schema=schema,        # Use the existing schema from BigQuery
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Append to the table
        )
        
        # Load the preprocessed CSV data into BigQuery
        with open(csv_file_path, "rb") as file:
            load_job = client.load_table_from_file(
                file,
                table_id,
                job_config=job_config
            )
        
        # Wait for the load job to complete
        load_job.result()
        
        # Check the result
        destination_table = client.get_table(table_id)
        st.success(f"Loaded {destination_table.num_rows} rows into {table_id}.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

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
<h1 class="fixed-title">BigQuery upload</h1>
"""
st.markdown(html_title, unsafe_allow_html=True)
st.write("")
st.write("")



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
            ">Enter project name</h3>
        </div>
    </body>
    </html>
    """

st.markdown(html_subject, unsafe_allow_html=True)

# Input fields for Project Name and Table ID
project_name = st.text_input("",key ="project_name")


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
            ">Enter table id</h3>
        </div>
    </body>
    </html>
    """

st.markdown(html_subject, unsafe_allow_html=True)
table_id = st.text_input("", key= "table_id_name")

# File uploader for credentials.json

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
            ">Upload credentials file</h3>
        </div>
    </body>
    </html>
    """

st.markdown(html_subject, unsafe_allow_html=True)
credentials_file = st.file_uploader("", type=["json"])

# File uploader for the CSV file

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
            ">Upload the CSV file</h3>
        </div>
    </body>
    </html>
    """

st.markdown(html_subject, unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv", "xlsx"])

# Submit button
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
if st.button("Submit"):
    if uploaded_file is not None and credentials_file is not None and project_name and table_id:
        # Save the uploaded files to the current directory
        credentials_path = "./credentials.json"
        with open(credentials_path, "wb") as f:
            f.write(credentials_file.getbuffer())
        
        csv_file_path = f"./{uploaded_file.name}"
        with open(csv_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Preprocess the CSV file (convert date formats)
        preprocessed_file_path = preprocess_csv(csv_file_path)
        
        # Upload the preprocessed CSV file to BigQuery
        upload_to_bigquery(credentials_path, preprocessed_file_path, project_name, table_id)
    else:
        st.error("Please fill out all fields, including the credentials file and CSV file.")

