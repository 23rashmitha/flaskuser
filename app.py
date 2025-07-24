from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB Atlas connection
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://rashmithakeshireddy:Renuka232006@mongodb.sn6rje7.mongodb.net/userdb?retryWrites=true&w=majority"
)

# Connect with TLS (SSL)
client = MongoClient(MONGO_URI, tls=True)

db = client["userdb"]
collection = db["users"]

# Helper: Convert MongoDB ObjectId to string
def serialize_user(user):
    return {
        "_id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", "")
    }

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        users = list(collection.find())
        users = [serialize_user(user) for user in users]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_data', methods=['POST'])
def add_data():
    user = request.get_json()
    if not user.get("name") or not user.get("email"):
        return jsonify({"message": "Name and Email are required"}), 400
    try:
        result = collection.insert_one(user)
        return jsonify({
            "message": "User added successfully",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_data/<string:user_id>', methods=['PUT'])
def update_data(user_id):
    updated_user = request.get_json()
    if not updated_user.get("name") or not updated_user.get("email"):
        return jsonify({"message": "Name and Email are required"}), 400
    try:
        result = collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updated_user}
        )
        if result.matched_count == 0:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"message": "User updated"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

@app.route('/delete_data/<string:user_id>', methods=['DELETE'])
def delete_data(user_id):
    try:
        result = collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

# Entry point for Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
