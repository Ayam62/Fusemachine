import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# classicmodels schema context given to Gemini
SCHEMA_CONTEXT = """
You are a PostgreSQL expert. The database is called 'classicmodels' and has these tables:

- customers(customerNumber, customerName, contactLastName, contactFirstName, phone, addressLine1, city, state, postalCode, country, salesRepEmployeeNumber, creditLimit)
- employees(employeeNumber, lastName, firstName, extension, email, officeCode, reportsTo, jobTitle)
- offices(officeCode, city, phone, addressLine1, state, country, postalCode, territory)
- orderdetails(orderNumber, productCode, quantityOrdered, priceEach, orderLineNumber)
- orders(orderNumber, orderDate, requiredDate, shippedDate, status, comments, customerNumber)
- payments(customerNumber, checkNumber, paymentDate, amount)
- productlines(productLine, textDescription, htmlDescription, image)
- products(productCode, productName, productLine, productScale, productVendor, productDescription, quantityInStock, buyPrice, MSRP)

IMPORTANT RULES:
- Only write SELECT queries
- Use double quotes around column names that may be case-sensitive
- Return ONLY the raw SQL query, no explanation, no markdown, no backticks
"""


def extract_decomposition(question: str) -> str:
    prompt = f"""
{SCHEMA_CONTEXT}

Given this natural language question:
"{question}"

Break it down into:
- Intent: what is being asked
- Tables: which tables are needed
- Columns: which columns are needed
- Filters: any WHERE conditions
- Joins: any joins needed

Reply in this exact format:
Intent: ...
Tables: ...
Columns: ...
Filters: ...
Joins: ...
"""
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_sql(question: str, decomposition: str) -> str:
    prompt = f"""
{SCHEMA_CONTEXT}

Natural language question: "{question}"

Structured decomposition:
{decomposition}

Now write the PostgreSQL SELECT query. Return ONLY the raw SQL, nothing else.
"""
    response = model.generate_content(prompt)
    sql = response.text.strip()
    # Strip markdown code blocks if Gemini wraps them
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def fix_sql(original_sql: str, error_message: str) -> str:
    prompt = f"""
{SCHEMA_CONTEXT}

The following PostgreSQL query failed:

{original_sql}

Error message:
{error_message}

Fix the query and return ONLY the corrected raw SQL, nothing else.
"""
    response = model.generate_content(prompt)
    sql = response.text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def summarize_result(question: str, sql: str, result: list[dict]) -> str:
    """Convert raw SQL result into a natural language summary."""
    # Trim result to avoid huge prompts
    result_preview = result[:10]

    prompt = f"""
You are a data analyst. A user asked this question:
"{question}"

The SQL query run was:
{sql}

The result returned {len(result)} row(s). Here is a preview:
{json.dumps(result_preview, default=str, indent=2)}

Write a single clear, concise sentence summarizing the answer to the user's question.
Do not mention SQL. Do not say "the query". Just answer the question naturally.
"""
    response = model.generate_content(prompt)
    return response.text.strip()