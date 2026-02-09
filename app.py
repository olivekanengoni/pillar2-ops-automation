from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- Database (Postgres) ---
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432"),
    sslmode='require'
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    source TEXT,
    input TEXT,
    action TEXT
)
""")
conn.commit()

# --- ChromaDB ---
chroma = chromadb.Client()
collection = chroma.get_or_create_collection("sop")

# --- Load SOP once (MVP) ---
SOP_TEXT = """SFO EXPENSES – STANDARD OPERATING PROCEDURE (SOP)
Company: QUANT LAB SFO FZCO
Applies to: All purchases made using the SFO (company) card

1. Purpose
To ensure all company expenses are UAE audit-compliant, properly documented for accounting,
and clearly separated from personal expenses.

2. What Can Be Purchased
2.1 Employee Assets
• Laptops
• Mobile phones
• Tablets
• Company SIM cards / DU recharge plans (SIM must be registered under Quantlab)

2.2 Products, Services & Subscriptions
The following must be purchased only under a company account (examples, not limited to):
• Products required for company or employee use
• Recruitment portals (e.g. pracuj.pl, Indeed)
• Software tools
• Business subscriptions
• DU business / enterprise mobile plans
Conditions (mandatory):
• Purchase under company account (QUANT LAB SFO FZCO)
• Payment via SFO card
• Valid invoice issued to company

3. Payment Rule
• Only the SFO card may be used
• Personal cards are not allowed
• No mixing personal and company items

4. Shipping & Billing Details
Shipping Address:
Villa 47A, Frond N, Palm Jumeirah, Dubai, United Arab Emirates
Billing Address (Bills To):
QUANT LAB SFO FZCO
DMCC Business Centre, UT-11-CO-190
Uptown Tower, JLT, Dubai, UAE
This billing address must be used until DMCC registration is officially updated.

5. Purchase as Company & Tax Details
Buyer Name: QUANT LAB SFO FZCO
TRN: 105069744800001

6. Online Accounts
Personal accounts must be avoided. If no company account exists, one must be created under
QUANT LAB SFO FZCO.

7. Invoices
A valid tax invoice is mandatory and must include seller details, buyer name, billing address, TRN,
invoice date, and amount.

8. Invoice Storage
All invoices must be uploaded to the SFO Purchases – Invoices Google Drive folder.

9. PA Responsibility Summary
Ensure correct payment, correct buyer details, correct billing address, TRN inclusion, and invoice
upload.
"""

collection.add(
    ids=["sfo_expense_sop"],
    documents=[SOP_TEXT]
)


# --- Request schema ---
class Intake(BaseModel):
    message: str
    source: str

@app.post("/process")
def process_request(data: Intake):
    # RAG lookup
    result = collection.query(
        query_texts=[data.message],
        n_results=1
    )

    sop_context = result["documents"][0][0]

    # Simple classification (MVP logic)
    if "expense" in data.message.lower():
        category = "Finance"
        priority = 4
    else:
        category = "General"
        priority = 2

    enriched_text = f"""
Task: {data.message}

Relevant SOP:
{sop_context}
"""

    # Log
    cursor.execute(
        "INSERT INTO audit_logs (source, input, action) VALUES (%s, %s, %s)",
        (data.source, data.message, "processed")
    )
    conn.commit()

    return {
        "task_content": enriched_text,
        "category": category,
        "priority": priority
    }

