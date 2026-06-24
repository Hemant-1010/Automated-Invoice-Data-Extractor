import pdfplumber   # reads PDF files and extracts text from them
import os           # lets us read environment variables 
import json         # converts JSON strings into Python dictionaries and back
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Build the path to the .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

try:
    # Open the file and extract the key in one clean sweep
    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
        api_key = next(line.split("=")[1].strip() for line in f if "GEMINI_API_KEY=" in line)
    
    client = genai.Client(api_key=api_key)
    print("✅ API Key successfully loaded!")

except (FileNotFoundError, StopIteration):
    raise ValueError(f"CRITICAL ERROR: Missing .env file or GEMINI_API_KEY not found at: {env_path}")



#  FUNCTION TO READ AND EXTRACT TEXT FROM PDF

def extract_text_from_pdf(pdf_path):
    raw_text = ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + "\n"
    except FileNotFoundError:
        print(f"ERROR: File not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"ERROR: Could not read PDF - {str(e)}")
        return None
    
    return raw_text

# FUNCTION TO CLEAN AND PREPROCESS TEXT

def clean_text(raw_text):
    lines = [line.strip() for line in raw_text.split('\n')]
    cleaned = '\n'.join([line for line in lines if line])
    return cleaned


# ENGINEER THE EXTRACTION PROMPT

def get_extraction_prompt():
    prompt = """You are an expert invoice data extractor. Your job is to read invoice text and extract all key fields into a JSON object.

IMPORTANT RULES:
1. Extract ONLY the 13 fields listed below
2. If a field is NOT present in the invoice, return null (not 'N/A', not empty string, not false)
3. Format dates as DD-MM-YYYY (example: 03-06-2025)
4. Keep amounts exactly as they appear (with currency symbols if present)
5. line_items must be a list of objects with 'item' and 'amount' keys
6. Do NOT guess or make up values
7. Return ONLY valid JSON, no markdown formatting, no code fences, no explanations

Extract these 13 fields:
{
  "invoice_number": "unique invoice ID or reference number",
  "invoice_date": "date issued (DD-MM-YYYY format)",
  "due_date": "payment deadline (DD-MM-YYYY format or description)",
  "billed_by": "company/person issuing the invoice",
  "billed_to": "client/recipient being billed",
  "line_items": "[{item: description, amount: value}, ...]",
  "subtotal": "total before discounts and taxes",
  "discount": "discount amount if any",
  "tax_or_gst": "tax/GST amount if applicable",
  "total_amount": "final payable amount",
  "currency": "currency code (INR, USD, etc.)",
  "payment_method": "how to pay (NEFT, UPI, credit card, etc.)",
  "notes": "additional remarks or instructions"
}

Return ONLY the JSON object, nothing else."""
    
    return prompt


# FUNCTION TO CALL GEMINI API AND EXTRACT DATA

def extract_invoice_data(cleaned_text):
    full_prompt = f"{get_extraction_prompt()}\n\nExtract all invoice data from this text:\n\n{cleaned_text}"
    
    try:
        # Call the Google GenAI SDK
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0,  
                response_mime_type="application/json", 
            )
        )
        
        response_text = response.text
        extracted_data = json.loads(response_text)
        return extracted_data
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: API call failed - {error_msg}")   # If anything goes wrong (503, 429, etc.), print the exact error and stop instantly
        return None
    

# FUNCTION TO DISPLAY EXTRACTED DATA CLEANLY

def display_extracted_data(extracted_data, invoice_path):
    
    if not extracted_data:
        print("No data to display.")
        return
    
    print("\n" + "="*70)
    print(f"EXTRACTED DATA FROM: {os.path.basename(invoice_path)}")
    print("="*70)
    
    print(f"\nInvoice Number:     {extracted_data.get('invoice_number')}")
    print(f"Invoice Date:       {extracted_data.get('invoice_date')}")
    print(f"Due Date:           {extracted_data.get('due_date')}")
    print(f"Billed By:          {extracted_data.get('billed_by')}")
    print(f"Billed To:          {extracted_data.get('billed_to')}")
    
    print(f"\nLine Items:")
    line_items = extracted_data.get('line_items', [])
    if line_items and isinstance(line_items, list):
        for idx, item in enumerate(line_items, 1):
            item_desc = item.get('item', 'N/A') if isinstance(item, dict) else item
            item_amount = item.get('amount', 'N/A') if isinstance(item, dict) else 'N/A'
            print(f"  {idx}. {item_desc}: {item_amount}")
    else:
        print(f"  {line_items}")
    
    print(f"\nSubtotal:           {extracted_data.get('subtotal')}")
    print(f"Discount:           {extracted_data.get('discount')}")
    print(f"Tax/GST:            {extracted_data.get('tax_or_gst')}")
    print(f"Total Amount:       {extracted_data.get('total_amount')}")
    
    print(f"\nCurrency:           {extracted_data.get('currency')}")
    print(f"Payment Method:     {extracted_data.get('payment_method')}")
    print(f"Notes:              {extracted_data.get('notes')}")
    
    print("\n" + "="*70)

# MAIN PIPELINE FUNCTION

def process_invoice(pdf_path, output_json_path=None):
    
    print(f"\n Processing invoice: {pdf_path}")
    
    print("Loading PDF and extracting text...")
    raw_text = extract_text_from_pdf(pdf_path)
    
    if not raw_text:
        print("Failed to extract text from PDF")
        return None
    
    print("Cleaning and preprocessing text...")
    cleaned_text = clean_text(raw_text)
    
    print("Calling Gemini API for data extraction...")
    extracted_data = extract_invoice_data(cleaned_text)
    
    if not extracted_data:
        print("Failed to extract data")
        return None
    
    print("Extraction successful!")
    display_extracted_data(extracted_data, pdf_path)
    
    if output_json_path:
        try:
            os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            print(f"\n JSON output saved to: {output_json_path}")
        except Exception as e:
            print(f"\nCould not save JSON: {str(e)}")
    
    return extracted_data

# MAIN EXECUTION

if __name__ == "__main__":
    
    invoices =[ 
        {
            "pdf_path": "1.pdf",
            "output_json": "outputs/output_invoice_1.json"
        },

        {
            "pdf_path": "2.pdf",
            "output_json": "outputs/output_invoice_2.json"
        },

        {
            "pdf_path": "3.pdf",
            "output_json": "outputs/output_invoice_3.json"
        },
    ]
    
    print("\n Starting Automated Invoice Data Extraction Pipeline\n")
    
    for invoice in invoices:
        if os.path.exists(invoice["pdf_path"]):
            process_invoice(invoice["pdf_path"], invoice["output_json"])
        else:
            print(f"Invoice file not found: {invoice['pdf_path']}")
    
    print("\nPipeline complete!")