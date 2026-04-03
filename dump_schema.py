import asyncio
from sqlalchemy import text
from app.core.database import engine

async def dump_schema():
    async with engine.connect() as conn:
        # List all tables
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables: {tables}")
        
        for table in tables:
            print(f"\nColumns for '{table}':")
            result = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"))
            columns = [row[0] for row in result.fetchall()]
            print(columns)

if __name__ == "__main__":
    asyncio.run(dump_schema())
