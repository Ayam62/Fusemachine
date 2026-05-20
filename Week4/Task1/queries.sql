
-- Q1: List all products
SELECT "productCode", "productName", "productLine", "buyPrice", "MSRP"
FROM products
ORDER BY "productLine", "productName";

-- Q2: Get all customers
SELECT "customerNumber", "customerName", "city", "country", "phone"
FROM customers
ORDER BY "country", "customerName";

-- Q3: Show all orders
SELECT "orderNumber", "orderDate", "status", "customerNumber"
FROM orders
ORDER BY "orderDate" DESC;

-- Q4: List all employees
SELECT "employeeNumber", "firstName", "lastName", "jobTitle", "email"
FROM employees
ORDER BY "jobTitle", "lastName";

-- Q5: Get all offices
SELECT "officeCode", "city", "country", "territory", "phone"
FROM offices
ORDER BY "territory", "city";

-- Q6: Show all product lines
SELECT "productLine", "textDescription"
FROM productlines
ORDER BY "productLine";

-- Q7: List all payments
SELECT "customerNumber", "checkNumber", "paymentDate", "amount"
FROM payments
ORDER BY "paymentDate" DESC;

-- Q8: Get product names and prices
SELECT "productName", "buyPrice", "MSRP"
FROM products
ORDER BY "MSRP" DESC;

-- Q9: Get customer names and cities
SELECT "customerName", "city", "country"
FROM customers
ORDER BY "country", "city";

-- Q10: List employee first and last names
SELECT "firstName", "lastName", "jobTitle"
FROM employees
ORDER BY "lastName", "firstName";

-- Q11: Get all order dates
SELECT DISTINCT "orderDate"
FROM orders
ORDER BY "orderDate";

-- Q12: Show product vendor list
SELECT DISTINCT "productVendor"
FROM products
ORDER BY "productVendor";

-- Q13: Get all product codes
SELECT "productCode", "productName"
FROM products
ORDER BY "productCode";

-- Q14: List all countries from offices
SELECT DISTINCT "country", "city", "territory"
FROM offices
ORDER BY "country";

-- Q15: Show all order statuses
SELECT DISTINCT "status"
FROM orders
ORDER BY "status";

-- Q16: Get all payment amounts
SELECT "customerNumber", "checkNumber", "paymentDate", "amount"
FROM payments
ORDER BY "amount" DESC;

-- Q17: List all job titles
SELECT DISTINCT "jobTitle"
FROM employees
ORDER BY "jobTitle";

-- Q18: Get customer phone numbers
SELECT "customerName", "phone", "country"
FROM customers
ORDER BY "customerName";

-- Q19: Show product MSRP values
SELECT "productName", "MSRP", "buyPrice",
       ROUND("MSRP" - "buyPrice", 2) AS margin
FROM products
ORDER BY "MSRP" DESC;

-- Q20: List order numbers
SELECT "orderNumber", "orderDate", "status"
FROM orders
ORDER BY "orderNumber";


-- ============================================================
-- SECTION B: JOIN QUERIES (Q21 - Q30)
-- ============================================================

-- Q21: Get orders with customer names
SELECT o."orderNumber", o."orderDate", o."status",
       c."customerName", c."country"
FROM orders o
JOIN customers c ON o."customerNumber" = c."customerNumber"
ORDER BY o."orderDate" DESC;

-- Q22: Get employees with office city
SELECT e."firstName", e."lastName", e."jobTitle",
       o."city", o."country"
FROM employees e
JOIN offices o ON e."officeCode" = o."officeCode"
ORDER BY o."country", e."lastName";

-- Q23: Get payments with customer names
SELECT p."checkNumber", p."paymentDate", p."amount",
       c."customerName", c."country"
FROM payments p
JOIN customers c ON p."customerNumber" = c."customerNumber"
ORDER BY p."paymentDate" DESC;

-- Q24: Get order details with product names
SELECT od."orderNumber", p."productName", od."quantityOrdered",
       od."priceEach",
       ROUND(od."quantityOrdered" * od."priceEach", 2) AS line_total
FROM orderdetails od
JOIN products p ON od."productCode" = p."productCode"
ORDER BY od."orderNumber", line_total DESC;

-- Q25: Get products with product line description
SELECT p."productName", p."productLine",
       pl."textDescription"
FROM products p
JOIN productlines pl ON p."productLine" = pl."productLine"
ORDER BY p."productLine", p."productName";

-- Q26: Get customers with sales rep names
SELECT c."customerName", c."country",
       e."firstName" || ' ' || e."lastName" AS sales_rep
FROM customers c
LEFT JOIN employees e ON c."salesRepEmployeeNumber" = e."employeeNumber"
ORDER BY c."country", c."customerName";

-- Q27: Get orders with customer city
SELECT o."orderNumber", o."orderDate", o."status",
       c."customerName", c."city", c."country"
FROM orders o
JOIN customers c ON o."customerNumber" = c."customerNumber"
ORDER BY c."country", c."city";

-- Q28: Get employees and their manager
SELECT e."firstName" || ' ' || e."lastName" AS employee,
       e."jobTitle",
       m."firstName" || ' ' || m."lastName" AS manager,
       m."jobTitle" AS manager_title
FROM employees e
LEFT JOIN employees m ON e."reportsTo" = m."employeeNumber"
ORDER BY m."lastName" NULLS FIRST, e."lastName";

