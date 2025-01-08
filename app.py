from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to store connected users. Key is socket id, value is a dictionary with username and avatar URL.
users = {}

@app.route('/')
def index():
    return render_template('index.html')

# Handle client connection
@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000, 9999)}"
    gender = random.choice(["girl", "boy"])
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    users[request.sid] = {"username": username, "avatar": avatar_url, "join_time": datetime.now()}

    emit("user_joined", {"username": username, "avatar": avatar_url}, broadcast=True)
    emit("set_username", {"username": username})

# Handle client disconnection
@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)

# Handle incoming messages from users
@socketio.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if user:
        message_data = {
            "username": user["username"],
            "avatar": user["avatar"],
            "message": data.get("message", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        emit("new_message", message_data, broadcast=True)

# Handle username update requests
@socketio.on("update_username")
def handle_update_username(data):
    user = users.get(request.sid)
    if user:
        old_username = user["username"]
        new_username = data.get("username", "").strip()
        if new_username and new_username != old_username:
            user["username"] = new_username
            emit("username_updated", {
                "old_username": old_username,
                "new_username": new_username
            }, broadcast=True)

# Handle typing indicator
@socketio.on("typing")
def handle_typing(data):
    user = users.get(request.sid)
    if user:
        emit("user_typing", {"username": user["username"]}, broadcast=True, include_self=False)

# Handle stop typing indicator
@socketio.on("stop_typing")
def handle_stop_typing(data):
    user = users.get(request.sid)
    if user:
        emit("user_stopped_typing", {"username": user["username"]}, broadcast=True, include_self=False)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
