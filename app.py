from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "fashion_store_secret_key"


# ==================================================
# PRODUCTS
# ==================================================

products = [
    # ================= MEN =================

    {
        "id": 1,
        "name": "Men's T-Shirt",
        "price": 499,
        "category": "Men",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab"
    },
    {
        "id": 2,
        "name": "Men's Shirt",
        "price": 799,
        "category": "Men",
        "image": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf"
    },
    {
        "id": 3,
        "name": "Men's Jeans",
        "price": 999,
        "category": "Men",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d"
    },
    {
        "id": 4,
        "name": "Men's Polo T-Shirt",
        "price": 699,
        "category": "Men",
        "image": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d"
    },
    {
        "id": 5,
        "name": "Men's Kurta",
        "price": 899,
        "category": "Men",
        "image": "https://images.unsplash.com/photo-1617127365659-c47fa864d8bc"
    },
    {
        "id": 6,
        "name": "Men's Hoodie",
        "price": 1099,
        "category": "Men",
        "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7"
    },

    # ================= WOMEN =================

    {
        "id": 7,
        "name": "Women's Suit",
        "price": 1299,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1"
    },
    {
        "id": 8,
        "name": "Women's Dupatta",
        "price": 499,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c"
    },
    {
        "id": 9,
        "name": "Women's Lehenga",
        "price": 2499,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1583391733956-6c78276477e2"
    },
    {
        "id": 10,
        "name": "Women's Dress",
        "price": 999,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8"
    },
    {
        "id": 11,
        "name": "Women's Top",
        "price": 599,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3"
    },
    {
        "id": 12,
        "name": "Women's Kurti",
        "price": 899,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1610030469668-8e9f641aaf58"
    },
    {
        "id": 13,
        "name": "Women's Saree",
        "price": 1499,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb"
    },
    {
        "id": 14,
        "name": "Women's Jeans",
        "price": 899,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246"
    },
    {
        "id": 15,
        "name": "Women's Palazzo",
        "price": 699,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f"
    },

    # ================= KIDS =================

    {
        "id": 16,
        "name": "Kids T-Shirt",
        "price": 299,
        "category": "Kids",
        "image": "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea"
    },
    {
        "id": 17,
        "name": "Kids Shirt",
        "price": 399,
        "category": "Kids",
        "image": "https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8"
    },
    {
        "id": 18,
        "name": "Kids Jeans",
        "price": 499,
        "category": "Kids",
        "image": "https://images.unsplash.com/photo-1519457431-44ccd64a579b"
    },
    {
        "id": 19,
        "name": "Kids Dress",
        "price": 599,
        "category": "Kids",
        "image": "https://images.unsplash.com/photo-1503919545889-aef636e10ad4"
    },
    {
        "id": 20,
        "name": "Kids Kurta",
        "price": 699,
        "category": "Kids",
        "image": "https://images.unsplash.com/photo-1621452773781-0f992fd1f5e4"
    }
]


# ==================================================
# CART
# ==================================================

cart = {}


# ==================================================
# DATABASE
# ==================================================

def create_database():

    connection = sqlite3.connect("orders.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            product TEXT NOT NULL,
            total INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    try:
        cursor.execute(
            "ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT 'Cash on Delivery'"
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()


create_database()
# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    search = request.args.get("search", "")
    category = request.args.get("category", "")

    filtered_products = products

    # Search filter
    if search:
        filtered_products = [
            product for product in filtered_products
            if search.lower() in product["name"].lower()
        ]

    # Category filter
    if category:
        filtered_products = [
            product for product in filtered_products
            if product["category"] == category
        ]

    cart = session.get("cart", {})
    cart_count = sum(
    item["quantity"] for item in cart.values()
)

    return render_template(
        "index.html",
        products=filtered_products,
        cart_count=cart_count
    )


# ==================================================
# ADD TO CART
# ==================================================
@app.route("/product/<int:product_id>")
def product_details(product_id):

    selected_product = None

    for product in products:
        if product["id"] == product_id:
            selected_product = product
            break

    if selected_product is None:
        return "Product not found"

    cart_count = sum(
        item["quantity"] for item in cart.values()
    )

    return render_template(
        "product_details.html",
        product=selected_product,
        cart_count=cart_count
    )
    @app.route("/track_order", methods=["GET", "POST"])
    def track_order():

     order = None

    if request.method == "POST":

        order_id = request.form["order_id"]

        connection = sqlite3.connect("orders.db")
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        )

        order = cursor.fetchone()

        connection.close()

    return render_template(
        "track_order.html",
        order=order
    )

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    cart = session.get("cart", {})

    for product in products:

        if product["id"] == product_id:

            product_key = str(product_id)

            if product_key in cart:

                cart[product_key]["quantity"] += 1

            else:

                cart[product_key] = {
                    "product": product,
                    "quantity": 1
                }

            break

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("home"))

