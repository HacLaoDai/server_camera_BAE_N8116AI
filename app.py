# app.py
from flask import Flask, request, jsonify
import jwt, bcrypt, os, base64
from functools import wraps
from datetime import datetime, timedelta

from database.db import users_col
from services.task_service import CameraClient

JWT_SECRET = "baoan_DSFfo832f@refw1!dfsof_3312ido0f"
JWT_EXPIRE_DAYS = 30
BASE_IMAGE_DIR = "/data/faces"

app = Flask(__name__)

# ======================
# JWT MIDDLEWARE
# ======================
def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"message": "Missing token"}), 401

        token = auth.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)
    return wrapper


# ======================
# LOGIN API
# ======================
@app.route("/api/login", methods=["POST"])
def login():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"message": "Invalid JSON"}), 400

    username = body.get("username", "").lower().replace("+84", "0").replace(" ", "")
    password = body.get("password")

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    user = users_col.find_one({
        "$or": [
            {"email": username},
            {"phone": username}
        ]
    })

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    stored_pw = user.get("password")
    if isinstance(stored_pw, str):
        stored_pw = stored_pw.encode()

    if not bcrypt.checkpw(password.encode(), stored_pw):
        return jsonify({"message": "Invalid credentials"}), 401

    payload = {
        "user_id": str(user["_id"]),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "roles": user.get("roles", []),
        "exp": datetime.utcnow() + timedelta(days=30)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token})


# ======================
# SET FACE API
# ======================
@app.route("/api/set-face", methods=["POST"])
@jwt_required
def set_face():
    body = request.json

    image_b64 = body.get("image_b64")
    name = body.get("name")
    group_id = body.get("group_id")

    if not image_b64:
        return jsonify({"message": "Missing image_b64"}), 400

    info = {
        "group_id": group_id,
        "name": name,
        "image": image_b64,
        "count": body.get("count", 1),
        "sex": body.get("sex", 0),
        "age": body.get("age", 0),
        "nation": body.get("nation", "VN"),
        "email": body.get("email", ""),
        "phone": body.get("phone", "")
    }

    cam = CameraClient("192.168.100.119", "admin", "Batek@abcd")
    if not cam.login():
        return jsonify({"message": "Camera login failed"}), 500

    resp = cam.add_face(info)

    return jsonify({
        "success": True,
        "set_by": request.user.get("phone"),
        "camera_response": resp.json()
    })

# -----------------------
@app.route("/api/remove", methods=["POST"])
@jwt_required
def Remove():
    body = request.json

    image_b64 = body.get("image_b64")
    name = body.get("name")
    group_id = body.get("group_id")

    if not image_b64:
        return jsonify({"message": "Missing image_b64"}), 400

    info = {
        "group_id": group_id,
        "name": name,
        "image": image_b64,
        "count": body.get("count", 1),
        "sex": body.get("sex", 0),
        "age": body.get("age", 0),
        "nation": body.get("nation", "VN"),
        "email": body.get("email", ""),
        "phone": body.get("phone", "")
    }

    cam = CameraClient("192.168.100.119", "admin", "Batek@abcd")
    if not cam.login():
        return jsonify({"message": "Camera login failed"}), 500

    resp = cam.add_face(info)

    return jsonify({
        "success": True,
        "set_by": request.user.get("phone"),
        "camera_response": resp.json()
    })
# --------------------
@app.route("/api/takelist", methods=["POST"])
@jwt_required
def Takelist():
    body = request.json

    image_b64 = body.get("image_b64")
    name = body.get("name")
    group_id = body.get("group_id")

    if not image_b64:
        return jsonify({"message": "Missing image_b64"}), 400

    info = {
        "group_id": group_id,
        "name": name,
        "image": image_b64,
        "count": body.get("count", 1),
        "sex": body.get("sex", 0),
        "age": body.get("age", 0),
        "nation": body.get("nation", "VN"),
        "email": body.get("email", ""),
        "phone": body.get("phone", "")
    }

    cam = CameraClient("192.168.100.119", "admin", "Batek@abcd")
    if not cam.login():
        return jsonify({"message": "Camera login failed"}), 500

    resp = cam.add_face(info)

    return jsonify({
        "success": True,
        "set_by": request.user.get("phone"),
        "camera_response": resp.json()
    })


if __name__ == "__main__":
    app.run(host="192.168.100.80", port=2123)
