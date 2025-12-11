CREATE TABLE purchase_orders (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- No need for updated_at, as these records will never be updated.
)


CREATE TABLE purchase_order_lines (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    purchase_order_id TEXT NOT NULL,
    purchase_order_line_number INT NOT NULL,
    item_code TEXT NOT NULL, -- item codes may vary across different vendors.
    description TEXT NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- No duplicate lines for a given purchase order.
    UNIQUE(purchase_order_id, purchase_order_line_number),
    -- The same item should not be listed on multiple lines in a given purchase order.
    UNIQUE(purchase_order_id, item_code),

    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders (id) ON DELETE CASCADE
)


-- Add trigger for update_at
CREATE TRIGGER trg_purchase_order_lines_updated_at
BEFORE UPDATE ON purchase_order_lines
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();