@app.route("/buy_now/<int:product_id>")
def buy_now(product_id):

    cart = {}

    for product in products:

        if product["id"] == product_id:

            cart[str(product_id)] = {
                "product": product,
                "quantity": 1
            }

            break

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("checkout"))
# ========================================
# INCREASE QUANTITY
# ==================================================

@app.route("/increase/<int:product_id>")
def increase_quantity(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id]["quantity"] += 1

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("view_cart"))
# ==================================================
# CART PAGE
# ==================================================

@app.route("/cart")
def view_cart():

    cart = session.get("cart", {})

    cart_items = []
    total = 0
    cart_count = 0

    for product_id, item in cart.items():

        product = item["product"]
        quantity = item["quantity"]

        cart_item = product.copy()
        cart_item["quantity"] = quantity

        cart_items.append(cart_item)

        total += product["price"] * quantity
        cart_count += quantity

    return render_template(
        "cart.html",
        cart=cart_items,
        total=total,
        cart_count=cart_count
    )
# DECREASE QUANTITY
# ==================================================

# ==================================================
# DECREASE QUANTITY
# ==================================================

@app.route("/decrease/<int:product_id>")
def decrease_quantity(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        if cart[product_id]["quantity"] > 1:
            cart[product_id]["quantity"] -= 1

        else:
            del cart[product_id]

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("view_cart"))
# ==================================================
# REMOVE PRODUCT
# ================================================

@app.route("/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("view_cart"))


# ==================================================
# CHECKOUT
# ==================================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    total = 0

    for item in cart.values():
        total += (
            item["product"]["price"]
            * item["quantity"]
        )

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        address = request.form["address"]
        payment_method = request.form["payment_method"]

        product_names = ", ".join(
            item["product"]["name"]
            + " x "
            + str(item["quantity"])
            for item in cart.values()
        )

        connection = sqlite3.connect("orders.db")
        cursor = connection.cursor()

        cursor.execute("""
    INSERT INTO orders
    (name, phone, address, product, total, status, payment_method)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    name,
    phone,
    address,
    product_names,
    total,
    "Pending",
    payment_method
))

        order_id = cursor.lastrowid

        connection.commit()
        connection.close()

        cart.clear()
        session.pop("cart", None)

        return render_template(
            "success.html",
            name=name,
            total=total,
            order_id=order_id
        )

    return render_template(
        "checkout.html",
        total=total
    )
    @app.route("/track_order", methods=["GET", "POST"])
    def track_order():

     order = None

    if request.method == "POST":

        order_id = request.form["order_id"]

        connection = sqlite3.connect("orders.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        )

        order = cursor.fetchone()

        connection.close()

    return render_template(
        "track_order.html",
        order=order
    )
# ==================================================
# ADMIN LOGIN
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "Naved@786":

            session["admin"] = True

            return redirect(url_for("admin"))

        return "Invalid Username or Password"

    return render_template("login.html")


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route("/admin")
def admin():

    if not session.get("admin"):

        return redirect(url_for("login"))

    connection = sqlite3.connect("orders.db")

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM orders ORDER BY id DESC"
    )

    orders = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )

    total_orders = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(total), 0) FROM orders"
    )

    total_sales = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "admin.html",
        orders=orders,
        total_orders=total_orders,
        total_sales=total_sales
    )


# ==================================================
# UPDATE ORDER STATUS
# ==================================================

@app.route("/update_status/<int:order_id>/<status>")
def update_status(order_id, status):

    if not session.get("admin"):

        return redirect(url_for("login"))

    allowed_status = [
        "Pending",
        "Shipped",
        "Delivered"
    ]

    if status not in allowed_status:

        return redirect(url_for("admin"))

    connection = sqlite3.connect("orders.db")

    cursor = connection.cursor()

    cursor.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))


# ==================================================
# DELETE ORDER
# ==================================================

@app.route("/delete_order/<int:order_id>")
def delete_order(order_id):

    if not session.get("admin"):

        return redirect(url_for("login"))

    connection = sqlite3.connect("orders.db")

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM orders WHERE id = ?",
        (order_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(url_for("login"))
# ==================================================
# TRACK ORDER
# ==================================================

@app.route("/track_order", methods=["GET", "POST"])
def track_order():

    order = None

    if request.method == "POST":

        order_id = request.form["order_id"]

        connection = sqlite3.connect("orders.db")
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        )

        order = cursor.fetchone()

        connection.close()

    return render_template(
        "track_order.html",
        order=order
    )

# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(debug=True)