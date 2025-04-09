from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
if not MONGO_URI:
    raise ValueError("No MONGO_URI found in environment variables")

client = MongoClient(MONGO_URI)
db = client['blog_db']
