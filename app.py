import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_option_menu import option_menu
from io import BytesIO
import requests
from email.mime.application import MIMEApplication
import os
from email.mime.base import MIMEBase
from email import encoders
import base64


# Function to read files from local path
def read_file(path):
    try:
        with open(path, 'rb') as file:
            return file.read()
    except Exception as e:
        st.error(f"Failed to read file from {path}: {str(e)}")
        return None

# Function to get file content type based on file extension
def get_content_type(file_path):
    if file_path.lower().endswith('.pdf'):
        return 'application/pdf'
    elif file_path.lower().endswith('.csv'):
        return 'text/csv'
    elif file_path.lower().endswith('.xlsx'):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        return 'application/octet-stream'

# Define your email server details
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ninadmandavkar@gofynd.com'
EMAIL_HOST_PASSWORD = 'vxay jiss cctw lsdo'


st.set_page_config(page_title="Alerter",page_icon="",layout="centered")


# Display logo using st.logo
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
<h1 class="fixed-title">Slack Integration</h1>
"""
st.markdown(html_title, unsafe_allow_html=True)
st.write("")
st.write("")

    

# Encode the image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    


# Define your Slack email addresses and webhook URLs
Slack_email_addresses = {
    'Rahul Mandowara': 'aaaankma7mqecgi5ckgiutv3ga@gofynd.slack.com',
    'Abhimanyu':'aaaanm6gie6scddpk5pycnwwma@gofynd.slack.com',
    'VS': 'aaaaneedladlp3nszpmwwulkay@gofynd.slack.com',
    'ninadmandavkar': 'aaaanfcp5znlb2etchdfewwr3y@gofynd.slack.com',
    'Priyanshi Nahata': 'aaaandms5io6pfh5qawofrdplm@gofynd.slack.com',
    'kiran jadhav': 'aaaangzileg6adyfyz6y7siqme@gofynd.slack.com',
    'Bhavin Parmar': 'aaaannkdegaoe6g3vppkj26ft4@gofynd.slack.com',
    'RJ': 'aaaanf4e6nhjaryx7ba475qp2e@gofynd.slack.com',
    'Roshani Mohan': 'aaaanhjh5f2cihhkybe4k7bdre@gofynd.slack.com',
    'omkarsp': 'aaaanlsvaa7liwu3zgp42artb4@gofynd.slack.com',
    'Abhilash Sawant': 'aaaanp57acudcxnhlgmoonpsri@gofynd.slack.com',
    'Hemant Yadav': 'aaaanz2tp3lxatl4uadyc5h24e@gofynd.slack.com',
    'SandeeP Salunkhe': 'aaaanjukkjprfide3ofd6prno4@gofynd.slack.com',
    'Sid': 'aaaaneehkkyokdx5ydr5ifktui@gofynd.slack.com',
    'chetanpatole': 'aaaanptkf3sbppf5jlrlwlzmme@gofynd.slack.com',
    'Shweta Kanungo': 'aaaannsfn3qehkb4cgfqi7oqbe@gofynd.slack.com',
    'chandnichaurasia': 'aaaantvq257inlgipy6n3n4oyu@gofynd.slack.com',
    'Rasika': 'aaaanjz7aqzgmgvbq2j2erk2xi@gofynd.slack.com',
    'Bhushan Khapare': 'aaaanhompmuol3cupdtcbhyzaa@gofynd.slack.com',
    'Vaibhavi':'aaaanimf7vltovi7cs5gwknmre@gofynd.slack.com',
    'daily-alerts-for-unsubscribed-companies': 'daily-alerts-for-unsu-aaaanufptnpzgjtmknapgi45oq@gofynd.slack.com',
    'finance_team_internal': 'finance_team_internal-aaaabrz6gd5km3hjwxs7saxa4a@gofynd.slack.com',
    'valyx-fynd-poc': 'valyx-fynd-poc-aaaamwv2kpahjf3krqa752pate@gofynd.slack.com',
    'valyx_auto_invoices': 'valyx_auto_invoices-aaaanykb7mbnlhtajda4slllia@gofynd.slack.com',
    'recon-check': 'recon-check-aaaan32uofkccdehnmkymfp5qu@gofynd.slack.com'
}

gmail_addresses = {
    'Rahul Mandowara': 'rahulmandowara@gofynd.com',
    'Abhimanyu':'abhimanyumallik@gofynd.com',
    'VS': 'vikysangoi@gofynd.com',
    'ninadmandavkar': 'ninadmandavkar@gofynd.com',
    'omkarsp': 'omkarsp@gofynd.com',
    'Priyanshi Nahata': 'priyanshinahata@gofynd.com',
    'kiran jadhav': 'kiranjadhav@gofynd.com',
    'Bhavin Parmar': 'bhavinparmar@gofynd.com',
    'RJ': 'rasikajadhav@gofynd.com',
    'Roshani Mohan': 'roshanimohan@gofynd.com',
    'Abhilash Sawant': 'abhilashsawant@gofynd.com',
    'Hemant Yadav': 'hemantyadav@gofynd.com',
    'SandeeP Salunkhe': 'sandeepsalunkhe@gofynd.com',
    'Sid': 'siddheshmayekar@gofynd.com',
    'chetanpatole': 'chetanpatole@gofynd.com',
    'Shweta Kanungo': 'shwetakanungo@gofynd.com',
    'chandnichaurasia': 'chandnichaurasia@gofynd.com',
    'Rasika': 'rasikasalunkhe@gofynd.com',
    'Bhushan Khapare': 'bhushankhapare@gofynd.com',
    'Vaibhavi': 'vaibhavidambe@gofynd.com',
    'daily-alerts-for-unsubscribed-companies': 'daily-alerts-for-unsu-aaaanufptnpzgjtmknapgi45oq@gofynd.slack.com',
    'finance_team_internal': 'finance_team_internal-aaaabrz6gd5km3hjwxs7saxa4a@gofynd.slack.com',
    'valyx-fynd-poc': 'valyx-fynd-poc-aaaamwv2kpahjf3krqa752pate@gofynd.slack.com',
    'valyx_auto_invoices': 'valyx_auto_invoices-aaaanykb7mbnlhtajda4slllia@gofynd.slack.com',
    'recon-check': 'recon-check-aaaan32uofkccdehnmkymfp5qu@gofynd.slack.com'
}

Webhook_urls = {
    'Rahul Mandowara': 'https://hooks.slack.com/services/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',
    'Abhimanyu':'https://hooks.slack.com/services/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',
    'VS': 'https://hooks.slack.com/services/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',
    'ninadmandavkar': 'https://hooks.slack.com/services/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',
    'Priyanshi Nahata': 'https://hooks.slack.com/services/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',
    'kiran jadhav': 'https://hooks.slack.com/services/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',
    'Bhavin Parmar': 'https://hooks.slack.com/services/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',
    'RJ': 'https://hooks.slack.com/services/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',
    'Roshani Mohan': 'https://hooks.slack.com/services/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',
    'omkarsp': 'https://hooks.slack.com/services/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',
    'Abhilash Sawant': 'https://hooks.slack.com/services/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',
    'Hemant Yadav': 'https://hooks.slack.com/services/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',
    'SandeeP Salunkhe': 'https://hooks.slack.com/services/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',
    'Sid': 'https://hooks.slack.com/services/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',
    'chetanpatole': 'https://hooks.slack.com/services/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',
    'Shweta Kanungo': 'https://hooks.slack.com/services/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',
    'chandnichaurasia': 'https://hooks.slack.com/services/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',
    'Rasika': 'https://hooks.slack.com/services/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',
    'Bhushan Khapare': 'https://hooks.slack.com/services/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',
    'Vaibhavi': 'https://hooks.slack.com/services/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',
    'daily-alerts-for-unsubscribed-companies': 'https://hooks.slack.com/services/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',
    'finance_team_internal': 'https://hooks.slack.com/services/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',
    'valyx-fynd-poc': 'https://hooks.slack.com/services/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',
    'valyx_auto_invoices': 'https://hooks.slack.com/services/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',
    'recon-check': 'https://hooks.slack.com/services/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'
}




# Define your email server details
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ninadmandavkar@gofynd.com'
EMAIL_HOST_PASSWORD = 'etdv kmvs qbsi zose'

def send_message_via_email(message, email_address, files, subject=None, body=None):
    try:
        # Set up the server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = email_address
        msg['Subject'] = subject if subject else "🚨 Alerter"

        # Attach the message body
        msg.attach(MIMEText(body if body else message, 'plain'))

        # Attach each file if provided
        if files:
            for uploaded_file in files:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(uploaded_file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={uploaded_file.name}')
                msg.attach(part)

        # Send the email
        server.sendmail(EMAIL_HOST_USER, email_address, msg.as_string())
        server.quit()
        return True, "Message sent successfully"
    except Exception as e:
        return False, str(e)

def send_message_via_webhook(message, webhook_url):
    try:
        payload = {
            "text": message
        }
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True, "Message sent successfully"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def main():

    # # Path to your image
    # image_path = "Designer (1).png"
    # base64_image = get_base64_image(image_path)

    # Define the CSS for setting the background image
    # background_image_css = f"""
    # <style>
    #     .stApp {{
    #         background-image: url(data:image/png;base64,{base64_image});
    #         background-size: 100%;
    #         background-repeat: no-repeat;
    #         background-attachment: fixed;
    #         background-position: center;
    #         height: 100vh; /* Make sure the background covers the full viewport height */
            
    #     }}
    # </style>
    # """

    # # Apply the CSS to the Streamlit app
    # st.markdown(background_image_css, unsafe_allow_html=True)


    
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
        ">Write a Slack message</h3>
    </div>
