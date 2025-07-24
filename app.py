import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Note: Consider restricting origins for production, e.g., CORS(app, resources={r"/*": {"origins": "https://your-frontend-domain.com"}})

# MongoDB Atlas connection
MONGO_URI = os.environ["MONGO_URI"]  # Must be set in Render environment variables

try:
    client = MongoClient(MONGO_URI, tls=True, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connection at startup
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

db = client["userdb"]
collection = db["users"]

# Helper: Convert MongoDB ObjectId to string
def serialize_user(user):
    return {
        "_id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", "")
    }

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Flask MongoDB API"}), 200

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        users = list(collection.find())
        logger.info(f"Retrieved {len(users)} users from MongoDB")
        users = [serialize_user(user) for user in users]
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error in get_data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/add_data', methods=['POST'])
def add_data():
    user = request.get_json()
    if not user.get("name") or not user.get("email"):
        return jsonify({"message": "Name and Email are required"}), 400
    try:
        result = collection.insert_one(user)
        logger.info(f"Added user with ID: {str(result.inserted_id)}")
        return jsonify({
            "message": "User added successfully",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        logger.error(f"Error in add_data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_data/<string:user_id>', methods=['PUT'])
def update_data(user_id):
    try:
        ObjectId(user_id)  # Validate ObjectId
        updated_user = request.get_json()
        if not updated_user.get("name") or not updated_user.get("email"):
            return jsonify({"message": "Name and Email are required"}), 400
        result = collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updated_user}
        )
        if result.matched_count == 0:
            return jsonify({"message": "User not found"}), 404
        logger.info(f"Updated user with ID: {user_id}")
        return jsonify({"message": "User updated"}), 200
    except ValueError:
        return jsonify({"message": "Invalid user_id format"}), 400
    except Exception as e:
        logger.error(f"Error in update_data: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/delete_data/<string:user_id>', methods=['DELETE'])
def delete_data(user_id):
    try:
        ObjectId(user_id)  # Validate ObjectId
        result = collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "User not found"}), 404
        logger.info(f"Deleted user with ID: {user_id}")
        return jsonify({"message": "User deleted"}), 200
    except ValueError:
        return jsonify({"message": "Invalid user_id format"}), 400
    except Exception as e:
        logger.error(f"Error in delete_data: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        client.close()
        logger.info("MongoDB client closed")
        return jsonify({"message": "Server shutting down"}), 200
    except Exception as e:
        logger.error(f"Error in shutdown: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
