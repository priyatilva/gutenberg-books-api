from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://gutenberg_user:gutenberg123@localhost:5432/gutenberg"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
