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
    <title>NSUBUGA HOT MEALS</title>
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

        .mode-switch {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 16px;
        }

        .mode-btn {
            border: 0;
            padding: 12px;
            border-radius: 12px;
            font-weight: 700;
            cursor: pointer;
            background: rgba(183, 28, 28, 0.1);
            color: var(--red-dark);
        }

        .mode-btn.active {
            background: linear-gradient(90deg, var(--red), #ff7b00);
            color: #fff;
        }

        .panel-slider {
            overflow: hidden;
            width: 100%;
        }

        .panel-track {
            width: 200%;
            display: flex;
            transition: transform 0.35s ease;
        }

        .panel-page {
            width: 50%;
            padding-right: 2px;
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

        .orders-list {
            margin-top: 14px;
            display: grid;
            gap: 10px;
            max-height: 280px;
            overflow: auto;
        }

        .order-card {
            background: linear-gradient(180deg, #fff, #fff7d1);
            border: 1px solid rgba(183, 28, 28, 0.15);
            border-radius: 14px;
            padding: 12px;
        }

        .order-head {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .order-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 10px;
        }

        .mini-btn {
            border: 0;
            border-radius: 10px;
            padding: 10px;
            font-weight: 700;
            cursor: pointer;
        }

        .mini-btn.update {
            background: #ffe066;
            color: #7f0909;
        }

        .mini-btn.delete {
            background: #ffccd5;
            color: #7f0909;
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
            <div class="badge">NSUBUGA HOT MEALS</div>
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
        </section>

        <section class="panel">
            <div class="mode-switch">
                <button id="showPlace" class="mode-btn active" type="button">Place Order</button>
                <button id="showView" class="mode-btn" type="button">View / Manage Orders</button>
            </div>

            <div class="panel-slider">
                <div id="panelTrack" class="panel-track">
                    <section class="panel-page">
                        <h2>Start your order</h2>
                        <p>Submit a fresh order for this customer.</p>

                        <form id="placeOrderForm">
                            <label for="place_customer_id">Customer ID</label>
                            <input id="place_customer_id" name="customer_id" placeholder="Enter your customer ID" required>

                            <label for="place_menu_item">Menu Item</label>
                            <select id="place_menu_item" name="menu_item" required>
                                <option value="" disabled selected>Choose your order</option>
                                {% for item in menu_items %}
                                <option value="{{ item }}">{{ item }}</option>
                                {% endfor %}
                            </select>

                            <button class="btn" type="submit">Place Order</button>
                        </form>
                    </section>

                    <section class="panel-page">
                        <h2>Find your orders</h2>
                        <p>Enter customer ID first, then manage existing orders.</p>

                        <form id="viewOrdersForm">
                            <label for="view_customer_id">Customer ID</label>
                            <input id="view_customer_id" name="customer_id" placeholder="Enter your customer ID" required>
                            <button class="btn" type="submit">Load Orders</button>
                        </form>

                        <div id="ordersList" class="orders-list"></div>
                    </section>
                </div>
            </div>
        </section>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script>
        const panelTrack = document.getElementById("panelTrack");
        const showPlaceBtn = document.getElementById("showPlace");
        const showViewBtn = document.getElementById("showView");
        const placeOrderForm = document.getElementById("placeOrderForm");
        const viewOrdersForm = document.getElementById("viewOrdersForm");
        const ordersList = document.getElementById("ordersList");
        const menuItems = {{ menu_items | tojson }};

        let activeCustomerId = "";

        function setMode(mode) {
            const viewMode = mode === "view";
            panelTrack.style.transform = viewMode ? "translateX(-50%)" : "translateX(0%)";
            showPlaceBtn.classList.toggle("active", !viewMode);
            showViewBtn.classList.toggle("active", viewMode);
        }

        showPlaceBtn.addEventListener("click", () => setMode("place"));
        showViewBtn.addEventListener("click", () => setMode("view"));

        function renderOrders(orders) {
            if (!orders.length) {
                ordersList.innerHTML = '<div class="message error">No orders found for this customer ID.</div>';
                return;
            }

            ordersList.innerHTML = orders.map(order => {
                const options = menuItems.map(item =>
                    `<option value="${item}" ${item === order.menu_item ? "selected" : ""}>${item}</option>`
                ).join("");

                return `
                    <article class="order-card" data-order-id="${order.id}">
                        <div class="order-head">
                            <span>Order #${order.id}</span>
                            <span>${order.created_at || ""}</span>
                        </div>
                        <label>Menu Item</label>
                        <select class="edit-menu-item">${options}</select>
                        <div class="order-actions">
                            <button class="mini-btn update" type="button" data-action="update">Update</button>
                            <button class="mini-btn delete" type="button" data-action="delete">Delete</button>
                        </div>
                    </article>
                `;
            }).join("");
        }

        async function loadOrders(customerId) {
            const res = await fetch(`/orders?customer_id=${encodeURIComponent(customerId)}`);
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Could not load orders");
            }

            renderOrders(data.orders || []);
        }

        placeOrderForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const customer_id = document.getElementById("place_customer_id").value.trim();
            const menu_item = document.getElementById("place_menu_item").value;

            try {
                const res = await fetch("/orders", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ customer_id, menu_item })
                });
                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.error || "Failed to place order");
                }

                await Swal.fire({
                    icon: "success",
                    title: "Order placed",
                    text: `Order #${data.id} saved successfully.`
                });

                placeOrderForm.reset();
            } catch (err) {
                Swal.fire({ icon: "error", title: "Oops", text: err.message });
            }
        });

        viewOrdersForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const customerId = document.getElementById("view_customer_id").value.trim();

            if (!customerId) {
                Swal.fire({ icon: "warning", title: "Required", text: "Please enter customer ID first." });
                return;
            }

            activeCustomerId = customerId;

            try {
                await loadOrders(customerId);
                Swal.fire({ icon: "success", title: "Loaded", text: "Orders loaded successfully." });
            } catch (err) {
                Swal.fire({ icon: "error", title: "Load failed", text: err.message });
                ordersList.innerHTML = "";
            }
        });

        ordersList.addEventListener("click", async (e) => {
            const action = e.target.dataset.action;
            if (!action) return;

            if (!activeCustomerId) {
                Swal.fire({ icon: "warning", title: "Required", text: "Enter customer ID to manage orders." });
                return;
            }

            const card = e.target.closest(".order-card");
            const orderId = card?.dataset.orderId;
            const menuSelect = card?.querySelector(".edit-menu-item");

            if (!orderId) return;

            try {
                if (action === "update") {
                    const res = await fetch(`/orders/${orderId}`, {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            customer_id: activeCustomerId,
                            menu_item: menuSelect.value
                        })
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || "Update failed");

                    await Swal.fire({ icon: "success", title: "Updated", text: "Order updated successfully." });
                    await loadOrders(activeCustomerId);
                }

                if (action === "delete") {
                    const res = await fetch(`/orders/${orderId}`, {
                        method: "DELETE",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ customer_id: activeCustomerId })
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || "Delete failed");

                    await Swal.fire({ icon: "success", title: "Deleted", text: "Order deleted successfully." });
                    await loadOrders(activeCustomerId);
                }
            } catch (err) {
                Swal.fire({ icon: "error", title: "Operation failed", text: err.message });
            }
        });
    </script>
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


