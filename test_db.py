from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

# Password ko encode karo taaki @ symbol break na kare
raw_password = os.getenv("password")
encoded_password = urllib.parse.quote_plus(raw_password)

user = os.getenv("user")
host = os.getenv("host")
port = os.getenv("port")
dbname = os.getenv("dbname")

# Ab encoded_password use karenge
# .env se load ho raha hai
db_url = f"postgresql+psycopg2://{os.getenv('user')}:{urllib.parse.quote_plus(os.getenv('password'))}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('dbname')}?sslmode=require"

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("✅ CONNECTION SUCCESSFUL!")
except Exception as e:
    print(f"❌ FAILED: {e}")