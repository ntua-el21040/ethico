import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def create_supabase_client() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_PUBLISHABLE_KEY"],
    )