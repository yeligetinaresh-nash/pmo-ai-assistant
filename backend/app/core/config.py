import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pmo_user:pmo_password@localhost:5432/pmo_db"
)