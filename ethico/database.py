import os

from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.client import ClientOptions

load_dotenv()


def create_supabase_client() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_PUBLISHABLE_KEY"],
        options=ClientOptions(
            persist_session=False,
            auto_refresh_token=False,
        ),
    )
