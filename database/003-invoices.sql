CREATE TABLE invoice (
    id TEXT PRIMARY KEY,
    purchase_order_id TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- No need for updated_at, as these records will never be updated.

    FOREIGN KEY (purchase_order_id) REFERENCES purchase_order (id) ON DELETE CASCADE
);


CREATE TABLE invoice_line_item (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_id TEXT,
    purchase_order_line_item_id INT,
    item_code TEXT, -- item codes may vary across different vendors.
    description TEXT,
    quantity INT,
    unit_price NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- The same item should not be listed on multiple lines in a given invoice.
    UNIQUE(invoice_id, item_code),

    FOREIGN KEY (invoice_id) REFERENCES invoice (id) ON DELETE CASCADE,
    FOREIGN KEY (purchase_order_line_item_id) REFERENCES purchase_order_line_item (id) ON DELETE CASCADE
);

-- Add trigger for update_at
CREATE TRIGGER trg_purchase_invoice_line_item_updated_at
BEFORE UPDATE ON invoice_line_item
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();