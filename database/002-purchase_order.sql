CREATE TABLE purchase_order (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    -- No need for updated_at, as these records will never be updated.
);


CREATE TABLE purchase_order_line_item (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    purchase_order_id TEXT NOT NULL,
    purchase_order_line_number INT NOT NULL,
    item_code TEXT NOT NULL, -- item codes may vary across different vendors.
    description TEXT NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- No duplicate lines for a given purchase order.
    UNIQUE(purchase_order_id, purchase_order_line_number),
    -- The same item should not be listed on multiple lines in a given purchase order.
    UNIQUE(purchase_order_id, item_code),

    CONSTRAINT purchase_order_line_item_total_price_check
        CHECK (quantity * unit_price = total_price),

    FOREIGN KEY (purchase_order_id) REFERENCES purchase_order (id) ON DELETE CASCADE
);


-- Add trigger for update_at
CREATE TRIGGER trg_purchase_order_line_item_updated_at
BEFORE UPDATE ON purchase_order_line_item
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- Create indexes
CREATE INDEX idx_po_line_item_purchase_order_id
ON purchase_order_line_item(purchase_order_id);