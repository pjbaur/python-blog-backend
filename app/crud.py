from .models import UserModel
from .database import db
from bson.objectid import ObjectId

users_collection = db['users']

def create_user(user: UserModel):
    user_dict = user.dict(by_alias=True)
    insert_result = users_collection.insert_one(user_dict)
    user.id = str(insert_result.inserted_id)
    return user

def get_user_by_email(email: str):
    user_data = users_collection.find_one({"email": email})
    if user_data:
        return UserModel(**user_data)
    return None

def get_user_by_id(user_id: str):
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return UserModel(**user_data)
    return None

def get_all_users():
    users = []
    for user_data in users_collection.find():
        users.append(UserModel(**user_data))
    return users

def update_user(user_id: str, updates: dict):
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updates})

def delete_user(user_id: str):
    users_collection.delete_one({"_id": ObjectId(user_id)})
