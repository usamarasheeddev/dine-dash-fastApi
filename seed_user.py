import asyncio
from sqlalchemy.future import select
from app.core.database import engine, get_db
from app.models.user import User
from app.models.company import Company
from app.core.security import get_password_hash

async def seed_user():
    async for db in get_db():
        # First, ensure a company exists
        result = await db.execute(select(Company))
        company = result.scalars().first()
        if not company:
            company = Company(name="Test Company", email="test@example.com")
            db.add(company)
            await db.flush()
        
        # Then, ensure a user exists
        email = "rxxpulse@gmail.com" # Using the one from .env for testing
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            user = User(
                username="testuser",
                email=email,
                password=get_password_hash("password123"),
                role="admin",
                company_id=company.id
            )
            db.add(user)
            print(f"Created user with email: {email}")
        else:
            print(f"User with email: {email} already exists")
            
        await db.commit()
        break

if __name__ == "__main__":
    asyncio.run(seed_user())
