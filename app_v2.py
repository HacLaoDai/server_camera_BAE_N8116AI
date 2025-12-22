# app.py
from flask import Flask, request, jsonify
import jwt, bcrypt
from functools import wraps
from datetime import datetime, timedelta

from database.db import users_col
from services.task_service import CameraClient

JWT_SECRET = "baoan_DSFfo832f@refw1!dfsof_3312ido0f"
JWT_EXPIRE_DAYS = 30

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
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token})


# ======================
# SET FACE
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

# ======================
# REMOVE FACE
# ======================
@app.route("/api/remove-face", methods=["POST"])
@jwt_required
def remove_face():
    body = request.get_json(silent=True)

    MD5_txt = body.get("MD5_txt")
    face_id = body.get("face_id")

    if not MD5_txt or not face_id:
        return jsonify({"message": "Missing MD5 or face_id"}), 400

    try:
        task = CameraClient("192.168.100.119", "admin", "Batek@abcd")
        if not task.login():
            return jsonify({"message": "Camera login failed"}), 500

        resp = task.remove_face(MD5_txt, face_id)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return jsonify({
        "success": True,
        "removed_by": request.user.get("phone"),
        "camera_response": resp.json()
    })


# ======================
# TAKE LIST (GET FACE INFO)
# ======================
@app.route("/api/takelist", methods=["POST"])
@jwt_required
def takelist():
    body = request.get_json(silent=True)

    face_ids = body.get("face_ids", [])
    
    if not isinstance(face_ids, list):
        return jsonify({"message": "Missing face_ids"}), 400

    try:
        task = CameraClient("192.168.100.119", "admin", "Batek@abcd")
        if not task.login():
            return jsonify({"message": "Camera login failed"}), 500
        data = task.get_faces(face_ids)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return jsonify({
        "success": True,
        "data": data
    })


if __name__ == "__main__":
    app.run(host="192.168.100.80", port=2123, debug=True)
