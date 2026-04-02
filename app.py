import os
from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# -------------------------------
# Database Connection Function
# -------------------------------
def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not set")

    return psycopg2.connect(database_url)


# -------------------------------
# Initialize Database (safe)
# -------------------------------
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")

    except Exception as e:
        print("Database not ready yet:", e)


# Run DB initialization (safe)
init_db()


# -------------------------------
# Routes
# -------------------------------

@app.route("/")
def home():
    return "Flask app running on Railway 🚀"


# CREATE
@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name) VALUES (%s) RETURNING id;",
            (data["name"],)
        )

        user_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User created", "id": user_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# READ
@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users;")
        users = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UPDATE
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    try:
        data = request.get_json()

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE users SET name=%s WHERE id=%s;",
            (data["name"], id)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM users WHERE id=%s;", (id,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "User deleted"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))