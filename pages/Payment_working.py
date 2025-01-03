from google.cloud import bigquery
import functions_framework
from payment_queries import queries
from google.oauth2 import service_account
import json
import requests
import streamlit as st
import pyperclip
from app import send_message_via_webhook, Webhook_urls


html_title = """
<style>
    .fixed-title {
        font-size: 50px;
        color: #ffffff;
        background-image: linear-gradient(to right, #ff0000, #ffdab9);
        background-clip: text;
        -webkit-background-clip: text;
        text-fill-color: transparent;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
</style>
<h1 class="fixed-title">Payment working</h1>
"""
st.markdown(html_title, unsafe_allow_html=True)
st.write("")

# Dropdown for channels/members
webhook_url = list(Webhook_urls.keys())
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
        ">Select channels/members</h3>
    </div>
</body>
</html>
"""


st.markdown(html_subject, unsafe_allow_html=True)
selection = st.multiselect("", webhook_url)
# SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"



def check_duplicates(credentials_file):
    """Check for duplicates using BigQuery with the provided credentials file."""
    results = {}
    # credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_file))

    credentials = service_account.Credentials.from_service_account_info(
    json.loads(credentials_file),
    scopes=[
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/drive.readonly"  # Include if accessing external Drive resources
    ]
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    for i, (query_name, query) in enumerate(queries.items()):
        
        query_job = client.query(query)
        df = query_job.result().to_dataframe()
        # For debugging, write the DataFrame to the Streamlit app
        st.write(f"{query_name}:", df)

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
        if st.button(f"Copy Query", key=f"copy_query_{i}"):
            pyperclip.copy(query)
            st.success('Query copied to clipboard!')

        if not df.empty:
            duplicate_count = len(df)
            results[query_name] = duplicate_count 

    return results

# Streamlit UI
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

# Upload credentials file
credentials_file = st.file_uploader("", type="json")

if credentials_file is not None:
    # Read the credentials file
    credentials_data = credentials_file.read().decode("utf-8")
    
    # Check for duplicates
    results = check_duplicates(credentials_data)
    st.write("")
    st.write("")
    
    if results:
    # Define the HTML message with gradient text and extra spacing
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
            .spacing {
                margin: 20px 0; /* Adjust the value as needed */
            }
            .result-box {
                border: 1px solid #ddd;
                border-radius: 8px;
                background: #f9f9f9;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                padding: 10px;
                margin-bottom: 10px;
                font-size: 16px;
            }
            .result-title {
                font-weight: bold;
                color: #333;
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
                ">Duplicate Counts for Queries:</h3>
            </div>
            <div class="spacing"></div> <!-- Adds spacing between the heading and the content -->
        </body>
        </html>
        """

        # Display HTML message with spacing
        st.markdown(html_subject, unsafe_allow_html=True)

        # Prepare the plain text message with styled boxes
        message_html = ""
        for query_name, count in results.items():
            message_html += f"""
            <div class="result-box">
                <div class="result-title">{query_name}</div>
                <div>{count} records</div>
            </div>
            """

        # Display the styled message in Streamlit
        st.markdown(message_html, unsafe_allow_html=True)

        # Prepare plain text for Slack messages
        message_text = ""
        for query_name, count in results.items():
            message_text += f"*{query_name}*\n{count}records\n\n"

        if not results:
            message_text = "No duplicates found in the queries."

        # Send the message to selected channels
        for channel in selection:
            webhook_url = Webhook_urls.get(channel)
        if webhook_url:
            send_message_via_webhook(message_text, webhook_url)
        else:
            st.error(f"Webhook URL not found for channel: {channel}")