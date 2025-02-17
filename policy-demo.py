from dotenv import load_dotenv
import streamlit as st
import os
import glob
from PIL import Image
import google.generativeai as genai
import docx

# Load environment variables
load_dotenv()

# Configure API Key
google_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=google_api_key)

# Function to extract rules from the policy document
def extract_rules_from_docx(file_path):
    doc = docx.Document(file_path)
    rules = []
    for para in doc.paragraphs:
        if para.text.strip():
            rules.append(para.text.strip())
    return "\n".join(rules)

# Extract rules from the local policy document
policy_document_path = "ExpenseNow Sample Expense Policy.docx"
policy_rules = extract_rules_from_docx(policy_document_path)

# Function to get AI response
def get_gemini_response(image, rules):
    prompt = f"""
    You are an expert in understanding invoices and company policies.
    You will receive an invoice image and a set of policy rules.
    Your task is to extract and validate the invoice details based on the rules.
    
    Policy Rules:
    {rules}
    
    Extract the following details from the invoice:
    1) Identify where the invoice is from (company name).
    2) Identify and print the total amount spent.
    3) Determine the nature of the bill (Restaurant, Travel Expense, or Accommodation).
    4) Based on the policy rules, decide whether the expense should be approved or not.
    """
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    response = model.generate_content([prompt, image[0]])
    return response.text

# Function to process uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    return None

# Function to process multiple images
def process_images(image_paths):
    results = []
    for image_path in image_paths:
        with open(image_path, "rb") as img_file:
            image_data = [{"mime_type": "image/jpeg", "data": img_file.read()}]
        response = get_gemini_response(image_data, policy_rules)
        results.append(response)  # Store response as a string
    return results

# Streamlit App
st.set_page_config(page_title="Invoice Analyzer")
st.header("Invoice Analysis with Gemini AI")

# Process all images in /sample-invoice folder
image_folder = "./sample-invoice"
image_paths = glob.glob(os.path.join(image_folder, "*.jpg")) + \
               glob.glob(os.path.join(image_folder, "*.jpeg")) + \
               glob.glob(os.path.join(image_folder, "*.png"))

if image_paths:
    st.subheader("Processing Invoices from /sample-invoice Folder")
    extracted_data = process_images(image_paths)
    
    for idx, details in enumerate(extracted_data):
        st.write(f"Invoice: {image_paths[idx].split('/')[-1]}")
        st.write(details)
        st.write("---")

# Upload additional invoices
st.subheader("Upload More Invoices for Analysis")
uploaded_files = st.file_uploader("Upload invoice images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        image_data = input_image_setup(uploaded_file)
        if image_data:
            response = get_gemini_response(image_data, policy_rules)
            st.write(f"Uploaded Invoice: {uploaded_file.name}")
            st.write(response)
            st.write("---")
