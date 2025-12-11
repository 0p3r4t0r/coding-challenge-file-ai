CREATE TABLE invoices (
    id TEXT PRIMARY KEY,
    purchase_order_id TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- No need for updated_at, as these records will never be updated.

    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders (id) ON DELETE CASCADE
)


CREATE TABLE invoice_lines (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_id TEXT,
    purchase_order_line_id TEXT,
    item_code TEXT, -- item codes may vary across different vendors.
    description TEXT,
    quantity INT,
    unit_price NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- The same item should not be listed on multiple lines in a given invoice.
    UNIQUE(invoice_id, item_code)

    FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
    FOREIGN KEY (purchase_order_line_id) REFERENCES purchase_order_lines (id) ON DELETE CASCADE
)

-- Add trigger for update_at
CREATE TRIGGER trg_purchase_order_lines_updated_at
BEFORE UPDATE ON invoice_lines
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();