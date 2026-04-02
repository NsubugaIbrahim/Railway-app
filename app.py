import os
from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Connect to PostgreSQL using Railway DATABASE_URL
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
""")
conn.commit()


@app.route("/")
def home():
    return "Flask app running on Railway 🚀"


# CREATE
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING id;", (data["name"],))
    conn.commit()
    return jsonify({"message": "User created"})


# READ
@app.route("/users", methods=["GET"])
def get_users():
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    return jsonify(users)


# UPDATE
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    cur.execute("UPDATE users SET name=%s WHERE id=%s;", (data["name"], id))
    conn.commit()
    return jsonify({"message": "User updated"})


# DELETE
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    cur.execute("DELETE FROM users WHERE id=%s;", (id,))
    conn.commit()
    return jsonify({"message": "User deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))