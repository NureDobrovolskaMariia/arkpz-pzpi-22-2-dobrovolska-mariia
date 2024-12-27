from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from fastapi import HTTPException


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:Mnbv1234@localhost/postgres"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
bind=engine,
class_=AsyncSession,
expire_on_commit=False,
)

Base = declarative_base()

async def init_db():
    try:
        logger.info("Initializing the database.")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error occurred while initializing the database: {str(e)}")
        raise HTTPException(status_code=500, detail="Error initializing database")


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

async def get_db():
    try:
        logger.info("Attempting to create a new database session.")
        async with AsyncSessionLocal() as db:
            logger.info("Database session created successfully.")
            yield db
    except Exception as e:
        logger.error(f"Error occurred while getting the database session: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection error")

