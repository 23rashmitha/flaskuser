from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Connect to local MongoDB instance
client = MongoClient("mongodb+srv://rashmithakeshireddy:Renuka232006@mongodb.sn6rje7.mongodb.net/")
db = client["userdb"]
collection = db["users"]

# Helper: Convert MongoDB ObjectId to string without modifying original
def serialize_user(user):
    return {
        "_id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", "")
    }

# Route: Get all users
@app.route('/get_data', methods=['GET'])
def get_data():
    users = list(collection.find())
    users = [serialize_user(user) for user in users]
    return jsonify(users), 200

# Route: Add a new user
@app.route('/add_data', methods=['POST'])
def add_data():
    user = request.get_json()
    if not user.get("name") or not user.get("email"):
        return jsonify({"message": "Name and Email are required"}), 400

    result = collection.insert_one(user)
    return jsonify({
        "message": "User added successfully",
        "id": str(result.inserted_id)
    }), 201

# Route: Update user by ID
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

# Route: Delete user by ID
@app.route('/delete_data/<string:user_id>', methods=['DELETE'])
def delete_data(user_id):
    try:
        result = collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

