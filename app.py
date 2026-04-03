import os
from flask import Flask, request, jsonify, render_template_string
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

        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_id TEXT NOT NULL,
            menu_item TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

MENU_ITEMS = [
    "Classic Cheeseburger",
    "Crispy Chicken Sandwich",
    "Loaded Fries",
    "Coke Float",
    "Vanilla Shake",
    "Veggie Wrap",
]

HOME_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ketchup & Mustard Grill</title>
    <style>
        :root {
            --red: #e63946;
            --red-dark: #b71c1c;
            --yellow: #ffd60a;
            --yellow-soft: #fff2b2;
            --cream: #fff9e6;
            --text: #2b2b2b;
            --muted: #6b6b6b;
            --card: rgba(255, 255, 255, 0.92);
            --shadow: 0 18px 50px rgba(130, 30, 30, 0.22);
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, Helvetica, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(255, 214, 10, 0.32), transparent 30%),
                linear-gradient(135deg, #7f0909 0%, #b91c1c 35%, #f59e0b 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 28px;
        }

        .shell {
            width: min(1100px, 100%);
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 24px;
            align-items: stretch;
        }

        .hero, .panel {
            background: var(--card);
            border-radius: 28px;
            box-shadow: var(--shadow);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .hero {
            padding: 36px;
            position: relative;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--red), var(--yellow));
            color: white;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-size: 0.82rem;
        }

        h1 {
            margin: 18px 0 10px;
            font-size: clamp(2.3rem, 5vw, 4.6rem);
            line-height: 0.98;
            letter-spacing: -0.05em;
        }

        .lead {
            font-size: 1.05rem;
            color: var(--muted);
            max-width: 46ch;
            line-height: 1.6;
            margin-bottom: 24px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 22px;
        }

        .stat {
            background: linear-gradient(180deg, white, var(--cream));
            border: 1px solid rgba(183, 28, 28, 0.12);
            border-radius: 18px;
            padding: 16px;
        }

        .stat strong {
            display: block;
            font-size: 1.3rem;
            color: var(--red-dark);
            margin-bottom: 6px;
        }

        .panel {
            padding: 28px;
            border: 1px solid rgba(255, 255, 255, 0.35);
        }

        .panel h2 {
            margin: 0 0 8px;
            font-size: 1.8rem;
        }

        .panel p {
            margin: 0 0 22px;
            color: var(--muted);
            line-height: 1.5;
        }

        label {
            display: block;
            font-weight: 700;
            margin: 16px 0 8px;
        }

        input, select {
            width: 100%;
            padding: 14px 16px;
            border-radius: 16px;
            border: 2px solid rgba(183, 28, 28, 0.14);
            background: white;
            font-size: 1rem;
            outline: none;
        }

        input:focus, select:focus {
            border-color: var(--red);
            box-shadow: 0 0 0 4px rgba(230, 57, 70, 0.14);
        }

        .btn {
            margin-top: 22px;
            width: 100%;
            border: 0;
            padding: 16px 18px;
            border-radius: 16px;
            background: linear-gradient(90deg, var(--red), #ff7b00);
            color: white;
            font-size: 1rem;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 14px 25px rgba(183, 28, 28, 0.25);
        }

        .btn:hover {
            transform: translateY(-1px);
        }

        .message {
            margin-bottom: 18px;
            padding: 14px 16px;
            border-radius: 16px;
            font-weight: 700;
            line-height: 1.4;
        }

        .message.success {
            background: rgba(255, 214, 10, 0.22);
            border: 1px solid rgba(183, 28, 28, 0.18);
        }

        .message.error {
            background: rgba(230, 57, 70, 0.12);
            border: 1px solid rgba(183, 28, 28, 0.24);
        }

        .summary {
            margin-top: 18px;
            padding: 18px;
            border-radius: 18px;
            background: linear-gradient(180deg, #fff, #fff7d1);
            border: 1px solid rgba(183, 28, 28, 0.12);
        }

        .summary h3 {
            margin: 0 0 10px;
        }

        .summary span {
            color: var(--red-dark);
            font-weight: 800;
        }

        @media (max-width: 900px) {
            .shell { grid-template-columns: 1fr; }
            .stats { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <div class="badge">Ketchup &amp; Mustard Grill</div>
            <h1>Fast, fun, and built for hungry people.</h1>
            <p class="lead">
                Enter your customer ID, choose your meal from the dropdown, and send your order straight to the kitchen.
                Clean, simple, and styled like a classic red-and-yellow burger joint.
            </p>

            <div class="stats">
                <div class="stat"><strong>01</strong>Pick your meal</div>
                <div class="stat"><strong>02</strong>Enter your ID</div>
                <div class="stat"><strong>03</strong>Place order</div>
            </div>

            {% if confirmation %}
            <div class="summary">
                <h3>Order received</h3>
                <p><span>Customer ID:</span> {{ confirmation.customer_id }}</p>
                <p><span>Order:</span> {{ confirmation.menu_item }}</p>
                <p><span>Status:</span> {{ confirmation.status }}</p>
            </div>
            {% endif %}
        </section>

        <section class="panel">
            <h2>Start your order</h2>
            <p>Use the form below to submit a simple restaurant order.</p>

            {% if error %}
            <div class="message error">{{ error }}</div>
            {% endif %}

            {% if saved_to_db %}
            <div class="message success">Your order was saved successfully.</div>
            {% endif %}

            <form method="post">
                <label for="customer_id">Customer ID</label>
                <input id="customer_id" name="customer_id" placeholder="Enter your customer ID" value="{{ customer_id or '' }}" required>

                <label for="menu_item">Menu Item</label>
                <select id="menu_item" name="menu_item" required>
                    <option value="" disabled {% if not menu_item %}selected{% endif %}>Choose your order</option>
                    {% for item in menu_items %}
                    <option value="{{ item }}" {% if menu_item == item %}selected{% endif %}>{{ item }}</option>
                    {% endfor %}
                </select>

                <button class="btn" type="submit">Place Order</button>
            </form>
        </section>
    </main>
</body>
</html>
"""


def save_order(customer_id, menu_item):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO orders (customer_id, menu_item) VALUES (%s, %s) RETURNING id;",
            (customer_id, menu_item)
        )

        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return order_id

    except Exception as e:
        print("Order storage unavailable:", e)
        return None


@app.route("/", methods=["GET", "POST"])
def home():
    confirmation = None
    error = None
    saved_to_db = False

    if request.method == "POST":
        customer_id = request.form.get("customer_id", "").strip()
        menu_item = request.form.get("menu_item", "").strip()

        if not customer_id or not menu_item:
            error = "Please enter your customer ID and choose an item."
        elif menu_item not in MENU_ITEMS:
            error = "Please choose a valid menu item."
        else:
            order_id = save_order(customer_id, menu_item)
            saved_to_db = order_id is not None
            confirmation = {
                "customer_id": customer_id,
                "menu_item": menu_item,
                "status": f"Order #{order_id} accepted" if order_id else "Order accepted locally"
            }

        return render_template_string(
            HOME_TEMPLATE,
            confirmation=confirmation,
            error=error,
            saved_to_db=saved_to_db,
            customer_id=customer_id,
            menu_item=menu_item,
            menu_items=MENU_ITEMS,
        )

    return render_template_string(
        HOME_TEMPLATE,
        confirmation=None,
        error=None,
        saved_to_db=False,
        customer_id="",
        menu_item="",
        menu_items=MENU_ITEMS,
    )


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