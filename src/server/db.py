import os
from tenacity import retry, stop_after_attempt, wait_fixed

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Replace 'DATABASE_URL' with your actual database connection string
DATABASE_URL = os.environ['DATA_DB_CONNECTION']  # Ensure this is an async-compatible URL

# Create an async engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session maker
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
async def execute_db_operation(operation):
    async with AsyncSessionLocal() as session:
        try:
            result = await operation(session)
            await session.commit()
            return result
        except OperationalError as e:
            await session.rollback()
            raise e
