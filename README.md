# Automated-Invoice-Data-Extractor

##  Project Overview

This project solves a real-world problem: manually processing invoices is slow, error-prone, and unscalable. This pipeline automates the extraction of key invoice fields from PDFs into structured JSON format.

## What It Does

1. Reads any invoice PDF file
2. Extracts raw text using 'pdfplumber'
3. Cleans the text for LLM consumption
4. Engineers a precise extraction prompt
5. Calls Gemini's API (gemini-3.1-flash-lite) to extract structured data
6. Parses the JSON response
7. Outputs clean, structured invoice data

Extracted Fields (13 Total)

The pipeline extracts all of the following fields from each invoice:

| Field | Description | Example |
|-------|-------------|---------|
| `invoice_number` | Unique invoice ID | INV-2025-0047 |
| `invoice_date` | Issue date (DD-MM-YYYY) | 03-06-2025 |
| `due_date` | Payment deadline | 17-06-2025 |
| `billed_by` | Issuing company/person | Velora Software Agency |
| `billed_to` | Client/recipient | Mr. Alok Agrawal |
| `line_items` | Services/products with amounts | [{"item": "...", "amount": "..."}] |
| `subtotal` | Total before discounts/taxes | ₹1,30,000 |
| `discount` | Discount amount (null if none) | ₹15,000 |
| `tax_or_gst` | Tax amount (null if N/A) | ₹5,000 |
| `total_amount` | Final payable amount | ₹1,15,000 |
| `currency` | Currency code | INR |
| `payment_method` | Payment instruction | NEFT / UPI |
| `notes` | Additional remarks | Payment due on receipt |

---

## Quick Start

 1. Prerequisites

- **Python 3.8+** installed
- **Gemini API Key** (create account at https://aistudio.google.com)

2. Installation

# Clone the repository
- git clone https://github.com/Hemant-1010/Automated-Invoice-Data-Extractor.git 
- cd Automated-Invoice-Data-Extractor

# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

| Package | Version | Purpose |
|---------|---------|---------|
| pdfplumber | 0.10.3+ | PDF text extraction |
| Genai | 1.3.0+ | Gemini API client |
| python-dotenv | 1.0.0+ | Load .env environment variables | 

# Or manually
pip install pdfplumber openai python-dotenv

### 3. Setup API Key

Create a '.env' file in the root directory:

echo "Gemini_API_KEY=your-api-key-here" > .env

IMPORTANT: Never commit '.env' to GitHub.

4. Prepare Your Invoices

Place your invoice PDF files in the 'invoices/' folder:

invoices/
  ├── invoice_1.pdf
  ├── invoice_2.pdf
  └── invoice_3.pdf


### 5. Run the Pipeline

python invoice_extractor.py


### 6. Check Results

Extracted JSON files will be saved to `outputs/`:

outputs/
  ├── output_invoice_1.json
  ├── output_invoice_2.json
  └── output_invoice_3.json

## Repository Structure

invoice-extractor-genai/
├── invoice_extractor.py        # Main pipeline script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Prevents .env from being committed
├── invoices/                   # Place your invoice PDFs here
│   ├── invoice_1.pdf
│   ├── invoice_2.pdf
│   └── invoice_3.pdf
└── outputs/                    # Extracted JSON results (auto-created)
    ├── output_invoice_1.json
    ├── output_invoice_2.json
    └── output_invoice_3.json

---

## How the Pipeline Works

### Step-by-Step Flow


INPUT (PDF)
    ↓
[1] Load PDF with pdfplumber
    ↓
[2] Extract raw text from all pages
    ↓
[3] Clean text (remove empty lines, extra whitespace)
    ↓
[4] Engineer extraction prompt (define all 13 fields)
    ↓
[5] Call OpenAI gpt-4o-mini API (temperature=0)
    ↓
[6] Parse JSON response with json.loads()
    ↓
[7] Display and save results
    ↓
OUTPUT (JSON)

### Code Structure

Each function is clearly separated:

- "extract_text_from_pdf()" - PDF reading with pdfplumber
- "clean_text()" - Text preprocessing
- "get_extraction_prompt()" - Prompt engineering (critical!)
- "extract_invoice_data()" - OpenAI API call and JSON parsing
- "display_extracted_data()" - Pretty-print results
- "process_invoice()" - Main pipeline orchestrator

##  Sample Output

### Console Output

EXTRACTED DATA FROM: 3.pdf
------------------------------------------
Invoice Number:     INV-3337
Invoice Date:       25-01-2016
Due Date:           31-01-2016
Billed By:          DEMO - Sliced Invoices
Billed To:          Test Business

Line Items:
  1. Web Design: $85.00

Subtotal:           $85.00
Discount:           None
Tax/GST:            $8.50
Total Amount:       $93.50

Currency:           USD
Payment Method:     ANZ Bank
Notes:              Payment is due within 30 days from date of invoice. Late payment is subject to fees of 5% per month.
-------------------------------------------------

## JSON Output (output_invoice_3.json)
{
  "invoice_number": "INV-3337",
  "invoice_date": "25-01-2016",
  "due_date": "31-01-2016",
  "billed_by": "DEMO - Sliced Invoices",
  "billed_to": "Test Business",
  "line_items": [
    {
      "item": "Web Design",
      "amount": "$85.00"
    }
  ],
  "subtotal": "$85.00",
  "discount": null,
  "tax_or_gst": "$8.50",
  "total_amount": "$93.50",
  "currency": "USD",
  "payment_method": "ANZ Bank",
  "notes": "Payment is due within 30 days from date of invoice. Late payment is subject to fees of 5% per month."
}


---

##  Key Features

## Robust Text Extraction
- Uses 'pdfplumber' for reliable PDF reading
- Handles multi-page invoices
- Cleans whitespace and empty lines

###  Smart Prompt Engineering
- Defines all 13 required fields explicitly
- Specifies exact date format (DD-MM-YYYY)
- Enforces null for missing fields (not 'N/A' or empty strings)
- Prevents markdown code fences in output

###  Error Handling
- Try-except blocks for file operations
- JSON parsing error detection
- Graceful handling of missing files
- API failure recovery

###  Security
- API key stored in '.env' (not in code)
- '.gitignore' prevents accidental commits
- No sensitive data in source files

###  Clean Code
- Clear function names and docstrings
- Logical separation of concerns
- Comments above each major section
- Meaningful variable names


##  Testing

The pipeline has been tested on 3 different invoice types:

1.  Vendor Invoice - B2B requesting payment
2.  Sales Invoice
3. Service Invoice

Each test verifies:
-  PDF loads without errors
-  Text extraction captures all content
-  All 13 fields extracted correctly
-  JSON parses without errors
-  Missing fields return null (not empty strings)
-  Output saves correctly




