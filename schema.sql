-- Create the database
CREATE DATABASE IF NOT EXISTS crmdb;
USE crmdb;

-- USERS table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- CUSTOMERS table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(255)
);

-- PRODUCTS table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    sold INT DEFAULT 0,
    stock INT DEFAULT 0
);

-- SALES table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    sale_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_product_category ON products(category);

-- --------------------------------------------
-- SAMPLE DATA
-- --------------------------------------------

-- Sample Users
INSERT INTO users (name, email, password)
VALUES 
('Admin User', 'admin@example.com', 'admin123'), 
('Test User', 'test@example.com', 'test123');

-- Sample Customers
INSERT INTO customers (name, email, phone, address)
VALUES 
('Alice Smith', 'alice@gmail.com', '1234567890', 'New York'),
('Bob Johnson', 'bob@yahoo.com', '0987654321', 'Los Angeles'),
('Charlie Brown', 'charlie@outlook.com', '1122334455', 'Chicago'),
('David Lee', 'david@company.com', '2233445566', 'Houston'),
('Eva Green', 'eva@gmail.com', '3344556677', 'Phoenix');

-- Sample Products
INSERT INTO products (name, category, price, sold, stock)
VALUES 
('iPhone 14', 'Electronics', 999.99, 50, 20),
('Galaxy S22', 'Electronics', 899.99, 35, 15),
('MacBook Pro', 'Computers', 1999.99, 20, 5),
('Dell XPS 13', 'Computers', 1299.99, 15, 8),
('Bluetooth Speaker', 'Accessories', 49.99, 80, 30),
('Wireless Mouse', 'Accessories', 19.99, 100, 50);

-- Sample Sales
INSERT INTO sales (customer_id, product_id, quantity, amount, sale_date)
VALUES 
(1, 1, 1, 999.99, '2025-09-01'),
(2, 2, 2, 1799.98, '2025-09-03'),
(3, 3, 1, 1999.99, '2025-09-05'),
(4, 5, 3, 149.97, '2025-09-10'),
(1, 6, 2, 39.98, '2025-09-12'),
(2, 1, 1, 999.99, '2025-09-15'),
(5, 4, 1, 1299.99, '2025-09-17'),
(3, 5, 2, 99.98, '2025-09-18'),
(4, 6, 5, 99.95, '2025-09-19'),
(5, 2, 1, 899.99, '2025-09-20');