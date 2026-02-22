from flask import Flask, render_template, request, jsonify, session, url_for, flash, redirect
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'crmdb'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ---------------- AUTH ROUTES ---------------- #

@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

# ------------------ SIGNUP ------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, password))
        conn.commit()
        conn.close()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# ------------------ DASHBOARD ------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session["user_name"])

# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/products")
def products_page():
    return render_template("products.html")

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/customers')
def customers():
    return render_template('customers.html')

# === API ENDPOINTS ===

@app.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_customers FROM customers")
    total_customers = cursor.fetchone()['total_customers']

    cursor.execute("SELECT COUNT(*) AS total_products FROM products")
    total_products = cursor.fetchone()['total_products']

    cursor.execute("SELECT SUM(amount) AS revenue FROM sales")
    revenue = cursor.fetchone()['revenue'] or 0

    cursor.execute("SELECT name, sold FROM products ORDER BY sold DESC LIMIT 1")
    top_product_row = cursor.fetchone()
    top_product = top_product_row['name'] if top_product_row else 'N/A'
    top_product_sold = top_product_row['sold'] if top_product_row else 0

    conn.close()
    return jsonify({
        'total_customers': total_customers,
        'total_products': total_products,
        'ytd_revenue': revenue,
        'top_product': top_product,
        'top_product_sold': top_product_sold
    })
#DASHBOARD API ENDPOINTS
@app.route('/api/dashboard/sales-chart', methods=['GET'])
def get_sales_chart():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE_FORMAT(sale_date, '%b') AS month, SUM(amount) AS total
        FROM sales
        GROUP BY month
        ORDER BY STR_TO_DATE(month, '%b')
    """)
    data = cursor.fetchall()
    months = [row['month'] for row in data]
    totals = [float(row['total']) for row in data]
    conn.close()
    return jsonify({'months': months, 'totals': totals})

@app.route('/api/dashboard/product-chart', methods=['GET'])
def get_product_chart():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT category, COUNT(*) AS count FROM products GROUP BY category")
    data = cursor.fetchall()
    categories = [row['category'] for row in data]
    counts = [row['count'] for row in data]
    conn.close()
    return jsonify({'categories': categories, 'counts': counts})

@app.route('/api/dashboard/average-sale', methods=['GET'])
def average_sale():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT AVG(amount) AS average_sale FROM sales")
    result = cursor.fetchone()
    conn.close()
    return jsonify({'average_sale': result['average_sale']})

@app.route('/customer-demographics')
def customer_demographics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total number of customers
    cursor.execute("SELECT COUNT(*) AS total FROM customers")
    total = cursor.fetchone()['total']

    # Top 5 cities based on address (assuming address contains city names)
    cursor.execute("""
        SELECT address, COUNT(*) as count
        FROM customers
        GROUP BY address
        ORDER BY count DESC
        LIMIT 5;
    """)
    top_cities = cursor.fetchall()

    # Email domains
    cursor.execute("""
        SELECT 
            SUBSTRING_INDEX(email, '@', -1) AS domain,
            COUNT(*) as count
        FROM customers
        GROUP BY domain
        ORDER BY count DESC
        LIMIT 10;
    """)
    domains = cursor.fetchall()

    conn.close()

    return jsonify({
        "total_customers": total,
        "top_cities": top_cities,
        "email_domains": domains
    })




@app.route('/api/dashboard/top-customers', methods=['GET'])
def top_customers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                c.name AS customer_name,
                SUM(s.amount) AS total_spent,
                COUNT(*) AS total_orders
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            GROUP BY s.customer_id
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        print("Error in /api/dashboard/top-customers:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/repeat-customer-rate')    
def repeat_customer_rate():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) AS repeat_customers,
            COUNT(DISTINCT customer_id) AS total_customers
        FROM (
            SELECT customer_id, COUNT(*) AS order_count
            FROM sales
            GROUP BY customer_id
        ) AS sub;
    """)
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    repeat_rate = 0
    if result['total_customers'] > 0:
        repeat_rate = (result['repeat_customers'] / result['total_customers']) * 100

    return jsonify({
        "repeat_customer_rate": round(repeat_rate, 2),
        "repeat_customers": result['repeat_customers'],
        "total_customers": result['total_customers']
    })
    
@app.route('/api/dashboard/low-stock', methods=['GET'])
def low_stock_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT name, category, stock 
        FROM products 
        WHERE stock < 10 
        ORDER BY stock ASC
    """)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/api/dashboard/product-velocity')
def product_velocity():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.name AS product_name,
            SUM(s.quantity) AS total_sold
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY total_sold DESC
        LIMIT 10;
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)
 
@app.route('/sales_trend')
def sales_trend():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT sale_date, 
               SUM(amount) AS total_revenue,
               SUM(quantity) AS total_quantity
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

    
#SALES API ENDPOINTS
@app.route('/api/sales/customer-products')
def customer_product_sales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.name AS customer_name, c.email AS customer_email,
               p.name AS product_name, s.quantity, s.sale_date AS date
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN products p ON s.product_id = p.id
        ORDER BY s.sale_date DESC
        LIMIT 10;
    """)
    result = cursor.fetchall()
    conn.close()
    return jsonify(result)

@app.route('/api/sales/sales-details', methods=['GET'])
def get_sales_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            c.name AS customer_name,
            p.name AS product_name,
            s.quantity,
            s.amount AS total_price,
            s.sale_date AS date
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN products p ON s.product_id = p.id
        ORDER BY s.sale_date DESC
        ;
    """)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)



# CUSTOMERS API ENDPOINTS
@app.route("/api/customers", methods=["GET"])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(customers)

@app.route("/api/customers", methods=["POST"])
def add_customer():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Customer added successfully"}), 201

@app.route("/api/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Customer deleted successfully"}), 200



#PRODUCTS API POINTS
@app.route("/api/products", methods=["GET", "POST"])
def products_api():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "GET":
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)

    elif request.method == "POST":
        data = request.get_json()
        cursor.execute(
            "INSERT INTO products (name, category, price, sold) VALUES (%s, %s, %s, %s)",
            (data["name"], data["category"], data["price"], data["sold"])
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'deleted'}), 200

@app.route('/api/products/top-revenue', methods=['GET'])
def top_revenue_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.name AS product_name,
            SUM(s.amount) AS revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY s.product_id
        ORDER BY revenue DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

# MAIN ENTRY POINT 
if __name__ == '__main__':
    app.run(debug=True)
