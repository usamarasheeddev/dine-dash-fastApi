import asyncio
from sqlalchemy.future import select
from app.core.database import engine, get_db
from app.models.service_request import ServiceRequest

async def check_requests():
    async for db in get_db():
        result = await db.execute(select(ServiceRequest))
        reqs = result.scalars().all()
        print(f"Total registration requests: {len(reqs)}")
        for req in reqs:
            print(f"Request: {req.email} for {req.company_name}")
        break

if __name__ == "__main__":
    asyncio.run(check_requests())
