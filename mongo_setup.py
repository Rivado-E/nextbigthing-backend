from dotenv import load_dotenv, find_dotenv
import os
import pprint
from pymongo import MongoClient

load_dotenv(find_dotenv())

# MongoDB setup
password = os.environ.get("MONGODB_PASSWORD")
connection_string = f"mongodb+srv://admin:{password}@clubappcluster.cvs5zcu.mongodb.net/?retryWrites=true&w=majority&appName=ClubAppCluster"
client = MongoClient(connection_string)

# Accessing database and collections
# Main database for our application
umd_club_app_db = client.umd_club_app

# All Clubs collection
clubs = umd_club_app_db.clubs

# All Users collection
users = umd_club_app_db.users