</body>
</html>
"""



    st.markdown(html_subject, unsafe_allow_html=True)
    message = st.text_area("", "")
    

    # File uploader widget with a unique key
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
            ">Upload documents</h3>
        </div>
    </body>
    </html>
    """


    st.markdown(html_subject, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf", "docx", "png", "jpeg", "xlsx", "csv", "json"], key="file_uploader", accept_multiple_files= True)

    # Dropdown for channels/members
    options = list(Slack_email_addresses.keys())
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
    selection = st.multiselect("", options)

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
            ">Enter the subject(optional)</h3>
        </div>
    </body>
    </html>
    """


    st.markdown(html_subject, unsafe_allow_html=True)
    subject = st.text_input("", "",key ="subject_text_input")



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
            ">Enter the body (optional)</h3>
        </div>
    </body>
    </html>
    """


    st.markdown(html_subject, unsafe_allow_html=True)
    body = st.text_area("", "", key="body_text_area")
    

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

    col1, col2 = st.columns([0.125, 0.5])
    with col1:
        if st.button("Send to Slack"):
            if not message and not uploaded_file:
                st.error("Please enter a message or upload a document before sending.")
                return

            if not selection:
                st.error("Please select at least one channel or member")
                return 

            for item in selection:
                if uploaded_file:
                    # Send the document via email
                    email_address = Slack_email_addresses.get(item)
                    if email_address:
                        success, response_message = send_message_via_email(message, email_address, uploaded_file, subject, body)
                        # if success:
                        #     st.success(f"Document sent to {item} via email.")
                        # else:
                        #     st.error(f"Failed to send document to {item}: {response_message}")
                    else:
                        st.error(f"No email address found for {item}.")
                elif message:
                    # Send the message via Slack webhook
                    webhook_url = Webhook_urls.get(item)
                    if webhook_url:
                        success, response_message = send_message_via_webhook(message, webhook_url)
                        # if success:
                        #     st.success(f"Message sent to {item} via Slack webhook.")
                        # else:
                        #     st.error(f"Failed to send message to {item}: {response_message}")
                    else:
                        st.error(f"No webhook URL found for {item}.")

    with col2:
        if st.button("Send to Gmail"):
            if not message and not uploaded_file:
                st.error("Please enter a message or upload a document before sending.")
                return

            if not selection:
                st.error("Please select at least one channel or member")
                return

            for item in selection:
                email_address = gmail_addresses.get(item)
                if email_address:
                    success, response_message = send_message_via_email(message, email_address, uploaded_file, subject, body)
                    # if success:
                    #     st.success(f"Message sent to {item} via Gmail.")
                    # else:
                    #     st.error(f"Failed to send message to {item}: {response_message}")
                else:
                    st.error(f"No Gmail address found for {item}.")

if __name__ == "__main__":
    main()


