import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Missing credentials")
    sys.exit(1)

supabase = create_client(url, key)

print("Attempting to insert a dummy row to discover columns (summary)...")

dummy = {
    # Try providing NO year/month since they failed? 
    # Or maybe year/month failed because I sent them?
    # The error was "column MonthlyReview.year does not exist".
    # So I should NOT send year.
    "summary": "ProbeSummary"
}

try:
    res = supabase.table("MonthlyReview").insert(dummy).execute()
    print("Insert success! Row:", res.data)
except Exception as e:
    print(f"Insert failed: {e}")
