import asyncio
from sqlalchemy import text
from app.core.database import engine

async def verify_tables():
    try:
        async with engine.connect() as conn:
            # Check Users (uppercase) columns
            try:
                result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'Users'"))
                columns = [row[0] for row in result.fetchall()]
                print(f"Columns in 'Users' (uppercase): {columns}")
            except Exception as e:
                print(f"Error checking columns: {e}")
                
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    asyncio.run(verify_tables())
