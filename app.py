from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "fashion_store_secret_key"


# ==================================================
# PRODUCTS
# ==================================================

products = [
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
        "name": "Women's Dress",
        "price": 999,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8"
    },
    {
        "id": 4,
        "name": "Women's Top",
        "price": 599,
        "category": "Women",
        "image": "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3"
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

    for product in products:

        if product["id"] == product_id:

            if product_id in cart:

                cart[product_id]["quantity"] += 1

            else:

                cart[product_id] = {
                    "product": product,
                    "quantity": 1
                }

            break

    return redirect(url_for("home"))
@app.route("/buy_now/<int:product_id>")
def buy_now(product_id):

    for product in products:
        if product["id"] == product_id:

            cart.clear()

            cart[product_id] = {
                "product": product,
                "quantity": 1
            }

            return redirect(url_for("checkout"))

    return "Product not found"


# ==================================================
# CART
# ==================================================

@app.route("/cart")
def view_cart():

    total = 0

    cart_count = 0

    for item in cart.values():

        total += (
            item["product"]["price"]
            * item["quantity"]
        )

        cart_count += item["quantity"]

    return render_template(
        "cart.html",
        cart=cart,
        total=total,
        cart_count=cart_count
    )


# ==================================================
# INCREASE QUANTITY
# ==================================================

@app.route("/increase/<int:product_id>")
def increase_quantity(product_id):

    if product_id in cart:

        cart[product_id]["quantity"] += 1

    return redirect(url_for("view_cart"))


# ==================================================
# DECREASE QUANTITY
# ==================================================

@app.route("/decrease/<int:product_id>")
def decrease_quantity(product_id):

    if product_id in cart:

        cart[product_id]["quantity"] -= 1

        if cart[product_id]["quantity"] <= 0:

            del cart[product_id]

    return redirect(url_for("view_cart"))


# ==================================================
# REMOVE PRODUCT
# ==================================================

@app.route("/remove/<int:product_id>")
def remove_product(product_id):

    if product_id in cart:

        del cart[product_id]

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