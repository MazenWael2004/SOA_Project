USE ecommerce_system;
-- Sample products
INSERT INTO inventory (product_name, quantity_available, unit_price) VALUES
('Laptop', 50, 999.99),
('Mouse', 200, 29.99),
('Keyboard', 150, 79.99),
('Monitor', 75, 299.99),
('Headphones', 100, 149.99);
-- Sample customers
INSERT INTO customers (name, email, phone, loyalty_points) VALUES
('Ahmed Hassan', 'ahmed@example.com', '01012345678', 100),
('Sara Mohamed', 'sara@example.com', '01098765432', 250),
('Omar Ali', 'omar@example.com', '01055555555', 50);
-- Sample pricing rules
INSERT INTO pricing_rules (product_id, min_quantity, discount_percentage) VALUES
(1, 5, 10.00),
(2, 10, 15.00),
(3, 10, 12.00);