"""
Configuration settings for database connection.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'company_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_connection_string() -> str:
    """Generate PostgreSQL connection string from config."""
    return (f"dbname={DATABASE_CONFIG['dbname']} "
            f"user={DATABASE_CONFIG['user']} "
            f"password={DATABASE_CONFIG['password']} "
            f"host={DATABASE_CONFIG['host']} "
            f"port={DATABASE_CONFIG['port']}")
