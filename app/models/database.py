from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError("Les variables d'environnement pour la base de données ne sont pas correctement chargées.")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/{POSTGRES_DB}"
logger.info(f"Connexion à la base de données PostgreSQL : {DATABASE_URL}")

# Print the retrieved DATABASE_URL for debugging purposes
print(f"Using DATABASE_URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL, echo=True)
except Exception as e:
    logger.error(f"Erreur lors de la connexion à la base de données : {e}")
    raise e

# Configure the session
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

# Declare the Base
BaseSQL = declarative_base()
