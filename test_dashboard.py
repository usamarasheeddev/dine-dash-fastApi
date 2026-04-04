import asyncio
import sys
import os

sys.path.append('c:\\Users\\usama\\Desktop\\Projects\\dine-dash\\fastapi-backend')

from app.core.database import AsyncSessionLocal
from app.routes.dashboard import get_dashboard_stats
from app.models.user import User

async def main():
    try:
        async with AsyncSessionLocal() as db:
            user = User(company_id=1)
            # This calls the dict return of the router endpoint:
            res = await get_dashboard_stats(timeframe='daily', current_user=user, db=db)
            
            # Now we need to pass it to the Pydantic model to see where it fails!
            from app.schemas.dashboard import DashboardResponse
            try:
                validated = DashboardResponse.model_validate(res)
                print("Validation Success!")
            except Exception as ve:
                import traceback
                print("Validation Error:")
                traceback.print_exc()
    except Exception as e:
        import traceback
        print("Function Error:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
