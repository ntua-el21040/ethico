from ethico.database import create_supabase_client

try:
    client = create_supabase_client()

    response = (
        client.table("conversations")
        .select("*")
        .limit(1)
        .execute()
    )

    print("Database connection successful!")
    print(response.data)

except Exception as e:
    print("Database connection failed:", e)