from .models import UserModel
from .database import db
from bson.objectid import ObjectId

users_collection = db['users']

def create_user(user: UserModel):
    # Convert to dict but exclude_unset to avoid sending null _id
    user_dict = user.dict(by_alias=True, exclude_unset=True)
    # Explicitly remove _id if it's None to let MongoDB generate it
    if "_id" in user_dict and user_dict["_id"] is None:
        del user_dict["_id"]
    insert_result = users_collection.insert_one(user_dict)
    user.id = str(insert_result.inserted_id)
    print(f"User created with ID: {user.id}")
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
