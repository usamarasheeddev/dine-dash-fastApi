import asyncio
from sqlalchemy.future import select
from app.core.database import engine, get_db
from app.models.user import User

async def count_users():
    async for db in get_db():
        result = await db.execute(select(User))
        users = result.scalars().all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"User: {user.email}")
        break

if __name__ == "__main__":
    asyncio.run(count_users())