-- Q29: Get orderdetails with product vendor
SELECT od."orderNumber", p."productName",
       p."productVendor", od."quantityOrdered", od."priceEach"
FROM orderdetails od
JOIN products p ON od."productCode" = p."productCode"
ORDER BY p."productVendor", od."orderNumber";

-- Q30: Get payments with customer country
SELECT p."checkNumber", p."paymentDate", p."amount",
       c."customerName", c."country"
FROM payments p
JOIN customers c ON p."customerNumber" = c."customerNumber"
ORDER BY c."country", p."amount" DESC;


-- ============================================================
-- SECTION C: AGGREGATION QUERIES (Q31 - Q50)
-- ============================================================

-- Q31: Count customers per country
SELECT "country",
       COUNT(*) AS customer_count
FROM customers
GROUP BY "country"
ORDER BY customer_count DESC;

-- Q32: Total payments per customer
SELECT c."customerName",
       COUNT(p."checkNumber") AS payment_count,
       SUM(p."amount") AS total_paid
FROM customers c
JOIN payments p ON c."customerNumber" = p."customerNumber"
GROUP BY c."customerNumber", c."customerName"
ORDER BY total_paid DESC;

-- Q33: Number of orders per status
SELECT "status",
       COUNT(*) AS order_count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM orders
GROUP BY "status"
ORDER BY order_count DESC;

-- Q34: Products per product line
SELECT "productLine",
       COUNT(*) AS product_count
FROM products
GROUP BY "productLine"
ORDER BY product_count DESC;

-- Q35: Employees per office
SELECT o."city", o."country",
       COUNT(e."employeeNumber") AS employee_count
FROM offices o
LEFT JOIN employees e ON o."officeCode" = e."officeCode"
GROUP BY o."officeCode", o."city", o."country"
ORDER BY employee_count DESC;

-- Q36: Total stock per product vendor
SELECT "productVendor",
       COUNT(*) AS product_count,
       SUM("quantityInStock") AS total_stock
FROM products
GROUP BY "productVendor"
ORDER BY total_stock DESC;

-- Q37: Average buy price per product line
SELECT "productLine",
       ROUND(AVG("buyPrice"), 2) AS avg_buy_price,
       ROUND(AVG("MSRP"), 2) AS avg_msrp
FROM products
GROUP BY "productLine"
ORDER BY avg_msrp DESC;

-- Q38: Orders per customer
SELECT c."customerName", c."country",
       COUNT(o."orderNumber") AS order_count
FROM customers c
LEFT JOIN orders o ON c."customerNumber" = o."customerNumber"
GROUP BY c."customerNumber", c."customerName", c."country"
ORDER BY order_count DESC;

-- Q39: Max MSRP per product line
SELECT "productLine",
       MAX("MSRP") AS max_msrp,
       MIN("MSRP") AS min_msrp,
       MAX("MSRP") - MIN("MSRP") AS price_range
FROM products
GROUP BY "productLine"
ORDER BY max_msrp DESC;

-- Q40: Min buy price per vendor
SELECT "productVendor",
       MIN("buyPrice") AS min_buy_price,
       MAX("buyPrice") AS max_buy_price,
       COUNT(*) AS total_products
FROM products
GROUP BY "productVendor"
ORDER BY min_buy_price ASC;

-- Q41: Total number of customers
SELECT COUNT(*) AS total_customers
FROM customers;

-- Q42: Total number of products
SELECT COUNT(*) AS total_products,
       COUNT(DISTINCT "productLine") AS product_lines
FROM products;

-- Q43: Total revenue from payments
SELECT COUNT(*) AS total_payments,
       SUM("amount") AS total_revenue,
       ROUND(AVG("amount"), 2) AS avg_payment
FROM payments;

-- Q44: Average product price
SELECT ROUND(AVG("buyPrice"), 2) AS avg_buy_price,
       ROUND(AVG("MSRP"), 2) AS avg_msrp,
       ROUND(AVG("MSRP" - "buyPrice"), 2) AS avg_margin
FROM products;

-- Q45: Max payment amount
SELECT MAX("amount") AS max_payment,
       MIN("amount") AS min_payment
FROM payments;

-- Q46: Min payment amount
SELECT MIN("amount") AS min_payment,
       MAX("amount") AS max_payment,
       MAX("amount") - MIN("amount") AS payment_range
FROM payments;

-- Q47: Count total orders
SELECT COUNT(*) AS total_orders,
       COUNT(DISTINCT "customerNumber") AS ordering_customers,
       COUNT(DISTINCT "status") AS distinct_statuses
FROM orders;

-- Q48: Total quantity in stock
SELECT SUM("quantityInStock") AS total_stock,
       ROUND(AVG("quantityInStock"), 0) AS avg_stock_per_product,
       MIN("quantityInStock") AS min_stock,
       MAX("quantityInStock") AS max_stock
FROM products;

-- Q49: Average MSRP
SELECT ROUND(AVG("MSRP"), 2) AS avg_msrp,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "MSRP"), 2) AS median_msrp
FROM products;

-- Q50: Number of employees
SELECT COUNT(*) AS total_employees,
       COUNT(DISTINCT "jobTitle") AS distinct_roles,
       COUNT(DISTINCT "officeCode") AS offices_staffed
FROM employees;