@app.route("/", methods=["GET"])
def home():
    return render_template_string(
        HOME_TEMPLATE,
        menu_items=MENU_ITEMS,
    )


@app.route("/orders", methods=["POST"])
def create_order():
    try:
        data = request.get_json(silent=True) or {}
        customer_id = str(data.get("customer_id", "")).strip()
        menu_item = str(data.get("menu_item", "")).strip()

        if not customer_id or not menu_item:
            return jsonify({"error": "customer_id and menu_item are required"}), 400

        if menu_item not in MENU_ITEMS:
            return jsonify({"error": "Invalid menu item"}), 400

        order_id = save_order(customer_id, menu_item)
        if order_id is None:
            return jsonify({"error": "Could not save order"}), 500

        return jsonify({"message": "Order created", "id": order_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/orders", methods=["GET"])
def list_orders():
    try:
        customer_id = request.args.get("customer_id", "").strip()
        if not customer_id:
            return jsonify({"error": "customer_id is required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, customer_id, menu_item, created_at FROM orders WHERE customer_id=%s ORDER BY id DESC;",
            (customer_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        orders = [
            {
                "id": row[0],
                "customer_id": row[1],
                "menu_item": row[2],
                "created_at": row[3].strftime("%Y-%m-%d %H:%M") if row[3] else None,
            }
            for row in rows
        ]

        return jsonify({"orders": orders})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    try:
        data = request.get_json(silent=True) or {}
        customer_id = str(data.get("customer_id", "")).strip()
        menu_item = str(data.get("menu_item", "")).strip()

        if not customer_id or not menu_item:
            return jsonify({"error": "customer_id and menu_item are required"}), 400

        if menu_item not in MENU_ITEMS:
            return jsonify({"error": "Invalid menu item"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE orders SET menu_item=%s WHERE id=%s AND customer_id=%s RETURNING id;",
            (menu_item, order_id, customer_id),
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not updated:
            return jsonify({"error": "Order not found for this customer"}), 404

        return jsonify({"message": "Order updated", "id": order_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def remove_order(order_id):
    try:
        data = request.get_json(silent=True) or {}
        customer_id = str(data.get("customer_id", "")).strip()

        if not customer_id:
            return jsonify({"error": "customer_id is required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM orders WHERE id=%s AND customer_id=%s RETURNING id;",
            (order_id, customer_id),
        )
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not deleted:
            return jsonify({"error": "Order not found for this customer"}), 404

        return jsonify({"message": "Order deleted", "id": order_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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