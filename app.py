from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId

# Initialization
app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["userdb"]
collection = db["users"]

# Helper: Serialize Mongo document
def ser(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "age": user["age"]  # ✅ lowercase 'age'
    }

# ----------------- USER ROUTES -----------------

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = [ser(u) for u in collection.find()]
    return jsonify({"users": users}), 200

# Get single user by ID
@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return jsonify(ser(user)), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except:
        return jsonify({"error": "Invalid user ID"}), 400

# Add a new user
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    if not data.get("name") or not data.get("age"):
        return jsonify({"error": "Name and age are required"}), 400

    user = {
        "name": data["name"],
        "age": data["age"]  # ✅ lowercase 'age'
    }
    result = collection.insert_one(user)
    user["_id"] = result.inserted_id
    return jsonify(ser(user)), 201

# Update user by ID
@app.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        updated = collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        if updated.matched_count == 0:
            return jsonify({"error": "User not found"}), 404
        user = collection.find_one({"_id": ObjectId(user_id)})
        return jsonify(ser(user)), 200
    except:
        return jsonify({"error": "Invalid user ID or update data"}), 400

# Delete user by ID
@app.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": f"User with ID {user_id} deleted successfully"}), 200
    except:
        return jsonify({"error": "Invalid user ID"}), 400

# ----------------- RUN APP -----------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
