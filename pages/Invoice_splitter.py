import streamlit as st
import pandas as pd
import os
from io import BytesIO
from zipfile import ZipFile


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
<h1 class="fixed-title">Invoice splitter</h1>
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
            ">Upload a CSV file</h3>
        </div>
    </body>
    </html>
    """

st.markdown(html_subject, unsafe_allow_html=True)

# Step 1: Upload CSV file
uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file is not None:
    # Step 2: Read the CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)

    if 'Invoice_No' not in df.columns:
        st.error("The uploaded CSV does not contain the 'Invoice_No' column.")
    else:
        # Step 3: Split the DataFrame based on unique Invoice_No values
        invoice_groups = df.groupby('Invoice_No')
        
        # Step 4: Generate CSV files for each Invoice_No and add them to a ZIP archive
        zip_buffer_csv = BytesIO()
        with ZipFile(zip_buffer_csv, "a") as zip_file:
            for invoice_no, group in invoice_groups:
                csv_buffer = BytesIO()
                group.to_csv(csv_buffer, index=False)
                zip_file.writestr(f"{invoice_no}.csv", csv_buffer.getvalue())

        zip_buffer_csv.seek(0)  # Move to the beginning of the buffer
        
        # Step 5: Generate Excel files for each Invoice_No and add them to a ZIP archive
        zip_buffer_xlsx = BytesIO()
        with ZipFile(zip_buffer_xlsx, "a") as zip_file:
            for invoice_no, group in invoice_groups:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    group.to_excel(writer, index=False, sheet_name=str(invoice_no))
                excel_buffer.seek(0)
                zip_file.writestr(f"{invoice_no}.xlsx", excel_buffer.getvalue())

        zip_buffer_xlsx.seek(0)  # Move to the beginning of the buffer

        # Step 6: Provide download buttons for both ZIP files (CSV and Excel)
        button_styles = """
                <style>
                div.stDownloadButton > button {
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
                div.stDownloadButton > button:hover {
                    background-color: #00ff00; /* Hover background color */
                    color: #ff0000; /* Hover text color */
                    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2), 0 12px 20px rgba(0, 0, 0, 0.2); /* Box shadow on hover */
                }
                </style>
            """
        st.markdown(button_styles, unsafe_allow_html=True)
        # Download buttons
        st.download_button(
            label="Download Invoice ZIP (CSV)",
            data=zip_buffer_csv,
            file_name="invoices_csv.zip",
            mime="application/zip"
        )

        st.download_button(
            label="Download Invoice ZIP (Excel)",
            data=zip_buffer_xlsx,
            file_name="invoices_xlsx.zip",
            mime="application/zip"
        )
