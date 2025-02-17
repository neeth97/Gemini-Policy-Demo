from dotenv import load_dotenv
import streamlit as st
import os
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

# Streamlit App
st.set_page_config(page_title="Invoice Analyzer")
st.header("Invoice Analysis with Gemini AI")

uploaded_file = st.file_uploader("Upload an invoice image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Invoice.", width=300)
    
    image_data = input_image_setup(uploaded_file)
    if image_data:
        response = get_gemini_response(image_data, policy_rules)
        st.subheader("Extracted Invoice Details:")
        st.write(response)
