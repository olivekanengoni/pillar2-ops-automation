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
SOP_TEXT = """Only the SFO card may be used. Buyer: QUANT LAB SFO FZCO.
TRN: 105069744800001. Personal cards are not allowed.
Invoices must be uploaded to Google Drive."""
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
